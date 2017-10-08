import os
import sys

import numpy as np

from keras.models import model_from_json
from sklearn.externals import joblib

module_path = os.path.dirname(sys.path[0])
if module_path not in sys.path:
    sys.path.append(module_path)

from Utils.data_preparation_helper import prepare_data


class LSTMclassification:

    def __init__(self):
        self.acc_clf = None
        self.gyro_clf = None
        self.ori_clf = None
        self.emg_clf = None

        self.config = None

        self.encoder = None

        self.__clf_loaded = False

    def load_classifier(self, data_list):
        self.config = joblib.load(self.__find_path(data_list, 'config')[0])
        self.encoder = joblib.load(self.__find_path(data_list, 'encoder')[0])

        json = []
        weights = []

        for element in data_list:
            if 'weights' in element:
                weights.append(element)
            else:
                json.append(element)

        # print(json)
        # print(weights)

        json_file = open(self.__find_path(json, 'acc')[0], 'r')
        acc_lstm_json = json_file.read()
        json_file.close()
        self.acc_clf = model_from_json(acc_lstm_json)
        self.acc_clf.load_weights(self.__find_path(weights, 'acc')[0])
        self.acc_clf.compile(loss=self.config['loss'], optimizer=self.config['optimizer'], metrics=self.config['metrics'])

        json_file = open(self.__find_path(json, 'gyro')[0], 'r')
        gyro_lstm_json = json_file.read()
        json_file.close()
        self.gyro_clf = model_from_json(gyro_lstm_json)
        self.gyro_clf.load_weights(self.__find_path(weights, 'gyro')[0])
        self.gyro_clf.compile(loss=self.config['loss'], optimizer=self.config['optimizer'], metrics=self.config['metrics'])

        json_file = open(self.__find_path(json, 'ori')[0], 'r')
        ori_lstm_json = json_file.read()
        json_file.close()
        self.ori_clf = model_from_json(ori_lstm_json)
        self.ori_clf.load_weights(self.__find_path(weights, 'ori')[0])
        self.ori_clf.compile(loss=self.config['loss'], optimizer=self.config['optimizer'], metrics=self.config['metrics'])

        json_file = open(self.__find_path(json, 'emg')[0], 'r')
        emg_lstm_json = json_file.read()
        json_file.close()
        self.emg_clf = model_from_json(emg_lstm_json)
        self.emg_clf.load_weights(self.__find_path(weights, 'emg')[0])
        self.emg_clf.compile(loss=self.config['loss'], optimizer=self.config['optimizer'], metrics=self.config['metrics'])

        self.__clf_loaded = True

    def predict(self, gesture_dict):
        if self.__clf_loaded:
            acc_data = prepare_data(gesture_dict, self.config['acc_frames'], 'accelerometer',
                                    is_labeled=False, verbose=False)
            acc_data = acc_data.reshape(acc_data.shape[0], 1, acc_data.shape[1])

            gyro_data = prepare_data(gesture_dict, self.config['gyro_frames'], 'gyro',
                                     is_labeled=False, verbose=False)
            gyro_data = gyro_data.reshape(gyro_data.shape[0], 1, gyro_data.shape[1])

            ori_data = prepare_data(gesture_dict, self.config['ori_frames'], 'orientation',
                                    is_labeled=False, verbose=False)
            ori_data = ori_data.reshape(ori_data.shape[0], 1, ori_data.shape[1])

            emg_data = prepare_data(gesture_dict, self.config['emg_frames'], 'emg',
                                    is_labeled=False, verbose=False)
            emg_data = emg_data.reshape(emg_data.shape[0], 1, emg_data.shape[1])

            acc_pred_probs = self.acc_clf.predict(acc_data)
            gyro_pred_probs = self.gyro_clf.predict(gyro_data)
            ori_pred_probs = self.ori_clf.predict(ori_data)
            emg_pred_probs = self.emg_clf.predict(emg_data)

            acc_gyro = np.add(acc_pred_probs[0], gyro_pred_probs[0])
            ori_emg = np.add(ori_pred_probs[0], emg_pred_probs[0])
            final = np.divide(np.add(acc_gyro, ori_emg), 4)
            result = self.encoder.classes_[np.argmax(final)]

            print(result)
        else:
            print('Please load classifiers first!')

    @staticmethod
    def __find_path(search_list, find_this):
        return [found for found in search_list if find_this in found]
