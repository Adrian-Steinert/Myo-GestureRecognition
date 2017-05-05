import csv
from math import floor
from myo import DeviceListener, StreamEmg
from datetime import datetime


class DataCollector(DeviceListener):

    def __init__(self):
        self.printedEMG = False
        self.printedACC = False
        self.printedGYR = False
        self.printedORI = False

        # TODO prepare files for writing
        self.emgFile = 'emg' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.csv'
        # self.gyroFile
        # self.orientationFile
        # self.orientationEulerFile
        # self.accelerometerFile

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
        myo.set_stream_emg(StreamEmg.enabled)
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
        pass

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        if not self.printedACC:
            self.printedACC = True
            print('ACCELEROMETER -- {}: {}'.format(timestamp, acceleration))
        pass

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if not self.printedGYR:
            self.printedGYR = True
            print('GYROSCOPE -- {}: {}'.format(timestamp, gyroscope))
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
        pass

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        print('WARMUP COMPLETE -- {}: {}'.format(timestamp, warmup_result))
        pass

# TODO prepare files for writing
'''
    def __openFile(self, filename):
        try:
            file = open(filename, 'wb', newline='')
        except IOError:
            print('Could not open file')
        with open(self.emgFile, 'wb', newline='') as csvfile:
            emgwriter = csv.writer(csvfile, delimiter=',')
'''