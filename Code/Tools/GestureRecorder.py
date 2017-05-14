import os
import sys
import msvcrt
from time import sleep
import myo as libmyo

# add project folder to path, this needs to be done so that modules of these folders are importable
sys.path.append(os.path.dirname(sys.path[0]))
from Utils import FileWriter, DataCollector

libmyo.init(os.path.join(os.path.dirname(sys.path[0]), 'myo-sdk-win-0.9.0', 'bin'))

fileWriter = FileWriter.FileWriter()
dataCollector = DataCollector.DataCollector(fileWriter)


def main():
    print("Connecting to Myo ... Use CTRL^C to exit.")
    try:
        hub = libmyo.Hub()
    except MemoryError:
        print("Myo Hub could not be created. Make sure Myo Connect is running.")
        return

    hub.set_locking_policy(libmyo.LockingPolicy.none)

    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        hub.run(1000, dataCollector)
        while hub.running:

            # check if Enter was pressed to start/stop recording data
            if msvcrt.kbhit() and (msvcrt.getch() == b'\r'):
                if fileWriter.filesOpened:
                    print('Finished collecting data!')
                    fileWriter.close_files()
                else:
                    print('Starting to collect data...')
                    fileWriter.open_files()

            sleep(0.1)

    except KeyboardInterrupt:
        print("\nQuitting ...")

    finally:
        if fileWriter.filesOpened:
            print('Closing files...')
            fileWriter.close_files()
        print("Shutting down hub...")
        hub.shutdown()


if __name__ == '__main__':
    main()
