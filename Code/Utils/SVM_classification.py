import os
import sys

import numpy as np

from sklearn.externals import joblib

module_path = os.path.dirname(sys.path[0])
if module_path not in sys.path:
    sys.path.append(module_path)

from Utils.data_preparation_helper import prepare_data


class SVMclassification:

    def __init__(self):
        self.acc_clf = None
        self.gyro_clf = None
        self.ori_clf = None
        self.emg_clf = None

        self.frame_config = None

        self.__clf_loaded = False

    def load_classifier(self, data_list):
        self.acc_clf = joblib.load(self.__find_path(data_list, 'acc')[0])
        self.gyro_clf = joblib.load(self.__find_path(data_list, 'gyro')[0])
        self.ori_clf = joblib.load(self.__find_path(data_list, 'ori')[0])
        self.emg_clf = joblib.load(self.__find_path(data_list, 'emg')[0])

        self.frame_config = joblib.load(self.__find_path(data_list, 'frame_config')[0])

        self.__clf_loaded = True

    def predict(self, gesture_dict):
        if self.__clf_loaded:
            acc_data = prepare_data(gesture_dict, self.frame_config['acc_frames'], 'accelerometer', is_labeled=False, verbose=False)
            gyro_data = prepare_data(gesture_dict, self.frame_config['gyro_frames'], 'gyro', is_labeled=False, verbose=False)
            ori_data = prepare_data(gesture_dict, self.frame_config['ori_frames'], 'orientation', is_labeled=False, verbose=False)
            emg_data = prepare_data(gesture_dict, self.frame_config['emg_frames'], 'emg', is_labeled=False, verbose=False)

            acc_pred_probs = self.acc_clf.predict_proba(acc_data)
            gyro_pred_probs = self.gyro_clf.predict_proba(gyro_data)
            ori_pred_probs = self.ori_clf.predict_proba(ori_data)
            emg_pred_probs = self.emg_clf.predict_proba(emg_data)

            acc_gyro = np.add(acc_pred_probs[0], gyro_pred_probs[0])
            ori_emg = np.add(ori_pred_probs[0], emg_pred_probs[0])
            final = np.divide(np.add(acc_gyro, ori_emg), 4)
            result = self.acc_clf.classes_[np.argmax(final)]

            print(result)
        else:
            print('Please load classifiers first!')

    @staticmethod
    def __find_path(search_list, find_this):
        return [found for found in search_list if find_this in found]