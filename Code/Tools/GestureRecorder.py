from time import sleep
from Utils import DataCollector
import myo as libmyo
libmyo.init('../../myo-sdk-win-0.9.0/bin')


def main():
    print("Connecting to Myo ... Use CTRL^C to exit.")
    try:
        hub = libmyo.Hub()
    except MemoryError:
        print("Myo Hub could not be created. Make sure Myo Connect is running.")
        return

    hub.set_locking_policy(libmyo.LockingPolicy.none)
    hub.run(1000, DataCollector.DataCollector())

    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        while hub.running:
            sleep(0.25)
    except KeyboardInterrupt:
        print("\nQuitting ...")
    finally:
        print("Shutting down hub...")
        hub.shutdown()


if __name__ == '__main__':
    main()
