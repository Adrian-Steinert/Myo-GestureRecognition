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
from multiprocessing import Pool, Process

rawPath = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'raw')
convertedPath = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'converted')

TIME_STEP_SIZE = 1_000 # in units of microseconds; 1_000 => create value every millisecond

# gesture_dict_lock = threading.Lock()
# interpolated_dict_lock = threading.Lock()


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
    print('Creating pickle {}/{}... '.format(user, gesture), flush=True)
    recordedData = glob(os.path.join(rawPath, user, gesture) + '\*')

    # sort by last modified date
    recordedData = sorted(recordedData, key=os.path.getmtime)

    # split in chunks of five, because a single gesture consists of the following csv files
    # accelerometer, emg, gyro, orientation and orientationEuler
    # sort by name, so that acquire functions are called in the right order
    recordedData = [sorted(recordedData[x:x + 5]) for x in range(0, len(recordedData), 5)]

    acquire_parameterlist = []

    for gesture_chunk in recordedData:
        gesture_dict['gesture'] = gesture
        gesture_dict['datetime'] = datetime.fromtimestamp(os.path.getctime(gesture_chunk[0]))
        gesture_dict['performed_by'] = user

        # start = time.time()
        # acquire_acc_or_gyro(gesture_chunk[0], gesture_dict, is_acc=True)
        # print('Acquire acc:      {}'.format(time.time()-start))
        # start = time.time()
        # acquire_emg(gesture_chunk[1], gesture_dict)
        # print('Acquire emg:      {}'.format(time.time() - start))
        # start = time.time()
        # acquire_acc_or_gyro(gesture_chunk[2], gesture_dict, is_acc=False)
        # print('Acquire gyro:     {}'.format(time.time() - start))
        # start = time.time()
        # acquire_orientation_euler(gesture_chunk[3], gesture_dict)
        # print('Acquire oriEuler: {}'.format(time.time() - start))
        # start = time.time()
        # acquire_orientation(gesture_chunk[4], gesture_dict)
        # print('Acquire ori:      {}'.format(time.time() - start))

        t_acc = threading.Thread(target=acquire_acc_or_gyro, args=(gesture_chunk[0], gesture_dict, True), daemon=True)
        t_acc.start()
        t_emg = threading.Thread(target=acquire_emg, args=(gesture_chunk[1], gesture_dict), daemon=True)
        t_emg.start()
        t_gyro = threading.Thread(target=acquire_acc_or_gyro, args=(gesture_chunk[2], gesture_dict, False), daemon=True)
        t_gyro.start()
        t_oriEuler = threading.Thread(target=acquire_orientation_euler, args=(gesture_chunk[3], gesture_dict), daemon=True)
        t_oriEuler.start()
        t_ori = threading.Thread(target=acquire_orientation, args=(gesture_chunk[4], gesture_dict), daemon=True)
        t_ori.start()

        t_acc.join()
        t_emg.join()
        t_gyro.join()
        t_oriEuler.join()
        t_ori.join()
        # print('Acquire data: {}'.format(time.time() - start))


        # start = time.time()
        interpolated_dict = {}
        # acquire_parameterlist.append((gesture_chunk[0], gesture_dict, interpolated_dict, TIME_STEP_SIZE))
        # interpolated_dict = interpolate_data(gesture_start, gesture_end, TIME_STEP_SIZE, gesture_dict, interpolated_dict)
        interpolate_and_save(gesture_chunk[0], gesture_dict, interpolated_dict, TIME_STEP_SIZE)
        # print('Interpolate:  {}'.format(time.time() - start))

    # return acquire_parameterlist
    # return (gesture_chunk[0], gesture_dict, interpolated_dict, TIME_STEP_SIZE)

