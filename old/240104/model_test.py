from keras.models import load_model
import data_unpack
import matplotlib.pyplot as plt
import HSPICE_SSH
import numpy as np

import tensorflow.python as tf

host = "103.218.163.120"
port = 3391
userId = "user_00"
password = "!!)#Kyung-Bae1103"

# 비교할 모델 불러오기
model = load_model(r'c:\temp\checkpoint')

index = 0

# 데이터 중 index번째를 불러온다.
data = data_unpack.get_data(r'c:\temp\0_data.npy')[index]
label = data_unpack.get_data(r'c:\temp\0_label.npy')[index]

# 정규화에 필요한 최댓값과 최솟값을 가져온다.
max_data = np.load(r'c:\temp\max_data.npy')
min_data = np.load(r'c:\temp\min_data.npy')
max_label = np.load(r'c:\temp\max_label.npy')
min_label = np.load(r'c:\temp\min_label.npy')

# 데이터를 정규화한다.
test_data = data[:, 1]
test_data = data_unpack.normalization(test_data, max_data, min_data)

# 모델에 데이터를 넣어 예측값을 얻는다.
predict_parameters = model.predict(np.array([test_data]))

# 예측값을 역정규화한다.
predict_parameters = data_unpack.denormalization(predict_parameters, max_label, min_label)

print(predict_parameters, test_data)

# 데이터를 그래프로 그린다.
plt.figure(figsize=(10, 10))
plt.subplot(2, 1, 1)
plt.plot(data[:, 0], data[:, 1], ':', label='original')
plt.xlabel('V (V)')
plt.ylabel('I (uA)')
plt.title(f'V-I curve: {predict_parameters[0]}')

# HSPICE 서버에 접속한다.
HSPICEssh = HSPICE_SSH.HSPICE_SSH(host, port, userId, password)

# 바꿀 파라미터들을 읽는다.
parameters = HSPICEssh.read_parameters(r'parameters.txt')

# HSPICE 파일의 경로를 설정한다.
HSPICEssh.model_file_path = r'/data2/Users/cws/3nm_NSFET_wBO_model.nmos'
HSPICEssh.sp_file_path = r'/data2/Users/cws/one_nmos.sp'

# 파라미터들을 바꾼다.
for i in range(len(parameters)):
    HSPICEssh.change_parameter_value(parameters[i].name, parameters[i].initial_value, predict_parameters[0][i])

# HSPICE를 작동시킨다.
data2 = HSPICEssh.get_hspice_data()

# 파라미터들을 원래대로 바꾼다.
for i in range(len(parameters)):
    HSPICEssh.change_parameter_value(parameters[i].name, predict_parameters[0][i], parameters[i].initial_value)

# 이미 그린 그래프 위에 그래프를 그린다.
plt.plot(data[:, 0], data2[:, 1], label='predicted')

# 두 그래프의 차이를 다른 그래프에 그린다.
plt.subplot(2, 1, 2)
plt.plot(data[:, 0], data[:, 1] - data2[:, 1])

plt.show()

HSPICEssh.close()