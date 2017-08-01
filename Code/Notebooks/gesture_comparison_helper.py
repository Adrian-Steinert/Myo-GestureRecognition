import os
import re
import pickle
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from scipy.fftpack import fft


def acc_print(data, ylim_range=[-1.5, 1.5]):
    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex='col', sharey='row')

    ax1.set_title('Accelerometer - x')
    ax1.grid(color='grey', linestyle='-.')
    ax1.set_ylim(ylim_range)
    ax2.set_title('Accelerometer - y')
    ax2.grid(color='grey', linestyle='-.')
    ax2.set_ylim(ylim_range)
    ax3.set_title('Accelerometer - z')
    ax3.grid(color='grey', linestyle='-.')
    ax3.set_ylim(ylim_range)

    colors = iter(cm.rainbow(np.linspace(0, 1, len(data))))
    handles = []
    labels = []

    for element in data:
        color = next(colors)
        labels.append(element['performed_by'])

        l1, = ax1.plot(element['accelerometer']['x'], color=color)
        ax2.plot(element['accelerometer']['y'], color=color)
        ax3.plot(element['accelerometer']['z'], color=color)

        handles.append(l1)

    f.legend(handles, labels, 'center right')


def emg_print(data, ylim_range=[-150, 150]):
    f, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, sharex='col', sharey='row')

    ax1.set_title('EMG 1')
    ax1.grid(color='grey', linestyle='-.')
    ax2.set_title('EMG 2')
    ax2.grid(color='grey', linestyle='-.')
    ax2.set_ylim(ylim_range)
    ax3.set_title('EMG 3')
    ax3.grid(color='grey', linestyle='-.')
    ax4.set_title('EMG 4')
    ax4.grid(color='grey', linestyle='-.')
    ax4.set_ylim(ylim_range)
    ax5.set_title('EMG 5')
    ax5.grid(color='grey', linestyle='-.')
    ax6.set_title('EMG 6')
    ax6.grid(color='grey', linestyle='-.')
    ax6.set_ylim(ylim_range)
    ax7.set_title('EMG 7')
    ax7.grid(color='grey', linestyle='-.')
    ax8.set_title('EMG 8')
    ax8.grid(color='grey', linestyle='-.')
    ax8.set_ylim(ylim_range)

    colors = iter(cm.rainbow(np.linspace(0, 1, len(data))))
    handles = []
    labels = []

    for element in data:
        color = next(colors)
        labels.append(element['performed_by'])

        l1, = ax1.plot(element['emg']['1'], color=color)
        ax2.plot(element['emg']['2'], color=color)
        ax3.plot(element['emg']['3'], color=color)
        ax4.plot(element['emg']['4'], color=color)
        ax5.plot(element['emg']['5'], color=color)
        ax6.plot(element['emg']['6'], color=color)
        ax7.plot(element['emg']['7'], color=color)
        ax8.plot(element['emg']['8'], color=color)

        handles.append(l1)

    f.legend(handles, labels, 'center right')


def gyro_print(data, ylim_range=[-250, 250]):
    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex='col', sharey='row')

    ax1.set_title('Gyroscope - x')
    ax1.grid(color='grey', linestyle='-.')
    ax1.set_ylim(ylim_range)
    ax2.set_title('Gyroscope - y')
    ax2.grid(color='grey', linestyle='-.')
    ax2.set_ylim(ylim_range)
    ax3.set_title('Gyroscope - z')
    ax3.grid(color='grey', linestyle='-.')
    ax3.set_ylim(ylim_range)

    colors = iter(cm.rainbow(np.linspace(0, 1, len(data))))
    handles = []
    labels = []

    for element in data:
        color = next(colors)
        labels.append(element['performed_by'])

        l1, = ax1.plot(element['gyro']['x'], color=color)
        ax2.plot(element['gyro']['y'], color=color)
        ax3.plot(element['gyro']['z'], color=color)

        handles.append(l1)

    f.legend(handles, labels, 'center right')


def orientation_print(data, ylim_range=[-1.5, 1.5]):
    f, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex='col', sharey='row')

    ax1.set_title('Orientation - x')
    ax1.grid(color='grey', linestyle='-.')
    ax1.set_ylim(ylim_range)
    ax2.set_title('Orientation - y')
    ax2.grid(color='grey', linestyle='-.')
    ax2.set_ylim(ylim_range)
    ax3.set_title('Orientation - z')
    ax3.grid(color='grey', linestyle='-.')
    ax3.set_ylim(ylim_range)
    ax4.set_title('Orientation - w')
    ax4.grid(color='grey', linestyle='-.')
    ax4.set_ylim(ylim_range)

    colors = iter(cm.rainbow(np.linspace(0, 1, len(data))))
    handles = []
    labels = []

    for element in data:
        color = next(colors)
        labels.append(element['performed_by'])

        l1, = ax1.plot(element['orientation']['x'], linewidth=2, color=color)
        ax3.plot(element['orientation']['z'], linewidth=2, color=color)
        ax2.plot(element['orientation']['y'], linewidth=2, color=color)
        ax4.plot(element['orientation']['w'], linewidth=2, color=color)

        handles.append(l1)

    f.legend(handles, labels, 'center right')


