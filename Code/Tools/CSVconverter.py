import os
import re
import csv
import sys
import time
import pickle

from glob import glob
from datetime import datetime

import threading
from multiprocessing import Pool

rawPath = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'raw')
convertedPath = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'converted')


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

    if is_acc:
        gesture_dict['accelerometer'] = data_dict
    else:
        gesture_dict['gyro'] = data_dict


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

    gesture_dict['emg'] = emg_dict


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

    gesture_dict['orientation'] = ori_dict


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

    for gesture_chunk in recordedData:
        gesture_dict['gesture'] = gesture
        gesture_dict['datetime'] = datetime.fromtimestamp(os.path.getctime(gesture_chunk[0]))
        gesture_dict['performed_by'] = user

        # acquire_acc_or_gyro(gesture_chunk[0], gesture_dict, is_acc=True)
        # acquire_emg(gesture_chunk[1], gesture_dict)
        # acquire_acc_or_gyro(gesture_chunk[2], gesture_dict, is_acc=False)
        # acquire_orientation_euler(gesture_chunk[3], gesture_dict)
        # acquire_orientation(gesture_chunk[4], gesture_dict)

        t_acc = threading.Thread(target=acquire_acc_or_gyro, args=(gesture_chunk[0], gesture_dict, True), daemon=True)
        t_acc.start()
        t_emg = threading.Thread(target=acquire_emg, args=(gesture_chunk[1], gesture_dict), daemon=True)
        t_emg.start()
        t_gyro = threading.Thread(target=acquire_acc_or_gyro, args=(gesture_chunk[2], gesture_dict, False), daemon=True)
        t_gyro.start()
        # t_oriEuler = threading.Thread(target=acquire_orientation_euler, args=(gesture_chunk[3], gesture_dict), daemon=True)
        # t_oriEuler.start()
        t_ori = threading.Thread(target=acquire_orientation, args=(gesture_chunk[4], gesture_dict), daemon=True)
        t_ori.start()

        t_acc.join()
        t_emg.join()
        t_gyro.join()
        # t_oriEuler.join()
        t_ori.join()

        # save dictionary as pickle to disk
        savePath = os.path.join(convertedPath, gesture_dict['performed_by'], gesture_dict['gesture'])
        os.makedirs(savePath, exist_ok=True)
        # extract timestamp from csv file name
        timestamp = re.sub(r'.*\\[a-z_]+', '', gesture_chunk[0]).strip('.csv')
        pickle.dump(gesture_dict, open(os.path.join(savePath, gesture_dict['gesture'] + timestamp) + '.p', 'wb'))
        # print(interpolated_dict)


def get_parameters():
    rawUserPath = glob(rawPath + '\*')
    rawUsers = [re.sub(r'.*\\', '', user) for user in rawUserPath]
    # rawUsers = ['adrian']
    # print(rawUsers)

    parameter_list = []

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

        # print('Converting gestures for {}... '.format(user), end='\n', flush=True)

        for gesture in rawGestures:
            gesture_dict = {}
            # acquire_data(user, gesture, gesture_dict)

            parameter_list.append((user, gesture, gesture_dict))
    return parameter_list


def main():
    params = get_parameters()

    with Pool() as p:
        p.starmap(acquire_data, params)

if __name__ == '__main__':
    starttime = time.time()
    main()
    # get_parameters()
    print('CSVconverter: {}'.format(time.time()-starttime))
