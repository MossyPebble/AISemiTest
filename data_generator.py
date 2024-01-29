from HSPICE_SSH import HSPICE_SSH
import os, re, csv
import numpy as np
from hspice_data_preprocessing import unit_remove

def slice_list(data:list, from_element:str, to_element:str):
    
   """
   리스트에서 from_element와 to_element 사이의 데이터를 슬라이싱하는 함수. from, to_element의 줄은 포함하지 않는다.
   모든 from_element와 to_element를 찾아 그 대상으로 한다.
   
   Args:
      data (list): 슬라이싱할 데이터
      from_element (str): 슬라이싱할 데이터의 시작점
      to_element (str): 슬라이싱할 데이터의 끝점

   Returns:
      list: 슬라이싱된 데이터
   """

   res = []

   try:
      while True:
         res.append(data[data.index(from_element) + 1:data.index(to_element)])
         data = data[data.index(to_element) + 1:]
   except ValueError:
      return res


# result.txt가 현재 프로그램이 작동하는 경로에 존재한다면, 그걸 불러온다.
# 그렇지 않다면, HSPICE를 작동시킨다. 그 후 result.txt를 불러온다.
current_directory = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(current_directory + "/result.txt"):
   Hspice_SSH = HSPICE_SSH()
   Hspice_SSH.send_command(f'hspice {Hspice_SSH.sp_file_path} > result.txt')
   Hspice_SSH.get_file(r'/data2/Users/cws/result.txt', current_directory)
   Hspice_SSH.close()

with open("result.txt", 'r') as f:
   data = f.readlines()
   

# 아래 두 과정이 완료되면, data와 index는 같은 길이를 가지고 서로 대응되는 순서를 가진다.
# data에 존재하는 모든 index가 포함된 줄을 찾아 그 줄에 적한 index를 저장한다.
index = []
for i in range(len(data)):
   if 'index =' in data[i]:
      tempindex = data[i].find('index =')
      index.append(int(data[i][tempindex+len('index ='):].replace('***', '').strip()))

# x, y를 기준으로 잘라낸다.
data = slice_list(data, 'x\n', 'y\n')


# data를 분해한다. 이 과정은 함수로 대체하는 것이 좋아 보임.
# 지금, data는 2차원 리스트이고, 첫 차원은 인덱스로 구분, 둘째 차원은 각 인덱스 안의 데이터이다.
# 해야 하는 일은, 각 인덱스 안의 데이터를 구분하는 것이다.
for i, j in enumerate(data):
   for k, l in enumerate(j):
      data[i][k] = re.split(' +', l.strip()) # 정규식으로 공백을 기준으로 잘라낸다.


# 위 과정을 모두 거친 현재 data[0]:str의 모습은 대략 다음과 같다. (다를 수 있음)
# ['']                              (본래 공백인 줄임)
# ['time', 'voltage', 'current']
# ['vg', 'mn1']
# ['0.', '0.', '16.9736u']
#       ...
# 위 예시에서는 줄이 3개지만, 데이터에 따라 늘어나거나 줄어들 수 있다.
# 이를 csv로 저장한다. data는 현재 3차원 리스트이므로, 이를 2차원 리스트로 각각 분리해 저장한다.
with open('result.csv', 'w', newline='') as f:
   for i in data:
      writer = csv.writer(f)
      writer.writerows(i)
      f.write('\n')

# index를 저장한다.
with open('index.csv', 'w', newline='') as f:
   writer = csv.writer(f)
   writer.writerow(index)
   f.write('\n')

# # data에 저장된 str형식의 원소들을 float형식으로 변환한다. 이 과정에서 각 원소의 단위가 없어진다.
# # 부동소수점 문제를 해결하기 위해 모든 원소에 1e+9를 곱한다.
# for i, j in enumerate(data):
#    data[i] = j[3:]
# for i, j in enumerate(data):
#    for k, l in enumerate(j):
#       for m, n in enumerate(l):
#          data[i][k][m] = float(unit_remove(n))

# #위 두 저장을 numpy 형식으로 저장한다.
# data = np.array(data, dtype=np.float64)
# index = np.array(index, dtype=int)

# print(data.shape, index.shape)
# np.save('result.npy', data)
# np.save('index.npy', np.array(index, dtype=int))