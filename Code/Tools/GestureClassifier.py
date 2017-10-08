import os
import re
import sys
import time
import msvcrt

import myo as libmyo

from time import sleep

# add project folder to path, this needs to be done so that modules of these folders are importable
module_path = os.path.dirname(sys.path[0])
if module_path not in sys.path:
    sys.path.append(module_path)
from Utils.GestureListener import GestureListener
from Utils.SVM_classification import SVMclassification
from Utils.HMM_classification import HMMclassification
from Utils.LSTM_classification import LSTMclassification

libmyo.init(os.path.join(os.path.dirname(sys.path[0]), 'myo-sdk-win-0.9.0', 'bin'))


gesture_listener = GestureListener()

# TODO: Implement different classifiers to choose from (SVM, LSTM, HMM)
def choose_classifier():
    possible_models = os.path.join(os.path.dirname(sys.path[0]), 'Data', 'models')

    clf_path = [dirname for dirname in os.listdir(possible_models)]
    # print(clf_path)

    if len(clf_path) == 0:
        return None

    choice_done = False

    while not choice_done:
        print('Available classifiers:')
        [print(clf) for clf in clf_path]
        chosen_clf = input('Please choose one...\n').split()[0].lower()

        if chosen_clf not in clf_path:
            print('\n{} is not an available classifier!'.format(chosen_clf))
            continue

        model_path = os.path.join(possible_models, chosen_clf)

        models = [model for model in os.listdir(model_path)]
        # print(models)

        print('Choose gesture set:')
        [print(gesture_set) for gesture_set in ['own', 'paper', 'all']]
        chosen_set = input('Please choose one...\n').split()[0].lower()

        chosen_models = [os.path.join(model_path, model) for model in models if chosen_set in model]

        if len(chosen_models) == 0:
            print('\nThis choice is not available!')
            continue

        choice_done = True

    # print(chosen_models)

    if chosen_clf == 'svm':
        clf = SVMclassification()
    elif chosen_clf == 'hmm':
        clf = HMMclassification()
    elif chosen_clf == 'lstm':
        clf = LSTMclassification()

    clf.load_classifier(chosen_models)

    return clf


def main():

    classifier = choose_classifier()

    if classifier is None:
        print('No models available!')
        return

    print('Connecting to Myo ... Use CTRL^C to exit.')
    try:
        hub = libmyo.Hub()
    except MemoryError:
        print('Myo Hub could not be created. Make sure Myo Connect is running.')
        return

    hub.set_locking_policy(libmyo.LockingPolicy.none)

    gesture_duration = 0

    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        hub.run(1000, gesture_listener)
        while hub.running:

            # check if Enter was pressed to start/stop recording data
            if msvcrt.kbhit() and (msvcrt.getch() == b'\r'):

                if gesture_listener.is_recording:
                    gesture_listener.is_recording = False

                    print('Finished recording gesture!')

                    print('Gesture duration: {}'.format(time.time() - gesture_duration))

                    # print(len(gesture_listener.gesture['accelerometer']['x']))
                    # print(len(gesture_listener.gesture['gyro']['x']))
                    # print(len(gesture_listener.gesture['orientation']['x']))
                    # print(len(gesture_listener.gesture['emg']['1']))

                    predict_duration = time.time()
                    classifier.predict([gesture_listener.gesture])
                    print('Predict duration: {}'.format(time.time() - predict_duration))

                else:
                    gesture_duration = time.time()
                    gesture_listener.is_recording = True
                    gesture_listener.gesture = gesture_listener.clear_gesture()
                    print('Recording gesture...')

            sleep(0.1)

    except KeyboardInterrupt:
        print('\nQuitting ...')

    finally:
        print('Shutting down hub... ', end='')
        hub.shutdown()
        print('DONE')


if __name__ == '__main__':
    main()
