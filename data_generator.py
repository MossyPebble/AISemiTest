import HSPICE_SSH
import numpy as np

sp_file_path = r'/data2/Users/cws/one_nmos.sp'
server_info = HSPICE_SSH.get_server_info_from_txt(r'server_info.txt')

HspiceSSH = HSPICE_SSH.HSPICE_SSH(*server_info)
HspiceSSH.sp_file_path = sp_file_path

def generate_data(drain_volt):

    HspiceSSH.drain_volt_change(drain_volt)

    data, axis_name = HspiceSSH.get_hspice_data()

    parameter_index = [i for i in range(len(axis_name)) if '_change' in axis_name[i]]
    parameter_name = [axis_name[i].replace('_change', '').replace('param', '').strip() for i in parameter_index]

    label = np.zeros((len(data), len(parameter_name)))

    for i, j in enumerate(parameter_index):
        label[:, i] = data[:, j, 0]

    for i, j in enumerate(parameter_index[::-1]):
        data = np.delete(data, j, axis=1)

    for i, j in enumerate(parameter_index[::-1]):
        axis_name = np.delete(axis_name, j)

    volt_index = [i for i in range(len(axis_name)) if 'volt' in axis_name[i]]
    volt = data[0, 0, :]
    for i, j in enumerate(volt_index[::-1]):
        data = np.delete(data, j, axis=1)
    for i, j in enumerate(volt_index[::-1]):
        axis_name = np.delete(axis_name, j)

    data = np.insert(data, 1, np.log(data[:, 0, :]), axis=1)
    axis_name = np.insert(axis_name, 1, 'log')
    data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)

    return data, label, axis_name, volt

######################################################################

data_count = 10000
HspiceSSH.repeat_count_change(data_count)

######################################################################

data1, label1, axis_name1, volt1 = generate_data(0.05)
data2, label2, axis_name2, volt2 = generate_data(0.7)
data = np.concatenate((data1, data2), axis=1)
label = label1
print(data.shape, label.shape)
print(label)

np.save('data.npy', data)
np.save('label.npy', label)

HspiceSSH.close()