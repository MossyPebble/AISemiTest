import numpy as np
import matplotlib.pyplot as plt

def get_data(file_path):

    """
    .npy 파일을 읽어와서 데이터를 반환한다.

    Args:
        file_path (str): 읽어올 파일의 경로

    Returns:
        numpy.ndarray: 읽어온 데이터
    """
    
    return np.load(file_path)

def show_hspice_data(data, label):

    """
    hspice로 얻은 IV 데이터를 그래프로 그린다.

    Args:
        data (numpy.ndarray): 그래프로 그릴 데이터
        label (numpy.ndarray): 데이터의 라벨
    """

    plt.plot(data[:, 0], data[:, 1])
    plt.xlabel('V (V)')
    plt.ylabel('I (uA)')
    plt.title(f'V-I curve: {label}')
    plt.show()

def normalization(data, max_val, min_val):
    
    """
    데이터를 정규화한다.

    Args:
        data (numpy.ndarray): 정규화할 데이터
        max_val (float): 데이터의 최댓값
        min_val (float): 데이터의 최솟값

    Returns:
        numpy.ndarray: 정규화된 데이터
    """

    return (data - min_val) / (max_val - min_val)

def denormalization(data, max_val, min_val):
    
    """
    데이터를 역정규화한다.

    Args:
        data (numpy.ndarray): 역정규화할 데이터
        max_val (float): 데이터의 최댓값
        min_val (float): 데이터의 최솟값

    Returns:
        numpy.ndarray: 역정규화된 데이터
    """

    return data * (max_val - min_val) + min_val

# data = get_data(r'C:\temp\0_data.npy')
# label = get_data(r'C:\temp\0_label.npy')

# print(data.shape)
# print(label.shape)

# index_of_data = 0

# print(data[index_of_data])
# print(label[index_of_data])

# show_hspice_data(data[index_of_data], label[index_of_data])