def interpolate_and_save(filename_for_timestamp, gesture_dict, interpolated_dict, TIME_STEP_SIZE):
    interpolate_data(gesture_dict, interpolated_dict, TIME_STEP_SIZE)

    # with Pool() as p:
    # p = Process(interpolate_data, [(gesture_dict, interpolated_dict, TIME_STEP_SIZE)], daemon=True)
    # p.start()
    # p.join()

    # save dictionary as pickle to disk
    savePath = os.path.join(convertedPath, interpolated_dict['performed_by'], interpolated_dict['gesture'])
    # os.makedirs(savePath, exist_ok=True)
    # extract timestamp from csv file name
    timestamp = re.sub(r'.*\\[a-z_]+', '', filename_for_timestamp).strip('.csv')
    # pickle.dump(interpolated_dict, open(os.path.join(savePath, interpolated_dict['gesture'] + timestamp) + '.p', 'wb'))
    # print(interpolated_dict)
    return interpolated_dict


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
#
# interpolation from scipy.interpolate.interp1d return numpy ndarrays with a single element, i cast this to float before
# appending to a list
def interpolate_data(gesture_dict, interpolated_dict, timestep_size):
    # start = time.time()
    gesture_start, gesture_end = find_gesture_start_end(gesture_dict)
    # print('Find start/end:   {}'.format(time.time() - start))
    # print('-'*20)
    # prepare interpolated dict
    interpolated_dict['gesture'] = gesture_dict['gesture']
    interpolated_dict['datetime'] = gesture_dict['datetime']
    interpolated_dict['performed_by'] = gesture_dict['performed_by']
    interpolated_dict['timestamps'] = list(range(gesture_start, gesture_end + 1, timestep_size)) # end shall be included thus + 1

    # get references to internal dicts
    acc_dict = gesture_dict['accelerometer']
    emg_dict = gesture_dict['emg']
    gyro_dict = gesture_dict['gyro']
    ori_dict = gesture_dict['orientation']
    ori_euler_dict = gesture_dict['orientationEuler']


    # interpolate and add results
    start = time.time()
    interpolate_acc_or_gyro(interpolated_dict['timestamps'], acc_dict, interpolated_dict, is_acc=True)
    print('Interpolate acc:      {}'.format(time.time() - start))
    start = time.time()
    interpolate_emg(interpolated_dict['timestamps'], emg_dict, interpolated_dict)
    print('Interpolate emg:      {}'.format(time.time() - start))
    start = time.time()
    interpolate_acc_or_gyro(interpolated_dict['timestamps'], gyro_dict, interpolated_dict, is_acc=False)
    print('Interpolate gyro:     {}'.format(time.time() - start))
    start = time.time()
    interpolate_orientation(interpolated_dict['timestamps'], ori_dict, interpolated_dict)
    print('Interpolate ori:      {}'.format(time.time() - start))
    start = time.time()
    interpolate_orientationEuler(interpolated_dict['timestamps'], ori_euler_dict, interpolated_dict)
    print('Interpolate oriEuler: {}'.format(time.time() - start))

    print('-'*20)

    # t_interpolate_acc = threading.Thread(target=interpolate_acc_or_gyro,
    #                             args=(interpolated_dict['timestamps'], acc_dict, interpolated_dict, True), daemon=True)
    # t_interpolate_acc.start()
    # t_interpolate_emg = threading.Thread(target=interpolate_emg,
    #                             args=(interpolated_dict['timestamps'], emg_dict, interpolated_dict), daemon=True)
    # t_interpolate_emg.start()
    # t_interpolate_gyro = threading.Thread(target=interpolate_acc_or_gyro,
    #                             args=(interpolated_dict['timestamps'], gyro_dict, interpolated_dict, False), daemon=True)
    # t_interpolate_gyro.start()
    # t_interpolate_ori = threading.Thread(target=interpolate_orientation,
    #                             args=(interpolated_dict['timestamps'], ori_dict, interpolated_dict), daemon=True)
    # t_interpolate_ori.start()
    # t_interpolate_oriEuler = threading.Thread(target=interpolate_orientationEuler,
    #                             args=(interpolated_dict['timestamps'], ori_euler_dict, interpolated_dict), daemon=True)
    # t_interpolate_oriEuler.start()

    # t_interpolate_acc.join()
    # t_interpolate_emg.join()
    # t_interpolate_gyro.join()
    # t_interpolate_ori.join()
    # t_interpolate_oriEuler.join()


    # p_interpolate_acc = Process(target=interpolate_acc_or_gyro,
    #                             args=(interpolated_dict['timestamps'], acc_dict, interpolated_dict, True), daemon=True)
    # p_interpolate_acc.start()
    # p_interpolate_emg = Process(target=interpolate_emg,
    #                             args=(interpolated_dict['timestamps'], emg_dict, interpolated_dict), daemon=True)
    # p_interpolate_emg.start()
    # p_interpolate_gyro = Process(target=interpolate_acc_or_gyro,
    #                             args=(interpolated_dict['timestamps'], gyro_dict, interpolated_dict, False), daemon=True)
    # p_interpolate_gyro.start()
    # p_interpolate_ori = Process(target=interpolate_orientation,
    #                             args=(interpolated_dict['timestamps'], ori_dict, interpolated_dict), daemon=True)
    # p_interpolate_ori.start()
    # p_interpolate_oriEuler = Process(target=interpolate_orientationEuler,
    #                             args=(interpolated_dict['timestamps'], ori_euler_dict, interpolated_dict), daemon=True)
    # p_interpolate_oriEuler.start()

    # p_interpolate_acc.join()
    # p_interpolate_emg.join()
    # p_interpolate_gyro.join()
    # p_interpolate_ori.join()
    # p_interpolate_oriEuler.join()


    # return interpolated_dict


