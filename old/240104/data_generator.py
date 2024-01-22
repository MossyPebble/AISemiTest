import SSHManager
from hspice_data_preprocessing import data_extract
import numpy as np
import random, time
import pyautogui

host = "103.218.163.120"
port = 3391
userId = "user_00"
password = "!!)#Kyung-Bae1103"

HSPICEssh = SSHManager.SSHManager(host, port, userId, password)

def generator(*vars, save_path, data_size, batch_size=128):

    """
    vars에 맞게 데이터를 생성하는 함수. vars는 [변경할 변수1, 초기, 최종, 간격, 변수1초기값], [변경할 변수2, 초기, 최종, 간격, 변수2초기값]...의 형태로 입력한다.
    해당 간격들에 맞춰서 촘촘한 랜덤으로 데이터를 생성하고, 이를 save_path에 .npy로 저장한다.
    최종값은 초기값보다 커야 한다. 간격은 0이 될 수 없다.
    
    Args:
        *vars (list): 생성할 데이터의 변수들
        save_path (str): 데이터를 저장할 경로
        data_size (int): 생성할 데이터의 개수, 이 값은 batch_size의 배수여야 한다. 배수가 아니라면 남는 값은 버린다.
        batch_size (int): 저장할 단위
    """

    init_time = time.time()

    var_count_in_linespace = [int((vars[i][2] - vars[i][1]) / vars[i][3]) + 1 for i in range(len(vars))]
    var_names = [vars[i][0] for i in range(len(vars))]

    labels = np.zeros((batch_size, len(vars)))
    data = np.zeros((batch_size, ))

    count = int(data_size / batch_size)
    prev_var_values = [vars[i][4] for i in range(len(vars))]
    data = np.zeros((batch_size, ))
    # 데이터 저장 단위만큼 반복
    for i in range(count):
        time_start = time.time()
        # batch_size만큼 반복
        for j in range(batch_size):
            label = np.zeros((len(vars), ))
            # vars의 변수 개수 만큼 반복하며 랜덤으로 변수값을 선택 후 파일에 쓰기
            for k in range(len(vars)):
                random_chosen_var_value = vars[k][1] + random.randint(0, var_count_in_linespace[k] - 1) * vars[k][3]
                label[k] = random_chosen_var_value
                HSPICEssh.change_file_content(r'/data2/Users/cws/3nm_NSFET_wBO_model.nmos', r'{} =  {}'.format(var_names[k], prev_var_values[k]), r'{} =  {}'.format(var_names[k], random_chosen_var_value))
                prev_var_values[k] = random_chosen_var_value
            HSPICEssh.send_command(r'hspice -i /data2/Users/cws/one_nmos.sp > /data2/Users/cws/res.txt')
            HSPICEssh.get_file(r'/data2/Users/cws/res.txt', r'C:\temp\res.txt')
            time.sleep(0.05)
            temp_data = data_extract(r'C:\temp\res.txt')
            if data[0].shape != temp_data.shape:
                data = np.zeros((batch_size, *temp_data.shape))
            labels[j] = label
            data[j] = temp_data
        lpath = save_path + str(i) + '_label.npy'
        dpath = save_path + str(i) + '_data.npy'
        np.save(lpath, labels)
        np.save(dpath, data)
        print('')
        print('배치 {} 저장 완료'.format(i), '소요시간: ', time.time() - time_start)

    for i in range(len(vars)):
        HSPICEssh.change_file_content(r'/data2/Users/cws/3nm_NSFET_wBO_model.nmos', r'{} =  {}'.format(var_names[i], prev_var_values[i]), r'{} =  {}'.format(var_names[i], vars[i][4]))
    print('초기화 완료')

    print('총 소요시간: ', time.time() - init_time)
    pyautogui.alert('데이터 생성 완료')

def get_parameters():

    """
    parameters.txt에서 변수들을 읽어온다.
    이 함수가 리턴하는 값은 리스트이고, generator 함수는 리스트가 아닌 변수들을 입력 받으므로 이 함수의 리턴값을 *args로 넣어줘야 한다.

    Returns:
        parameters (list): [[변경할 변수1, 초기, 최종, 간격, 변수1초기값], [변경할 변수2, 초기, 최종, 간격, 변수2초기값]]...의 형태로 저장된 변수들
    """

    parameters = []
    with open('parameters.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.split(',')
            parameters.append([line[0], float(line[1]), float(line[2]), float(line[3]), float(line[4])])
    return parameters

paramters = get_parameters()

#--------------------------------------------------------------------------------------------------------

batch_size = 512
data_count = 20

#--------------------------------------------------------------------------------------------------------

generator(*paramters, save_path='C:\\temp\\', data_size=data_count * batch_size, batch_size=batch_size)

HSPICEssh.close()

"""
고쳐야할 점:

부동소숫점 문제 탓에 데이터 크기가 존나게 커지는 문제점이 있어용. 이거 해결 안하면 실속은 없는 데이터의 크기가 존나게 커질거에용.
아닌가? 짜피 float32로 잡았으니까 그 안에서 데이터 길이가 길든 말든 상관 없는거 아닌가? 그럼 이거 해결 안해도 되는거 아닌가? 모르게써용.
정밀도 탓에 float64로 바꿔야 할지도 모르겠어요.
"""