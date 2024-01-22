import numpy as np
import re

"""전처리 자체는 짧으니까 그냥 str이나 list로 받아서 처리하는게 나을듯"""

def unit_remove(data):

    """데이터에서 단위를 제거하는 함수"""

    if 'm' in data:
        data = data.replace('m', ' ')
        data = float(data) * 1e-3
    elif 'n' in data:
        data = data.replace('n', ' ')
        data = float(data) * 1e-9
    elif 'u' in data:
        data = data.replace('u', ' ')
        data = float(data) * 1e-6
    return data

def slice_data(data, from_element, to_element):
    
    """데이터를 슬라이싱하는 함수. from, to_element의 줄은 포함하지 않는다."""

    res = []

    try:
        while True:
            res.append(data[data.index(from_element) + 1:data.index(to_element)])
            data = data[data.index(to_element) + 1:]
    except ValueError:
        return res
    
def data_extract(raw_data):
    
    """
    HSPICE에서 추출한 데이터를 numpy array로 변환하는 함수.
    파라미터의 이름은 파라미터_change라고 붙여야 한다.
    data의 shape가 나타내는 의미느 다음과 같다. (데이터의 개수, 파라미터의 개수, 데이터의 길이)
    label의 shape가 나타내는 의미는 다음과 같다. (파라미터의 개수,)
    현재 굉장비 비효율적으로 작성되어 있다. 수정이 필요하지만, 한 두번만 작동시키면 되는 코드이므로 후순위로 미룬다.

    Args:
        raw_data (str): HSPICE에서 추출한 데이터

    Returns:
        data (numpy.ndarray): 변환된 데이터
        label (numpy.ndarray): 데이터의 라벨
    """

    data = []
    label = []    

    # 줄바꿈 문자를 기준으로 슬라이싱 한다.
    lines = raw_data.split('\n')

    # 처음 '*** monte carlo'가 등장하면, 이전의 값들을 모두 버린다.
    for i in range(len(lines)):
        if '*** monte carlo' in lines[i]:
            lines = lines[i:]
            break

    # 다음 '*** monte carlo'가 등장할때까지의 줄 수를 센다. 이 줄 수를 line_count에 저장한다.
    line_count = 0
    for i in range(1, len(lines)):
        if '*** monte carlo' in lines[i]:
            line_count = i
            break
    
    # 아래 과정을 모든 monte carlo index에 대해 반복한다.
    # 반복이 끝나는 시점은 lines의 첫번째 줄이 '*** monte carlo'를 포함하지 않을 때이다. 이유는 매 monte carlo index를 읽을 때 마다 이전의 데이터를 모두 버리기 때문이다. 반복을 시작해야 하는 시점에서 lines의 첫번째 줄이 해당 내용이 아니면, 이는 데이터를 모두 읽었다는 의미이다.
    temp_store = []
    while '*** monte carlo' in lines[0]:
        monte_carlo = []
        temp_lines = []

        # 한 개의 monte_carlo에 해당하는 데이터를 추출한다. 이 값을 monte_carlo에 저장한다.
        monte_carlo = lines[:line_count]

        # monte_carlo의 줄을 읽으며 'x'인 줄과 'y'인 줄 사이의 데이터로 monte_carlo를 구성한다. 이 값을 monte_carlo에 저장한다.
        monte_carlo = slice_data(monte_carlo, 'x', 'y')
        temp_store = monte_carlo.copy()

        # monte_carlo에는 'x'와 'y'를 기준으로 자른 데이터, 즉, 그래프 또는 파라미터가 저장되어 있다. 이 데이터는 리스트 안의 리스트로 구성되어 있다.
        # 이 시점에서 monte_carlo[0]은 대략 다음과 같은 형태이다. (다를 수 있음.)
        # 0번째 줄: (비어있음)
        # 1번째 줄:  volt       param     
        # 2번째 줄:            phig_change
        # 3번째 줄:  0.000e+00  0.000e+00
        # 4번째 줄:  ... (이하 끝까지 데이터)
        # 이 데이터를 가공해서 temp_lines에 append한다.
        # monte_carlo의 모든 원소에 대해 3번째 부터 끝까지 데이터를 읽으며, 각 줄의 데이터 strip하고, 공백을 기준으로 split한다. 이후 unit_remove 함수를 적용한다. 이를 temp_lines에 저장한다.
        for i in range(len(monte_carlo)):
            monte_carlo[i] = [[unit_remove(x) for x in re.split(r' +', line.strip())] for line in monte_carlo[i][3:]]
            monte_carlo[i] = np.array(monte_carlo[i], dtype=np.float64)
            temp_lines += list(monte_carlo[i].T)

        # 이후 위 과정을 반복한다. 완성된 monte_carlo와 label은 아래와 같은 형태이다. (다를 수 있음.)
        # label: ['volt', 'current ml', 'volt', 'param phig_change']
        # monte_carlo: array([[value1, value2, ...], (volt)
        #                     [value1, value2, ...], (current ml)
        #                     [value1, value2, ...], (volt)
        #                     [value1, value2, ...]]) (param phig_change)
        # 이를 data에 append한다.
        data.append(temp_lines)

        # 이후 다음 monte_carlo를 읽기 위해 lines를 업데이트한다.
        lines = lines[line_count:]

    # data를 numpy array로 변환한다.
    data = np.array(data)

    # 각 lines의 0번째 줄은 불필요한 데이터이므로 고려하지 않는다.
    # 각 lines의 1, 2번째 줄은 해당 줄이 무엇을 의미하는지를 나타내므로 label에 저장한다. label은 모든 monte_carlo에 대해 동일하므로, 이는 한 번만 저장한다.
    for lines in temp_store:
        label.append((lines[1][:12].strip() + ' ' + lines[2][:12].strip()))
        label.append((lines[1][12:].strip() + ' ' + lines[2][12:].strip()))
    label = np.array(label)

    return data, label