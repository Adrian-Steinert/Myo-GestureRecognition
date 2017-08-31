import os
import numpy as np

from collections import Counter
from datetime import datetime
from hmmlearn.hmm import GaussianHMM
from sklearn.externals import joblib


class MyoHmmClassifier:
    def __init__(self, sensor_type, n_classes, n_states_per_hmm):
        self._sensor_type = sensor_type
        self._n_classes = n_classes
        self._class_mapping = {}
        self._n_states_per_hmm = n_states_per_hmm
        self._is_fit = False

    def fit(self, x, y):
        sorted_indices = np.argsort(y)
        x = x[sorted_indices]
        y = y[sorted_indices]
        class_counter = Counter(y)
        train_lengths = list(class_counter.values())

        if len(class_counter) != self._n_classes:
            print('Number of classes insufficient: Expected {} but was {}'.format(self._n_classes,
                                                                                  len(class_counter)))
            return None

        # map classes to hmm
        self._class_mapping = {class_label: GaussianHMM(self._n_states_per_hmm) for class_label in class_counter}

        # split up input into lists of the respective class
        splitted = np.array(np.split(x, [sum(train_lengths[:i]) for i in range(1, len(class_counter))]))

        # fit the class models
        for class_label, train_seqs in zip(self._class_mapping, splitted):
            self._class_mapping[class_label].fit(train_seqs)

        self._is_fit = True
        # return self.class_mapping

    def score(self, x):
        if self._is_fit:
            result = []
            for test_seq in x:
                test_seq = test_seq.reshape(1, -1)
                predictions = [(self._class_mapping[class_label].score(test_seq), class_label)
                               for class_label in self._class_mapping]
                result.append(predictions)
            return result
        else:
            print('Model is not fitted yet, call fit() first!')

    def predict(self, x):
        score_list = self.score(x)
        return [max(cls_score)[1] for cls_score in score_list]

    def monitor(self):
        if self._is_fit:
            return [(class_label, self._class_mapping[class_label].monitor_) for class_label in self._class_mapping]
        else:
            print('Model is not fitted yet, call fit() first!')

    ##########################
    # guess i won't need this
    ##########################
    def _save_models(self, directory_path):
        if os.path.isdir(directory_path):
            creation_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            for label in self._class_mapping:
                joblib.dump(self._class_mapping[label], os.path.join(directory_path, '' + label + creation_time + '.p'))
        else:
            print('{} is not a valid path to a directory!'.format(directory_path))