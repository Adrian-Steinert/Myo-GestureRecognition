from myo import DeviceListener, StreamEmg, WarmupState, WarmupResult
from datetime import datetime


class DataCollector(DeviceListener):

    def __init__(self, filewriter_instance):
        self.printedEMG = False
        self.printedACC = False
        self.printedGYR = False
        self.printedORI = False

        self.arm_synced = False
        self.warmup_complete = False

        self.fileWriter = filewriter_instance

    def on_pair(self, myo, timestamp, firmware_version):
        print('Myo paired')

    def on_unpair(self, myo, timestamp):
        print('Myo unpaired')

    def on_connect(self, myo, timestamp, firmware_version):
        print('CONNECTED -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), firmware_version))

    def on_disconnect(self, myo, timestamp):
        print('DISCONNECTED -- {}'.format(self.__timestamp_to_datetime(timestamp)))

    def on_arm_sync(self, myo, timestamp, arm, x_direction, rotation, warmup_state):
        print('SYNC -- {}: {} {}'.format(self.__timestamp_to_datetime(timestamp), arm, warmup_state))
        if warmup_state == WarmupState.warm:
            myo.set_stream_emg(StreamEmg.enabled)
        else:
            print('Warmup state was: {} -- EMG Stream could not be enabled!')

    def on_arm_unsync(self, myo, timestamp):
        print('ASYNC -- {}'.format(self.__timestamp_to_datetime(timestamp)))

    def on_unlock(self, myo, timestamp):
        # print('Myo unlocked')
        pass

    def on_lock(self, myo, timestamp):
        # print('Myo locked')
        pass

    # TODO: I do not know the initial pose when starting the script
    def on_pose(self, myo, timestamp, pose):
        # print('POSE -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), pose))
        pass

    def on_orientation_data(self, myo, timestamp, orientation):
        if not self.printedORI:
            self.printedORI = True
            print('ORIENTATION -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), orientation))

        if self.fileWriter.filesOpened:
            self.fileWriter.write_orientation_data(timestamp, orientation)

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        if not self.printedACC:
            self.printedACC = True
            print('ACCELEROMETER -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), acceleration))

        if self.fileWriter.filesOpened:
            self.fileWriter.write_accelerometer_data(timestamp, acceleration)

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if not self.printedGYR:
            self.printedGYR = True
            print('GYROSCOPE -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), gyroscope))

        if self.fileWriter.filesOpened:
            self.fileWriter.write_gyro_data(timestamp, gyroscope)

    def on_rssi(self, myo, timestamp, rssi):
        # print('RSSI -- {}: {}'.format(self.__timestampToDatetime(timestamp), rssi))
        pass

    def on_battery_level_received(self, myo, timestamp, level):
        print('BATTERY -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), level))

    def on_emg_data(self, myo, timestamp, emg):
        if not self.printedEMG:
            self.printedEMG = True
            print('EMG -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), emg))

            # print(datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f'))

        if self.fileWriter.filesOpened:
            self.fileWriter.write_emg_data(timestamp, emg)

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        print('WARMUP COMPLETE -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), warmup_result))
        if warmup_result == WarmupResult.success:
            myo.set_stream_emg(StreamEmg.enabled)

    @staticmethod
    def __timestamp_to_datetime(timestamp):

        # myo timestamps are microseconds as integer
        CONVERT_TO_SECONDS = 1_000_000

        return datetime.fromtimestamp(timestamp / CONVERT_TO_SECONDS)
