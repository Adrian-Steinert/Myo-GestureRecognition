import csv
import math
from myo import DeviceListener, StreamEmg, WarmupState, WarmupResult
from datetime import datetime


class DataCollector(DeviceListener):

    def __init__(self):
        self.printedEMG = False
        self.printedACC = False
        self.printedGYR = False
        self.printedORI = False


        # prepare variables for file objects to write data on disk
        self.emgFile = None
        self.emgFileWriter = None
        self.gyroFile = None
        self.gyroFileWriter = None
        self.orientationFile = None
        self.orientationFileWriter = None
        self.orientationEulerFile = None
        self.orientationEulerFileWriter = None
        self.accelerometerFile = None
        self.accelerometerFileWriter = None

        self.__openFiles()

    def on_pair(self, myo, timestamp, firmware_version):
        print('Myo paired')
        pass

    def on_unpair(self, myo, timestamp):
        print('Myo unpaired')
        pass

    def on_connect(self, myo, timestamp, firmware_version):
        print('CONNECTED -- {}: {}'.format(timestamp, firmware_version))
        pass

    def on_disconnect(self, myo, timestamp):
        print('DISCONNECTED -- {}'.format(timestamp))
        pass

    def on_arm_sync(self, myo, timestamp, arm, x_direction, rotation, warmup_state):
        print('SYNC -- {}: {} {}'.format(timestamp, arm, warmup_state))
        if (warmup_state == WarmupState.warm):
            myo.set_stream_emg(StreamEmg.enabled)
        else:
            print('Warmup state was: {} -- EMG Stream could not be enabled!')
        pass

    def on_arm_unsync(self, myo, timestamp):
        print('ASYMC -- {}'.format(timestamp))
        pass

    def on_unlock(self, myo, timestamp):
        print('Myo unlocked')
        pass

    def on_lock(self, myo, timestamp):
        print('Myo locked')
        pass

    # TODO: I do not know the initial pose when starting the script
    def on_pose(self, myo, timestamp, pose):
        print('POSE -- {}: {}'.format(timestamp, pose))
        pass

    def on_orientation_data(self, myo, timestamp, orientation):
        if not self.printedORI:
            self.printedORI = True
            print('ORIENTATION -- {}: {}'.format(timestamp, orientation))

        if (self.orientationFile.closed):
            self.orientationFile, self.orientationFileWriter = self.__reopenFile(self.orientationFile)
        if (self.orientationEulerFile.closed):
            self.orientationEulerFile, self.orientationEulerFileWriter = self.__reopenFile(self.orientationEulerFile)

        with self.orientationFile, self.orientationEulerFile:
            self.orientationFileWriter.writerow([timestamp, orientation.x, orientation.y, orientation.z, orientation.w])
            self.orientationEulerFileWriter.writerow([timestamp] + list(self.__calculateRollPitchYaw(orientation)))
        pass

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        if not self.printedACC:
            self.printedACC = True
            print('ACCELEROMETER -- {}: {}'.format(timestamp, acceleration))

        if (self.accelerometerFile.closed):
            self.accelerometerFile, self.accelerometerFileWriter = self.__reopenFile(self.accelerometerFile)

        with self.accelerometerFile:
            self.accelerometerFileWriter.writerow([timestamp, acceleration.x, acceleration.y, acceleration.z])
        pass

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if not self.printedGYR:
            self.printedGYR = True
            print('GYROSCOPE -- {}: {}'.format(timestamp, gyroscope))

        if (self.gyroFile.closed):
            self.gyroFile, self.gyroFileWriter = self.__reopenFile(self.gyroFile)

        with self.gyroFile:
            self.gyroFileWriter.writerow([timestamp, gyroscope.x, gyroscope.y, gyroscope.z])
        pass

    def on_rssi(self, myo, timestamp, rssi):
        # print('RSSI -- {}: {}'.format(timestamp, rssi))
        pass

    def on_battery_level_received(self, myo, timestamp, level):
        print('BATTERY -- {}: {}'.format(timestamp, level))
        pass

    def on_emg_data(self, myo, timestamp, emg):
        if not self.printedEMG:
            self.printedEMG = True
            print('EMG -- {}: {}'.format(timestamp, emg))

        if (self.emgFile.closed):
            self.emgFile, self.emgFileWriter = self.__reopenFile(self.emgFile)

        with self.emgFile:
            self.emgFileWriter.writerow([timestamp] + list(emg))
        pass

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        print('WARMUP COMPLETE -- {}: {}'.format(timestamp, warmup_result))
        if (warmup_result == WarmupResult.success):
            myo.set_stream_emg(StreamEmg.enabled)
        pass

    # open files and prepare them for writing
    def __openFiles(self):
        creationTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            self.emgFile = open('emg_' + creationTime + '.csv', 'a+', newline='')
            self.emgFileWriter = csv.writer(self.emgFile, delimiter=',')
            self.emgFileWriter.writerow(['timestamp,emg1,emg2,emg3,emg4,emg5,emg6,emg7,emg8'])

            self.gyroFile = open('gyro_' + creationTime + '.csv', 'a+', newline='')
            self.gyroFileWriter = csv.writer(self.gyroFile, delimiter=',')
            self.gyroFileWriter.writerow(['timestamp,x,y,z'])

            self.orientationFile = open('orientation_' + creationTime + '.csv', 'a+', newline='')
            self.orientationFileWriter = csv.writer(self.orientationFile, delimiter=',')
            self.orientationFileWriter.writerow(['timestamp,x,y,z,w'])

            self.orientationEulerFile = open('orientationEuler_' + creationTime + '.csv', 'a+', newline='')
            self.orientationEulerFileWriter = csv.writer(self.orientationEulerFile, delimiter=',')
            self.orientationEulerFileWriter.writerow(['timestamp,roll,pitch,yaw'])

            self.accelerometerFile = open('accelerometer_' + creationTime + '.csv', 'a+', newline='')
            self.accelerometerFileWriter = csv.writer(self.accelerometerFile, delimiter=',')
            self.accelerometerFileWriter.writerow(['timestamp,x,y,z'])
        except IOError:
            print('Could not open file!')

    # reopen files to append data, if an event has closed it
    # TODO i do not like this solution...
    def __reopenFile(self, fileObject):
        try:
           fileObject = open(fileObject.name, 'a+', newline='')
           fileObjectWriter = csv.writer(fileObject, delimiter=',')
           return fileObject, fileObjectWriter
        except IOError:
            print('Could not reopen file!')

    def __calculateRollPitchYaw(self, quaternionObject):
        w = quaternionObject.w
        x = quaternionObject.x
        y = quaternionObject.y
        z = quaternionObject.z

        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = math.atan2(2.0 * (w * z + x * y),	1.0 - 2.0 * (y * y + z * z))
        return roll, pitch, yaw