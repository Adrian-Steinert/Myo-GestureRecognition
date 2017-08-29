from myo import DeviceListener, StreamEmg, WarmupState, WarmupResult
from datetime import datetime


class GestureListener(DeviceListener):

    def __init__(self):
        self.arm_synced = False
        self.warmup_complete = False

        self.is_recording = False

        self.gesture = self.clear_gesture()

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
        if self.is_recording:
            self.gesture['orientation']['timestamp'].append(timestamp)
            self.gesture['orientation']['z'].append(orientation.x)
            self.gesture['orientation']['x'].append(orientation.y)
            self.gesture['orientation']['y'].append(orientation.z)
            self.gesture['orientation']['w'].append(orientation.w)

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        if self.is_recording:
            self.gesture['accelerometer']['timestamp'].append(timestamp)
            self.gesture['accelerometer']['x'].append(acceleration.x)
            self.gesture['accelerometer']['y'].append(acceleration.y)
            self.gesture['accelerometer']['z'].append(acceleration.z)

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        if self.is_recording:
            self.gesture['gyro']['timestamp'].append(timestamp)
            self.gesture['gyro']['x'].append(gyroscope.x)
            self.gesture['gyro']['y'].append(gyroscope.y)
            self.gesture['gyro']['z'].append(gyroscope.z)

    def on_rssi(self, myo, timestamp, rssi):
        # print('RSSI -- {}: {}'.format(self.__timestampToDatetime(timestamp), rssi))
        pass

    def on_battery_level_received(self, myo, timestamp, level):
        if level <= 35:
            print('BATTERY LOW -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), level))

    def on_emg_data(self, myo, timestamp, emg):
        if self.is_recording:
            self.gesture['emg']['timestamp'].append(timestamp)
            self.gesture['emg']['1'].append(emg[0])
            self.gesture['emg']['2'].append(emg[1])
            self.gesture['emg']['3'].append(emg[2])
            self.gesture['emg']['4'].append(emg[3])
            self.gesture['emg']['5'].append(emg[4])
            self.gesture['emg']['6'].append(emg[5])
            self.gesture['emg']['7'].append(emg[6])
            self.gesture['emg']['8'].append(emg[7])

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        print('WARMUP COMPLETE -- {}: {}'.format(self.__timestamp_to_datetime(timestamp), warmup_result))
        if warmup_result == WarmupResult.success:
            myo.set_stream_emg(StreamEmg.enabled)

    @staticmethod
    def clear_gesture(self):
        gesture = {'accelerometer':
                    {
                        'timestamps': [],
                        'x': [],
                        'y': [],
                        'z': []
                    },
                    'emg':
                        {
                            'timestamps': [],
                            '1': [],
                            '3': [],
                            '2': [],
                            '4': [],
                            '5': [],
                            '6': [],
                            '7': [],
                            '8': []
                        },
                    'gyro':
                        {
                            'timestamps': [],
                            'x': [],
                            'y': [],
                            'z': []
                        },
                    'orientation':
                        {
                            'timestamps': [],
                            'x': [],
                            'y': [],
                            'z': [],
                            'w': []
                        }
                }
        return gesture

    @staticmethod
    def __timestamp_to_datetime(timestamp):

        # myo timestamps are microseconds as integer
        CONVERT_TO_SECONDS = 1_000_000

        return datetime.fromtimestamp(timestamp / CONVERT_TO_SECONDS)
