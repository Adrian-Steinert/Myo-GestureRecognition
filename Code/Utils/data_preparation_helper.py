import pickle
import numpy as np

from itertools import combinations
from scipy.fftpack import fft
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.ar_model import AR


def load_gestures(path):
    loaded_data = []

    for element in path:
        loaded_data.append(pickle.load(open(element, 'rb')))
    return loaded_data


def create_frequency_domain_features(axis_fragment_list):
    frequency_domain_features = []

    mean_feature = []
    energy_feature = []
    entropy_feature = []

    for axis_fragment in axis_fragment_list:

        # first feature: mean
        axis_fragment_fft = fft(axis_fragment)
        axis_fragment_mean = axis_fragment_fft[0]
        mean_feature.append(axis_fragment_mean)

        # second feature: energy
        axis_fragment_energy = calculate_energy(axis_fragment_fft[1:], len(axis_fragment))
        energy_feature.append(axis_fragment_energy)

        # third feature: entropy
        axis_fragment_entropy = calculate_entropy(axis_fragment_fft, axis_fragment_fft[1:])
        entropy_feature.append(axis_fragment_entropy)

    frequency_domain_features.extend(mean_feature)
    frequency_domain_features.extend(energy_feature)
    frequency_domain_features.extend(entropy_feature)

    return frequency_domain_features


def calculate_energy(fft_no_mean_fragment, fragment_length):
    energy = np.divide(np.sum(np.square(np.absolute(fft_no_mean_fragment))), fragment_length)
    return energy


def calculate_entropy(fft_fragment, fft_no_mean_fragment):
    probability = np.divide(np.absolute(fft_fragment), np.sum(np.absolute(fft_no_mean_fragment)))

    # mask all values that equal 0, then create new array without masked values
    # => otherwise entropy calculation would fail due to division by 0
    filtered_probability = np.ma.masked_equal(probability, 0).compressed()

    entropy = np.sum(np.multiply(filtered_probability, np.log2(np.divide(1, filtered_probability))))

    return entropy


def create_time_domain_features(axis_fragment_list):
    time_domain_features = []

    for axis_fragment in axis_fragment_list:
        # fourth feature: standard deviation
        axis_fragment_std_dev = np.std(axis_fragment)
        time_domain_features.append(axis_fragment_std_dev)

    # fith feature: axis correlation
    # we want to have two fragments of different axis, to calculate correlation
    for axis_fragment_combination in combinations(axis_fragment_list, 2):
        axis_fragment_correlation = calculate_axis_correlation(axis_fragment_combination[0],
                                                               axis_fragment_combination[1])
        time_domain_features.append(axis_fragment_correlation)
    # print(len(time_domain_features))
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


def create_emg_features(axis_fragment_list, order=4):
    emg_features = []

    ar_feature = []
    mav_feature = []

    for axis_fragment in axis_fragment_list:
        ar_model = AR(axis_fragment)
        ar_model_fit = ar_model.fit(maxlag=order)
        # print('Lag: {}'.format(ar_model_fit.k_ar))
        # print(ar_model_fit.params)
        ar_feature.extend(ar_model_fit.params)
        mav_feature.append(np.mean(np.abs(axis_fragment)))

    emg_features.extend(ar_feature)
    emg_features.extend(mav_feature)

    return emg_features


def split_in_frames(sensor_data, frame_number):
    # every two adjunct sequences make a frame
    # => input data has one segment more than frames
    # => frame length is two times segment lenght

    data_length = len(sensor_data[0])
    segment_count = frame_number + 1
    segment_length = data_length // segment_count

    # check if data is long enough for given frame_number
    if segment_length <= 2:
        return None

    cut_off = data_length % segment_count
    frame_length = 2 * segment_length

    fragmented_data = []
    for sensor_axis in sensor_data:
        if cut_off > 0:
            filtered_sensor_axis = sensor_axis[:-cut_off]
        else:
            filtered_sensor_axis = sensor_axis[:]

        fragmented_axis = []
        for segment in range(0, len(filtered_sensor_axis) - segment_length, segment_length):
            step_size = segment + frame_length
            fragmented_axis.append(filtered_sensor_axis[segment:step_size])

        fragmented_data.append(fragmented_axis)

    return fragmented_data