def fill_interpolation(result_dict, key_string, function, timestamp_list):
    result_dict[key_string] = [(float(function(timestamp))) for timestamp in timestamp_list]


def interpolate_acc_or_gyro(timestamp_list, acc_or_gyro_dict, interpolated_dict, is_acc=True):
    acc_or_gyro_dict['timestamps'] = eliminate_duplicates(acc_or_gyro_dict['timestamps'])

    result_dict = {'x': [], 'y': [], 'z': []}
    ag_x_interpolate = interp1d(acc_or_gyro_dict['timestamps'], acc_or_gyro_dict['x'], kind='cubic', fill_value='extrapolate')
    ag_y_interpolate = interp1d(acc_or_gyro_dict['timestamps'], acc_or_gyro_dict['y'], kind='cubic', fill_value='extrapolate')
    ag_z_interpolate = interp1d(acc_or_gyro_dict['timestamps'], acc_or_gyro_dict['z'], kind='cubic', fill_value='extrapolate')

    # [result_dict['x'].append(float(ag_x_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['y'].append(float(ag_y_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['z'].append(float(ag_z_interpolate(timestamp))) for timestamp in timestamp_list]

    result_dict['x'] = [(float(ag_x_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['y'] = [(float(ag_y_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['z'] = [(float(ag_z_interpolate(timestamp))) for timestamp in timestamp_list]

    # t_x = threading.Thread(target=fill_interpolation, args=(result_dict, 'x', ag_x_interpolate, timestamp_list),
    #                        daemon=True)
    # t_x.start()
    # t_y = threading.Thread(target=fill_interpolation, args=(result_dict, 'y', ag_y_interpolate, timestamp_list),
    #                        daemon=True)
    # t_y.start()
    # t_z = threading.Thread(target=fill_interpolation, args=(result_dict, 'z', ag_z_interpolate, timestamp_list),
    #                        daemon=True)
    # t_z.start()

    # t_x.join()
    # t_y.join()
    # t_z.join()

    # p_x = Process(target=fill_interpolation, args=(result_dict, 'x', ag_x_interpolate, timestamp_list), daemon=True)
    # p_x.start()
    # p_y = Process(target=fill_interpolation, args=(result_dict, 'y', ag_y_interpolate, timestamp_list), daemon=True)
    # p_y.start()
    # p_z = Process(target=fill_interpolation, args=(result_dict, 'z', ag_z_interpolate, timestamp_list), daemon=True)
    # p_z.start()

    # p_x.join()
    # p_y.join()
    # p_z.join()

    if is_acc:
        interpolated_dict['accelerometer'] = result_dict
    else:
        interpolated_dict['gyroscope'] = result_dict

    # return result_dict


def interpolate_emg(timestamp_list, emg_dict, interpolated_dict):
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

    # [result_dict['1'].append(float(emg1_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['2'].append(float(emg2_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['3'].append(float(emg3_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['4'].append(float(emg4_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['5'].append(float(emg5_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['6'].append(float(emg6_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['7'].append(float(emg7_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['8'].append(float(emg8_interpolate(timestamp))) for timestamp in timestamp_list]

    result_dict['1'] = [(float(emg1_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['2'] = [(float(emg2_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['3'] = [(float(emg3_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['4'] = [(float(emg4_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['5'] = [(float(emg5_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['6'] = [(float(emg6_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['7'] = [(float(emg7_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['8'] = [(float(emg8_interpolate(timestamp))) for timestamp in timestamp_list]

    interpolated_dict['emg'] = result_dict

    # return result_dict


def interpolate_orientation(timestamp_list, ori_dict, interpolated_dict):
    result_dict = {'x': [], 'y': [], 'z': [], 'w': []}

    ori_dict['timestamps'] = eliminate_duplicates(ori_dict['timestamps'])

    ori_x_interpolate = interp1d(ori_dict['timestamps'], ori_dict['x'], kind='cubic', fill_value='extrapolate')
    ori_y_interpolate = interp1d(ori_dict['timestamps'], ori_dict['y'], kind='cubic', fill_value='extrapolate')
    ori_z_interpolate = interp1d(ori_dict['timestamps'], ori_dict['z'], kind='cubic', fill_value='extrapolate')
    ori_w_interpolate = interp1d(ori_dict['timestamps'], ori_dict['w'], kind='cubic', fill_value='extrapolate')

    # [result_dict['x'].append(float(ori_x_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['y'].append(float(ori_y_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['z'].append(float(ori_z_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['w'].append(float(ori_w_interpolate(timestamp))) for timestamp in timestamp_list]

    result_dict['x'] = [(float(ori_x_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['y'] = [(float(ori_y_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['z'] = [(float(ori_z_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['w'] = [(float(ori_w_interpolate(timestamp))) for timestamp in timestamp_list]


    interpolated_dict['orientation'] = result_dict

    # return result_dict


def interpolate_orientationEuler(timestamp_list, oriEuler_dict, interpolated_dict):
    result_dict = {'roll': [], 'pitch': [], 'yaw': []}

    oriEuler_dict['timestamps'] = eliminate_duplicates(oriEuler_dict['timestamps'])

    roll_interpolate = interp1d(oriEuler_dict['timestamps'], oriEuler_dict['roll'], kind='cubic',
                                fill_value='extrapolate')
    pitch_interpolate = interp1d(oriEuler_dict['timestamps'], oriEuler_dict['pitch'], kind='cubic',
                                 fill_value='extrapolate')
    yaw_interpolate = interp1d(oriEuler_dict['timestamps'], oriEuler_dict['yaw'], kind='cubic',
                               fill_value='extrapolate')

    # [result_dict['roll'].append(float(roll_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['pitch'].append(float(pitch_interpolate(timestamp))) for timestamp in timestamp_list]
    # [result_dict['yaw'].append(float(yaw_interpolate(timestamp))) for timestamp in timestamp_list]

    result_dict['roll'] = [(float(roll_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['pitch'] = [(float(pitch_interpolate(timestamp))) for timestamp in timestamp_list]
    result_dict['yaw'] = [(float(yaw_interpolate(timestamp))) for timestamp in timestamp_list]

    interpolated_dict['orientationEuler'] = result_dict


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

    start = int(math.floor(sorted_list[0] / CONVERT_MILLI_MICRO) * CONVERT_MILLI_MICRO)
    end = int(math.ceil(sorted_list[-1] / CONVERT_MILLI_MICRO) * CONVERT_MILLI_MICRO)

    # start and end are returned in microseconds
    return start, end


# def get_parameters():
def main():
    rawUserPath = glob(rawPath + '\*')
    # rawUsers = [re.sub(r'.*\\', '', user) for user in rawUserPath]
    rawUsers = ['adrian']
    # print(rawUsers)

    thread_list = []

    for user in rawUsers:
        rawGesturePath = glob(os.path.join(rawPath, user) + '\*')
        # rawGestures = [re.sub(r'.*\\', '', gesture) for gesture in rawGesturePath]
        rawGestures = ['big_stop']
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

        # print('Converting gestures for {}... '.format(user), end='\n', flush=True)

        for gesture in rawGestures:
            gesture_dict = {}
            # print('Creating pickles {}/{}... '.format(user, gesture), end='', flush=True)
            acquire_data(user, gesture, gesture_dict)
            # print('DONE')

            # t = threading.Thread(target=acquire_data, args=(user, gesture, gesture_dict), daemon=True)
            # thread_list.append(t)
            # t.start()

            # thread_list.append((user, gesture, gesture_dict))
    # return thread_list

        # print('DONE')

    # for thread in thread_list:
    #     thread.join()

def main_process():
    result = get_parameters()

    with Pool() as p:
        p.starmap(acquire_data, result)

if __name__ == '__main__':
    starttime = time.time()
    result = main()

    # r = acquire_data(result[0][0], result[0][1], result[0][2])
    # print(r)
    # with Pool() as p:
    #     p.starmap(acquire_data, result)
    # interp = interpolate_and_save(r[0][0], r[0][1], r[0][2], r[0][3])
    # print(interp)
    print('CSVconverter: {}'.format(time.time()-starttime))
