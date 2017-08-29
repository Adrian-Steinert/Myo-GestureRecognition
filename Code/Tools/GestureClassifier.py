import os
import sys
import msvcrt
from time import sleep
import myo as libmyo

# add project folder to path, this needs to be done so that modules of these folders are importable
sys.path.append(os.path.dirname(sys.path[0]))
from Utils import GestureListener

libmyo.init(os.path.join(os.path.dirname(sys.path[0]), 'myo-sdk-win-0.9.0', 'bin'))


gesture_listener = GestureListener.GestureListener()

# TODO: Implement different classifiers to choose from (SVM, LSTM, HMM)


def main():
    print('Connecting to Myo ... Use CTRL^C to exit.')
    try:
        hub = libmyo.Hub()
    except MemoryError:
        print('Myo Hub could not be created. Make sure Myo Connect is running.')
        return

    hub.set_locking_policy(libmyo.LockingPolicy.none)

    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        hub.run(1000, gesture_listener)
        while hub.running:

            # check if Enter was pressed to start/stop recording data
            if msvcrt.kbhit() and (msvcrt.getch() == b'\r'):
                if gesture_listener.is_recording:
                    gesture_listener.is_recording = False

            # TODO: test implementation of GestureListener. if self.gesture doesn't get filled correctly, split the dict

                    print('Finished recording gesture!')
                else:
                    gesture_listener.is_recording = True
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
