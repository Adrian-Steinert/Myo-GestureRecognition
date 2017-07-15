import os
import re
import csv
import sys
import math
import time
import pickle

from glob import glob
from datetime import datetime
from collections import Counter
from scipy.interpolate import interp1d

import threading
from multiprocessing import Pool

rawPath = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'raw')
convertedPath = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'converted')

gesture_dict_lock = threading.Lock()
interpolated_dict_lock = threading.Lock()


def acquire_acc_or_gyro(path_to_acc_or_gyro_file, gesture_dict, is_acc=True):
    data_dict = {'timestamps': [], 'x': [], 'y': [], 'z': []}

    with open(path_to_acc_or_gyro_file, newline='') as acc_or_gyro_csv:
        acc_or_gyro_csv.readline()   # skip the first line
        reader = csv.reader(acc_or_gyro_csv, delimiter=',')
        for row in reader:
            # print(row)
            data_dict['timestamps'].append(int(row[0]))
            data_dict['x'].append(float(row[1]))
            data_dict['y'].append(float(row[2]))
            data_dict['z'].append(float(row[3]))
    # with gesture_dict_lock:
    if is_acc:
        gesture_dict['accelerometer'] = data_dict
    else:
        gesture_dict['gyro'] = data_dict
    # return data_dict


def acquire_emg(path_to_emg_file, gesture_dict):
    emg_dict = {'timestamps': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': []}

    with open(path_to_emg_file, newline='') as emg_csv:
        emg_csv.readline()  # skip the first line
        reader = csv.reader(emg_csv, delimiter=',')
        for row in reader:
            # print(row)
            emg_dict['timestamps'].append(int(row[0]))
            emg_dict['1'].append(int(row[1]))
            emg_dict['2'].append(int(row[2]))
            emg_dict['3'].append(int(row[3]))
            emg_dict['4'].append(int(row[4]))
            emg_dict['5'].append(int(row[5]))
            emg_dict['6'].append(int(row[6]))
            emg_dict['7'].append(int(row[7]))
            emg_dict['8'].append(int(row[8]))

    # with gesture_dict_lock:
    gesture_dict['emg'] = emg_dict
    # return emg_dict


def acquire_orientation(path_to_orientation_file, gesture_dict):
    ori_dict = {'timestamps': [], 'x': [], 'y': [], 'z': [], 'w': []}
    with open(path_to_orientation_file, newline='') as ori_csv:
        ori_csv.readline()  # skip the first line
        reader = csv.reader(ori_csv, delimiter=',')
        for row in reader:
            # print(row)
            ori_dict['timestamps'].append(int(row[0]))
            ori_dict['x'].append(float(row[1]))
            ori_dict['y'].append(float(row[2]))
            ori_dict['z'].append(float(row[3]))
            ori_dict['w'].append(float(row[4]))

    # with gesture_dict_lock:
    gesture_dict['orientation'] = ori_dict
    # return ori_dict


def acquire_orientation_euler(path_to_orientationEuler_file, gesture_dict):
    ori_euler_dict = {'timestamps': [], 'roll': [], 'pitch': [], 'yaw': []}

    with open(path_to_orientationEuler_file, newline='') as ori_euler_csv:
        ori_euler_csv.readline()  # skip the first line
        reader = csv.reader(ori_euler_csv, delimiter=',')
        for row in reader:
            # print(row)
            ori_euler_dict['timestamps'].append(int(row[0]))
            ori_euler_dict['pitch'].append(float(row[1]))
            ori_euler_dict['roll'].append(float(row[2]))
            ori_euler_dict['yaw'].append(float(row[3]))

    # with gesture_dict_lock:
    gesture_dict['orientationEuler'] = ori_euler_dict


def acquire_data(user, gesture, gesture_dict):
    recordedData = glob(os.path.join(rawPath, user, gesture) + '\*')

    # sort by last modified date
    recordedData = sorted(recordedData, key=os.path.getmtime)

    # split in chunks of five, because a single gesture consists of the following csv files
    # accelerometer, emg, gyro, orientation and orientationEuler
    # sort by name, so that acquire functions are called in the right order
    recordedData = [sorted(recordedData[x:x + 5]) for x in range(0, len(recordedData), 5)]

    for gesture_chunk in recordedData:
        gesture_dict['gesture'] = gesture
        gesture_dict['datetime'] = datetime.fromtimestamp(os.path.getctime(gesture_chunk[0]))
        gesture_dict['performed_by'] = user

        acquire_acc_or_gyro(gesture_chunk[0], gesture_dict, is_acc=True)
        acquire_emg(gesture_chunk[1], gesture_dict)
        acquire_acc_or_gyro(gesture_chunk[2], gesture_dict, is_acc=False)
        acquire_orientation_euler(gesture_chunk[3], gesture_dict)
        acquire_orientation(gesture_chunk[4], gesture_dict)

        # t_acc = threading.Thread(target=acquire_acc_or_gyro, args=(gesture_chunk[0], gesture_dict, True), daemon=True)
        # t_acc.start()
        # t_emg = threading.Thread(target=acquire_emg, args=(gesture_chunk[1], gesture_dict), daemon=True)
        # t_emg.start()
        # t_gyro = threading.Thread(target=acquire_acc_or_gyro, args=(gesture_chunk[2], gesture_dict, False), daemon=True)
        # t_gyro.start()
        # t_oriEuler = threading.Thread(target=acquire_orientation_euler, args=(gesture_chunk[3], gesture_dict), daemon=True)
        # t_oriEuler.start()
        # t_ori = threading.Thread(target=acquire_orientation, args=(gesture_chunk[4], gesture_dict), daemon=True)
        # t_ori.start()

        # t_acc.join()
        # t_emg.join()
        # t_gyro.join()
        # t_oriEuler.join()
        # t_ori.join()

        start, end = find_gesture_start_end(gesture_dict)
        # interpolated_dict = interpolate_data(start, end, 1_000, gesture_dict) # interpolated values every millisecond


        # save dictionary as pickle to disk
        savePath = os.path.join(convertedPath, user, gesture)
        os.makedirs(savePath, exist_ok=True)
        # extract timestamp from csv file name
        timestamp = re.sub(r'.*\\[a-z_]+', '', gesture_chunk[0]).strip('.csv')
        pickle.dump(gesture_dict, open(os.path.join(savePath, gesture + timestamp) + '.p', 'wb'))


def eliminate_duplicates(list_with_duplicates):
    cleaned_list = []

    duplicate_counter = Counter(list_with_duplicates)

    for element, count in duplicate_counter.items():
        if count < 2:
            cleaned_list.append(element)
        else:
            for increment_by_one in range(count):
                cleaned_list.append(element + increment_by_one)

    return sorted(cleaned_list)


# timestep_size is an integer with unit microseconds
def interpolate_data(start, end, timestep_size, gesture_dict):
    # prepare interpolated dict
    interpolated_dict = {}
    interpolated_dict['gesture'] = gesture_dict['gesture']
    interpolated_dict['datetime'] = gesture_dict['datetime']
    interpolated_dict['performed_by'] = gesture_dict['performed_by']
    interpolated_dict['timestamps'] = list(range(start, end + 1, timestep_size)) # end shall be included thus + 1

    # get references to internal dicts
    acc_dict = gesture_dict['accelerometer']
    emg_dict = gesture_dict['emg']
    gyro_dict = gesture_dict['gyro']
    ori_dict = gesture_dict['orientation']
    ori_euler_dict = gesture_dict['orientationEuler']

    # interpolate and add results
    interpolated_dict['accelerometer'] = interpolate_acc_or_gyro_or_oriEuler(interpolated_dict['timestamps'], acc_dict)
    interpolated_dict['emg'] = interpolate_emg(interpolated_dict['timestamps'], emg_dict)
    interpolated_dict['gyro'] = interpolate_acc_or_gyro_or_oriEuler(interpolated_dict['timestamps'], gyro_dict)
    interpolated_dict['orientation'] = interpolate_orientation(interpolated_dict['timestamps'], ori_dict)
    interpolated_dict['orientationEuler'] = interpolate_acc_or_gyro_or_oriEuler(interpolated_dict['timestamps'],
                                                                          ori_euler_dict, is_oriEuler=True)

    return interpolated_dict


def interpolate_acc_or_gyro_or_oriEuler(timestamp_list, a_g_oE_dict, is_oriEuler=False):
    a_g_oE_dict['timestamps'] = eliminate_duplicates(a_g_oE_dict['timestamps'])

    if is_oriEuler:
        result_dict = {'roll': [], 'pitch': [], 'yaw': []}

        roll_interpolate = interp1d(a_g_oE_dict['timestamps'], a_g_oE_dict['roll'], kind='cubic', fill_value='extrapolate')
        pitch_interpolate = interp1d(a_g_oE_dict['timestamps'], a_g_oE_dict['pitch'], kind='cubic', fill_value='extrapolate')
        yaw_interpolate = interp1d(a_g_oE_dict['timestamps'], a_g_oE_dict['yaw'], kind='cubic', fill_value='extrapolate')

        [result_dict['roll'].append(roll_interpolate(timestamp)) for timestamp in timestamp_list]
        [result_dict['pitch'].append(pitch_interpolate(timestamp)) for timestamp in timestamp_list]
        [result_dict['yaw'].append(yaw_interpolate(timestamp)) for timestamp in timestamp_list]

    else:
        result_dict = {'x': [], 'y': [], 'z': []}
        ao_x_interpolate = interp1d(a_g_oE_dict['timestamps'], a_g_oE_dict['x'], kind='cubic', fill_value='extrapolate')
        ao_y_interpolate = interp1d(a_g_oE_dict['timestamps'], a_g_oE_dict['y'], kind='cubic', fill_value='extrapolate')
        ao_z_interpolate = interp1d(a_g_oE_dict['timestamps'], a_g_oE_dict['z'], kind='cubic', fill_value='extrapolate')

        [result_dict['x'].append(ao_x_interpolate(timestamp)) for timestamp in timestamp_list]
        [result_dict['y'].append(ao_y_interpolate(timestamp)) for timestamp in timestamp_list]
        [result_dict['z'].append(ao_z_interpolate(timestamp)) for timestamp in timestamp_list]

    return result_dict


def interpolate_emg(timestamp_list, emg_dict):
    result_dict = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': []}

    emg_dict['timestamps'] = eliminate_duplicates(emg_dict['timestamps'])

    emg1_interpolate = interp1d(emg_dict['timestamps'], emg_dict['1'], kind='cubic', fill_value='extrapolate')
    emg2_interpolate = interp1d(emg_dict['timestamps'], emg_dict['2'], kind='cubic', fill_value='extrapolate')
    emg3_interpolate = interp1d(emg_dict['timestamps'], emg_dict['3'], kind='cubic', fill_value='extrapolate')
    emg4_interpolate = interp1d(emg_dict['timestamps'], emg_dict['4'], kind='cubic', fill_value='extrapolate')
    emg5_interpolate = interp1d(emg_dict['timestamps'], emg_dict['5'], kind='cubic', fill_value='extrapolate')
    emg6_interpolate = interp1d(emg_dict['timestamps'], emg_dict['6'], kind='cubic', fill_value='extrapolate')
    emg7_interpolate = interp1d(emg_dict['timestamps'], emg_dict['7'], kind='cubic', fill_value='extrapolate')
    emg8_interpolate = interp1d(emg_dict['timestamps'], emg_dict['8'], kind='cubic', fill_value='extrapolate')

    [result_dict['1'].append(emg1_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['2'].append(emg2_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['3'].append(emg3_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['4'].append(emg4_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['5'].append(emg5_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['6'].append(emg6_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['7'].append(emg7_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['8'].append(emg8_interpolate(timestamp)) for timestamp in timestamp_list]

    return result_dict


def interpolate_orientation(timestamp_list, ori_dict):
    result_dict = {'x': [], 'y': [], 'z': [], 'w': []}

    ori_dict['timestamps'] = eliminate_duplicates(ori_dict['timestamps'])

    ori_x_interpolate = interp1d(ori_dict['timestamps'], ori_dict['x'], kind='cubic', fill_value='extrapolate')
    ori_y_interpolate = interp1d(ori_dict['timestamps'], ori_dict['y'], kind='cubic', fill_value='extrapolate')
    ori_z_interpolate = interp1d(ori_dict['timestamps'], ori_dict['z'], kind='cubic', fill_value='extrapolate')
    ori_w_interpolate = interp1d(ori_dict['timestamps'], ori_dict['w'], kind='cubic', fill_value='extrapolate')

    [result_dict['x'].append(ori_x_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['y'].append(ori_y_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['z'].append(ori_z_interpolate(timestamp)) for timestamp in timestamp_list]
    [result_dict['w'].append(ori_w_interpolate(timestamp)) for timestamp in timestamp_list]

    return result_dict


def find_gesture_start_end(gesture_dict):
    CONVERT_MILLI_MICRO = 1_000

    acc_timestamp_start = gesture_dict['accelerometer']['timestamps'][0]
    acc_timestamp_end = gesture_dict['accelerometer']['timestamps'][-1]
    emg_timestamp_start = gesture_dict['emg']['timestamps'][0]
    emg_timestamp_end = gesture_dict['emg']['timestamps'][-1]
    gyro_timestamp_start = gesture_dict['gyro']['timestamps'][0]
    gyro_timestamp_end = gesture_dict['gyro']['timestamps'][-1]
    ori_timestamp_start = gesture_dict['orientation']['timestamps'][0]
    ori_timestamp_end = gesture_dict['orientation']['timestamps'][-1]

    sorted_list = sorted([acc_timestamp_start, acc_timestamp_end, emg_timestamp_start, emg_timestamp_end,
                         gyro_timestamp_start, gyro_timestamp_end, ori_timestamp_start, ori_timestamp_end])

    start = math.floor(sorted_list[0] / CONVERT_MILLI_MICRO) * CONVERT_MILLI_MICRO
    end = math.ceil(sorted_list[-1] / CONVERT_MILLI_MICRO) * CONVERT_MILLI_MICRO

    # start and end are returned in microseconds
    return start, end


def main():
    rawUserPath = glob(rawPath + '\*')
    rawUsers = [re.sub(r'.*\\', '', user) for user in rawUserPath]
    # rawUsers = ['flo']
    # print(rawUsers)

    thread_list = []

    for user in rawUsers:
        rawGesturePath = glob(os.path.join(rawPath, user) + '\*')
        rawGestures = [re.sub(r'.*\\', '', gesture) for gesture in rawGesturePath]
        # rawGestures = ['big_stop']
        # print(rawGestures)

        convertedGesturePath = glob(os.path.join(convertedPath, user) + '\*')
        convertedGestures = [re.sub(r'.*\\', '', gesture) for gesture in convertedGesturePath]
        # print(convertedGestures)

        # remove any existing gestures from rawGesture list, so only new ones will be converted
        [rawGestures.remove(gesture) if gesture in rawGestures else '' for gesture in convertedGestures]
        # print(rawGestures)

        if len(rawGestures) == 0:
            print('Converted gestures are up-to-date.')
            break

        print('Converting gestures for {}... '.format(user), end='\n', flush=True)

        for gesture in rawGestures:
            gesture_dict = {}
            # print('Creating pickles {}/{}... '.format(user, gesture), end='', flush=True)
            # acquire_data(user, gesture, gesture_dict)
            # print('DONE')

            t = threading.Thread(target=acquire_data, args=(user, gesture, gesture_dict), daemon=True)
            thread_list.append(t)
            t.start()
        # print('DONE')

    for thread in thread_list:
        thread.join()


if __name__ == '__main__':
    starttime = time.time()
    main()
    print('CSVconverter: {}'.format(time.time()-starttime))
