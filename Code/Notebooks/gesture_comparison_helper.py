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