def orientation_euler_print(data, ylim_range=[-5, 5]):
    f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex='col', sharey='row')

    ax1.set_title('Orientation Euler - roll')
    ax1.grid(color='grey', linestyle='-.')
    ax1.set_ylim(ylim_range)
    ax2.set_title('Orientation Euler - pitch')
    ax2.grid(color='grey', linestyle='-.')
    ax2.set_ylim(ylim_range)
    ax3.set_title('Orientation Euler - yaw')
    ax3.grid(color='grey', linestyle='-.')
    ax3.set_ylim(ylim_range)

    colors = iter(cm.rainbow(np.linspace(0, 1, len(data))))
    handles = []
    labels = []

    for element in data:
        color = next(colors)
        labels.append(element['performed_by'])

        l1, = ax1.plot(element['orientationEuler']['roll'], color=color)
        ax2.plot(element['orientationEuler']['pitch'], color=color)
        ax3.plot(element['orientationEuler']['yaw'], color=color)

        handles.append(l1)

    f.legend(handles, labels, 'center right')

def all_print(data):
    acc_print(data)
    emg_print(data)
    gyro_print(data)
    orientation_print(data)
    # orientation_euler_print(data)


def load_gestures(path):
    loaded_data = []

    for element in path:
        loaded_data.append(pickle.load(open(element, 'rb')))
    return loaded_data

# sensor_data is a list with data of sensor data axes
def split_in_frames(sensor_data, frame_number):
    '''
    every two adjunct sequences make a frame
    => input data has one segment more than frames
    => frame length is two times segment lenght
    '''
    data_length = len(sensor_data[0])
    segment_count = frame_number + 1
    segment_length = data_length // segment_count
    cut_off = data_length % segment_count
    frame_length = 2 * segment_length

    segmented_data = []
    for sensor_axis in sensor_data:
        if cut_off > 0:
            filtered_sensor_axis = sensor_axis[:-cut_off]
        else:
            filtered_sensor_axis = sensor_axis[:]

        segmented_axis = []
        for segment in range(0, len(filtered_sensor_axis), segment_length):
            step_size = segment + frame_length
            segmented_axis.append(filtered_sensor_axis[segment:step_size])

        segmented_data.append(segmented_axis)

    return segmented_data

def create_acc_feature_vector(frame_list):
    if frame_list is None:
        print('frame_list was None in create create_acc_feature_vector()')
        return None

    acc_feature_vector = []
    x_axis = frame_list[0]
    y_axis = frame_list[1]
    z_axis = frame_list[2]

    for x_segment, y_segment, z_segment in zip(x_axis, y_axis, z_axis):
        acc_feature_vector.extend(create_frequency_domain_features(x_segment, y_segment, z_segment))
        acc_feature_vector.extend(create_time_domain_features(x_segment, y_segment, z_segment))

    return acc_feature_vector


def create_frequency_domain_features(x_segment, y_segment, z_segment):
    frequency_domain_features = []

    # first feature: mean
    x_fft = fft(x_segment)
    y_fft = fft(y_segment)
    z_fft = fft(z_segment)
    x_mean = x_fft[0]
    y_mean = y_fft[0]
    z_mean = z_fft[0]
    frequency_domain_features.extend([x_mean, y_mean, z_mean])

    # second feature: energy
    x_energy = calculate_energy(x_fft[1:])
    y_energy = calculate_energy(y_fft[1:])
    z_energy = calculate_energy(z_fft[1:])
    frequency_domain_features.extend([x_energy, y_energy, z_energy])

    # third feature: entropy
    x_entropy = calculate_entropy(x_fft, x_fft[1:])
    y_entropy = calculate_entropy(y_fft, y_fft[1:])
    z_entropy = calculate_entropy(z_fft, z_fft[1:])
    frequency_domain_features.extend([x_entropy, y_entropy, z_entropy])

    return frequency_domain_features


def calculate_energy(fft_no_mean_segment):
    energy = np.divide(np.sum(np.square(np.absolute(fft_no_mean_segment))), len(fft_no_mean_segment + 1))
    return energy


def calculate_entropy(fft_segment, fft_no_mean_segment):
    probability = np.divide(np.absolute(fft_segment), np.sum(np.absolute(fft_no_mean_segment)))
    entropy = np.sum(np.multiply(probability, np.log2(np.divide(1, probability))))
    return entropy


def create_time_domain_features(x_segment, y_segment, z_segment):
    time_domain_features = []

    # fourth feature: standard deviation
    x_std_dev = np.std(x_segment)
    y_std_dev = np.std(y_segment)
    z_std_dev = np.std(z_segment)
    time_domain_features.extend([x_std_dev, y_std_dev, z_std_dev])

    # fith feature: axis correlation
    x_y_correlation = calculate_axis_correlation(x_segment, y_segment)
    x_z_correlation = calculate_axis_correlation(x_segment, z_segment)
    y_z_correlation = calculate_axis_correlation(y_segment, z_segment)
    time_domain_features.extend([x_y_correlation, x_z_correlation, y_z_correlation])

    return time_domain_features


def calculate_axis_correlation(axis_1, axis_2):
    different_axis = np.divide(np.sum(np.abs(np.multiply(axis_1, axis_2))), len(axis_1))
    same_axis_1 = np.divide(np.sum(np.abs(np.multiply(axis_1, axis_1))), len(axis_1))
    same_axis_2 = np.divide(np.sum(np.abs(np.multiply(axis_2, axis_2))), len(axis_1))

    correlation_enumerator = np.subtract(different_axis, np.multiply(np.mean(axis_1), np.mean(axis_2)))
    correlation_denominator = np.multiply(np.sqrt(np.subtract(same_axis_1, np.square(np.mean(axis_1)))),
                                          np.sqrt(np.subtract(same_axis_2, np.square(np.mean(axis_2)))))
    correlation = np.divide(correlation_enumerator, correlation_denominator)
    return correlation