import HSPICE_SSH
import numpy as np
from hspice_data_preprocessing import unit_remove, slice_data
import re

import torch
import torch.nn as nn

import matplotlib.pyplot as plt

sp_file_path = r'/data2/Users/cws/one_nmos_test.sp'
server_info = HSPICE_SSH.get_server_info_from_txt(r'server_info.txt')

HspiceSSH = HSPICE_SSH.HSPICE_SSH(*server_info)
HspiceSSH.sp_file_path = sp_file_path

def one_data_extract(raw_data):

    # 줄바꿈 문자를 기준으로 슬라이싱 한다.
    lines = raw_data.split('\n')

    # 처음 '****** dc'가 등장하면, 이전의 값들을 모두 버린다.
    for i in range(len(lines)):
        if '****** dc' in lines[i]:
            lines = lines[i:]
            break
    
    one_epoch = slice_data(lines, 'x', 'y')
    temp_store = one_epoch.copy()

    # one_epoch에는 'x'와 'y'를 기준으로 자른 데이터, 즉, 그래프 또는 파라미터가 저장되어 있다. 이 데이터는 리스트 안의 리스트로 구성되어 있다.
    # 이 시점에서 one_epoch[0]은 대략 다음과 같은 형태이다. (다를 수 있음.)
    # 0번째 줄: (비어있음)
    # 1번째 줄:  volt       param     
    # 2번째 줄:            phig_change
    # 3번째 줄:  0.000e+00  0.000e+00
    # 4번째 줄:  ... (이하 끝까지 데이터)
    # 이 데이터를 가공해서 temp_lines에 append한다.
    # one_epoch의 모든 원소에 대해 3번째 부터 끝까지 데이터를 읽으며, 각 줄의 데이터 strip하고, 공백을 기준으로 split한다. 이후 unit_remove 함수를 적용한다. 이를 temp_lines에 저장한다.
    temp_lines = []
    for i in range(len(one_epoch)):
        one_epoch[i] = [[unit_remove(x) for x in re.split(r' +', line.strip())] for line in one_epoch[i][3:]]
        one_epoch[i] = np.array(one_epoch[i], dtype=np.float64)
        temp_lines += list(one_epoch[i].T)

    data = np.array(temp_lines, dtype=np.float64)

    # 각 lines의 0번째 줄은 불필요한 데이터이므로 고려하지 않는다.
    # 각 lines의 1, 2번째 줄은 해당 줄이 무엇을 의미하는지를 나타내므로 label에 저장한다. label은 모든 one_epoch에 대해 동일하므로, 이는 한 번만 저장한다.
    label = []
    for lines in temp_store:
        label.append((lines[1][:12].strip() + ' ' + lines[2][:12].strip()))
        label.append((lines[1][12:].strip() + ' ' + lines[2][12:].strip()))
    label = np.array(label)

    return data, label

def generate_one_data(drain_volt):

    HspiceSSH.drain_volt_change(drain_volt)

    data = HspiceSSH.send_command(f'hspice {HspiceSSH.sp_file_path}')
    data, axis_name = one_data_extract(data)

    parameter_index = [i for i in range(len(axis_name)) if '_change' in axis_name[i]]
    parameter_name = [axis_name[i].replace('_change', '').replace('param', '').strip() for i in parameter_index]

    label = np.zeros((len(parameter_name), ))

    for i, j in enumerate(parameter_index):
        label[i] = data[j, 0]

    for i, j in enumerate(parameter_index[::-1]):
        data = np.delete(data, j, axis=0)

    for i, j in enumerate(parameter_index[::-1]):
        axis_name = np.delete(axis_name, j)

    volt_index = [i for i in range(len(axis_name)) if 'volt' in axis_name[i]]
    volt = data[0, :].copy()
    for i, j in enumerate(volt_index[::-1]):
        data = np.delete(data, j, axis=0)
    for i, j in enumerate(volt_index[::-1]):
        axis_name = np.delete(axis_name, j)

    data = np.insert(data, 1, np.log(data[0, :]), axis=0)
    axis_name = np.insert(axis_name, 1, 'log')
    data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)

    return data, label, axis_name, volt

data1, label1, axis_name1, volt1 = generate_one_data(0.05)
data2, label2, axis_name2, volt2 = generate_one_data(0.7)
data = np.concatenate((data1, data2), axis=0)

label1 = list(label1)
label2 = list(label2)
for i in range(len(label1)):
    label1[i] = 'Linear Volt'+str(label1[i])
for i in range(len(label2)):
    label2[i] = 'Saturation Volt'+str(label2[i])
label = label1 + label2

volt = volt1.copy()

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.flatten = nn.Flatten()
        self.layer1 = None
        self.layer2 = nn.Linear(1000, 1000)
        self.layer3 = nn.Linear(1000, 3)

        torch.nn.init.xavier_normal_(self.layer2.weight)
        torch.nn.init.xavier_normal_(self.layer3.weight)

        self.activation = nn.ReLU()

    def forward(self, x):
        x = self.flatten(x)
        if self.layer1 == None:
            self.layer1 = nn.Linear(x.shape[1], 1000)
            torch.nn.init.xavier_normal_(self.layer1.weight)
        x = self.activation(self.layer1(x))
        x = self.activation(self.layer2(x))
        x = self.layer3(x)
        return x

model = torch.load(r'model.pt')

normal_data = np.load(r'normal_data.npy')
data = np.load(r'data.npy')

max_label = np.load(r'max_label.npy')
min_label = np.load(r'min_label.npy')

data_index = 0

print(normal_data[data_index].shape)

predict_paramter = model(torch.FloatTensor(np.array([normal_data[data_index]])))
predict_paramter = predict_paramter.detach().numpy()
predict_paramter = predict_paramter*(max_label-min_label) + min_label
predict_paramter = predict_paramter[0] / 1e+9

HspiceSSH.parameter_change(*predict_paramter)
res = HspiceSSH.get_hspice_data()
res, _ = one_data_extract(res)

volt = volt / 1e+9

for i in range(len(res)):
    plt.subplt(2, 3, i+1)
    plt.plot(volt, res[i, :])
    plt.plot(volt, data[i, :], '--')
    plt.title(label[i])