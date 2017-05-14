import csv
import math
from datetime import datetime


class FileWriter:

    def __init__(self):
        self.filesOpened = False

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

    # open files and prepare them for writing
    def open_files(self):
        creation_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        try:
            self.emgFile = open('emg_' + creation_time + '.csv', 'a+', newline='')
            self.emgFileWriter = csv.writer(self.emgFile, delimiter=',')
            self.emgFileWriter.writerow(['timestamp,emg1,emg2,emg3,emg4,emg5,emg6,emg7,emg8'])

            self.gyroFile = open('gyro_' + creation_time + '.csv', 'a+', newline='')
            self.gyroFileWriter = csv.writer(self.gyroFile, delimiter=',')
            self.gyroFileWriter.writerow(['timestamp,x,y,z'])

            self.orientationFile = open('orientation_' + creation_time + '.csv', 'a+', newline='')
            self.orientationFileWriter = csv.writer(self.orientationFile, delimiter=',')
            self.orientationFileWriter.writerow(['timestamp,x,y,z,w'])

            self.orientationEulerFile = open('orientationEuler_' + creation_time + '.csv', 'a+', newline='')
            self.orientationEulerFileWriter = csv.writer(self.orientationEulerFile, delimiter=',')
            self.orientationEulerFileWriter.writerow(['timestamp,roll,pitch,yaw'])

            self.accelerometerFile = open('accelerometer_' + creation_time + '.csv', 'a+', newline='')
            self.accelerometerFileWriter = csv.writer(self.accelerometerFile, delimiter=',')
            self.accelerometerFileWriter.writerow(['timestamp,x,y,z'])
        except IOError:
            print('Could not open file!')

        self.filesOpened = True

    def write_emg_data(self, timestamp, emg):
        if self.filesOpened:
            self.emgFileWriter.writerow([timestamp] + list(emg))

    def write_gyro_data(self, timestamp, gyroscope):
        if self.filesOpened:
            self.gyroFileWriter.writerow([timestamp, gyroscope.x, gyroscope.y, gyroscope.z])

    def write_orientation_data(self, timestamp, orientation):
        if self.filesOpened:
            self.orientationFileWriter.writerow([timestamp, orientation.x, orientation.y, orientation.z, orientation.w])
            self.orientationEulerFileWriter.writerow([timestamp] + list(self.__calculate_roll_pitch_yaw(orientation)))

    def write_accelerometer_data(self, timestamp, acceleration):
        if self.filesOpened:
            self.accelerometerFileWriter.writerow([timestamp, acceleration.x, acceleration.y, acceleration.z])

    def close_files(self):
        self.filesOpened = False

        self.emgFile.close()
        self.gyroFile.close()
        self.orientationFile.close()
        self.orientationEulerFile.close()
        self.accelerometerFile.close()

    @staticmethod
    def __calculate_roll_pitch_yaw(quaternion_object):
        w = quaternion_object.w
        x = quaternion_object.x
        y = quaternion_object.y
        z = quaternion_object.z

        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        return roll, pitch, yaw