def create_feature_vector(frame_list, sensor_type):
    if frame_list is None:
        return None

    feature_vector = []
    axis_count = len(frame_list)

    # reshape from:
    # shape = (3, 2, 5)
    # [[['x1' 'x1' 'x1' 'x1' 'x1']
    #   ['x2' 'x2' 'x2' 'x2' 'x2']]
    #
    #  [['y1' 'y1' 'y1' 'y1' 'y1']
    #     ['y2' 'y2' 'y2' 'y2' 'y2']]
    #
    #  [['z1' 'z1' 'z1' 'z1' 'z1']
    #     ['z2' 'z2' 'z2' 'z2' 'z2']]]
    #
    # to:
    # shape = (6, 5)
    # [['x1' 'x1' 'x1' 'x1' 'x1']
    #  ['y1' 'y1' 'y1' 'y1' 'y1']
    #  ['z1' 'z1' 'z1' 'z1' 'z1']
    #  ['x2' 'x2' 'x2' 'x2' 'x2']
    #  ['y2' 'y2' 'y2' 'y2' 'y2']
    #  ['z2' 'z2' 'z2' 'z2' 'z2']]
    #
    # => new dimension (from 3 to 2)
    # => new order: sorted by 'column'
    frame_list = np.array(frame_list)
    # print(frame_list.shape)
    frame_list = frame_list.reshape(-1, frame_list.shape[2], order='F')
    # print(frame_list.shape)

    # create emg features
    if sensor_type == 'emg':
        for axis_index in range(0, len(frame_list), axis_count):
            feature_vector.extend(create_emg_features(frame_list[axis_index:axis_index + axis_count]))
    # create imu features
    else:
        for axis_index in range(0, len(frame_list), axis_count):
            feature_vector.extend(create_frequency_domain_features(frame_list[axis_index:axis_index + axis_count]))
            feature_vector.extend(create_time_domain_features(frame_list[axis_index:axis_index + axis_count]))

    # print(len(feature_vector))
    return feature_vector


def prepare_data(acc_train, frame_number, sensor_type):
    label = []
    train_input = []
    features_per_gesture = []

    scaler = MinMaxScaler(feature_range=(0, 1))

    for gesture in acc_train:
        sensor_data = [gesture[sensor_type][sensor_axis] for sensor_axis in gesture[sensor_type]
                       if sensor_axis != 'timestamps']

        splitted_frames = split_in_frames(sensor_data, frame_number)

        if splitted_frames is None:
            data_length = len(gesture[sensor_type]['timestamps'])
            print('split_in_frames() returned None for sensor_type {}: Data length was {} but needs to be at least {}'
                  .format(sensor_type, data_length, (frame_number + 1) * 3))
            continue

        features = create_feature_vector(splitted_frames, sensor_type)

        if features is not None:
            features_per_gesture.append(features)
            label.append(gesture['gesture'])

    for feature_list in features_per_gesture:
        features = np.abs(feature_list)
        o_shape = features.shape

        features = scaler.fit_transform(features.reshape(-1, 1)).reshape(o_shape)

        train_input.append(features)
    return np.array(train_input), np.array(label)

########################################################################################################################
# the following functions are deprecated due to their static nature, they were replaced by their respective dynamic
# versions


def _depr_create_acc_feature_vector(frame_list):
    if frame_list is None:
        return None

    acc_feature_vector = []
    x_axis = frame_list[0]
    y_axis = frame_list[1]
    z_axis = frame_list[2]

    for x_fragment, y_fragment, z_fragment in zip(x_axis, y_axis, z_axis):
        acc_feature_vector.extend(_depr_create_frequency_domain_features(x_fragment, y_fragment, z_fragment))
        acc_feature_vector.extend(_depr_create_time_domain_features(x_fragment, y_fragment, z_fragment))

    return acc_feature_vector


def _depr_create_frequency_domain_features(x_fragment, y_fragment, z_fragment):
    frequency_domain_features = []

    # first feature: mean
    x_fft = fft(x_fragment)
    y_fft = fft(y_fragment)
    z_fft = fft(z_fragment)

    x_mean = x_fft[0]
    y_mean = y_fft[0]
    z_mean = z_fft[0]
    frequency_domain_features.extend([x_mean, y_mean, z_mean])

    # second feature: energy
    x_energy = calculate_energy(x_fft[1:], len(x_fragment))
    y_energy = calculate_energy(y_fft[1:], len(y_fragment))
    z_energy = calculate_energy(z_fft[1:], len(z_fragment))
    frequency_domain_features.extend([x_energy, y_energy, z_energy])

    # third feature: entropy
    x_entropy = calculate_entropy(x_fft, x_fft[1:])
    y_entropy = calculate_entropy(y_fft, y_fft[1:])
    z_entropy = calculate_entropy(z_fft, z_fft[1:])
    frequency_domain_features.extend([x_entropy, y_entropy, z_entropy])

    return frequency_domain_features


def _depr_create_time_domain_features(x_fragment, y_fragment, z_fragment):
    time_domain_features = []

    # fourth feature: standard deviation
    x_std_dev = np.std(x_fragment)
    y_std_dev = np.std(y_fragment)
    z_std_dev = np.std(z_fragment)
    time_domain_features.extend([x_std_dev, y_std_dev, z_std_dev])

    # fith feature: axis correlation
    x_y_correlation = calculate_axis_correlation(x_fragment, y_fragment)
    x_z_correlation = calculate_axis_correlation(x_fragment, z_fragment)
    y_z_correlation = calculate_axis_correlation(y_fragment, z_fragment)
    time_domain_features.extend([x_y_correlation, x_z_correlation, y_z_correlation])

    return time_domain_features
