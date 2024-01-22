SSHManager.py는 그냥 paramiko를 더 단순화 시켜 제가 사용하기 용이하게 만든 모듈입니다.

import SSHManager로 원하는 코드에 모듈을 포함시키면, class1 = SSHManager.SSHManager(주소, 포트, 아이디, 비밀번호)로 클래스를 만들고, 
class1.get_file(서버 파일 경로, 로컬 저장 위치)와 같이 사용하면 됩니다.

이런 식으로 만들어진 이유는 혹시 추후에 한 코드 내에서 여러 SSH 서버를 한번에 이용하거나 한 SSH 서버를 여러 사용자로 이용할 수 있어서 입니다.

예를 들어, class1 = SSHManager.SSHManager(주소1, 포트1, 아이디1, 비밀번호1), class2 = SSHManager.SSHManager(주소2, 포트2, 아이디2, 비밀번호2)와
같은 방식입니다.

위 예에서는 class1으로 서버 1번과의 통신을, class2로 서버 2번과의 통신을 제어합니다.

class1.get_file과, class2.put_flie을 함께 사용하면 서버1의 파일을 서버2로 옮길 수 있을 것입니다.

######################################################################################################################

HSPICE_SSH.py는 SSHManager.py와 hspice_data_preprocessing.py를 합쳐 더 간단하게 만든 것입니다.

HSPICE_SSH.py는 SSHManager.py의 클래스를 상속받아 만들어진 HSPICE_SSH.HSPICE_SSH 클래스가 핵심입니다.

이를 코드 내에서 사용하려면 import HSPICE_SSH로 모듈을 포함시키고, class1 = HSPICE_SSH.HSPICE_SSH(주소, 포트, 아이디, 비밀번호)로
클래스를 만들고, class1.get_file(서버 파일 경로, 로컬 저장 위치)와 같이 사용하면 됩니다.

class1.get_hspice_data(서버 파일 경로, 로컬 저장 위치)외에는 전부 반복을 조금 줄여줄 뿐인 코드이므로 이에 대해서만 설명합니다.
(HSPICE_SSH.HSPICE_SSH에 포함된 get_hspice_data 이외의 함수들은 거의 간단합니다.)

get_hspice_data는 아래와 같은 순서로 작동합니다. (self는 class1을 의미합니다.)
1. self.sp_file_path에 작동시키고 싶은 .sp파일의 서버 경로를 저장합니다.
2. 상속받은 함수 중 self.send_command("hspice " + self.sp_file_path)를 실행합니다.
   send_command 함수 자체가 명령문을 실행하고 그 결과를 반환하는 함수입니다.
   그래서 위 코드는 서버에서 미리 저장해둔 경로의 .sp파일을 실행하고 그 결과를 반환합니다.
   그래서, self.send_command를 사용하는 줄은, data = self.send_command("hspice " + self.sp_file_path)와 같이 사용되어야 합니다.
3. hspice_data_preprocessing.data_extract(data)를 실행합니다.
   이는 data에서 필요한 데이터만 추출하여 반환합니다.
   그래서, data_extract를 사용하는 줄은, data = hspice_data_preprocessing.data_extract(data)와 같이 사용되어야 합니다.
4. data를 return합니다.

그러면, data = class1.get_hspice_data(서버 파일 경로, 로컬 저장 위치)와 같이 사용할 때, data에는 정제된 데이터가 저장됩니다.

아마 사용하실 때, 자신만의 get_hspice_data를 만들어 사용하셔야 할 겁니다. 
get_hspice_data의 내용 중 hspice_data_preprocessing.data_extract만 자신의 코드에 맞게 수정하시면 됩니다.

저는 data_extract에 monte carlo index대로 잘라서 type가 numpy.ndarray인 data를 반환하도록 만들었습니다.
이를 구현하기 위해 data_extract에는 수많은 반복문이 사용되었고, 제가 구현할 수 있는 한계로 현재 성능 면에서 그리 빠르지 않습니다.

자신만의 get_hspice_data를 만드는 방법을 간단히 설명하자면, 아래와 같습니다.
1. 자신이 실행시키고 싶은 .sp파일의 결과문 형식을 파악합니다.
2. 해당 결과문을 어떤 방식으로 반복하여 잘라야 올바른 데이터를 얻을 수 있는지 생각합니다.
3. 그 방식대로 자신만의 hspice_data_preprocessing.data_extract를 만듭니다.
4. 3.의 함수를 포함하는 get_hspice_data를 만듭니다.

예를 들어, data_pre가 hspice_data_preprocessing.data_extract의 역할을 하는 함수라고 하면,
def get_hspice_data(self, sp_file_path, local_file_path):
    data = self.send_command("hspice " + sp_file_path)
    data = data_pre(data)
    return data
와 같이 만들고 사용하면 됩니다. (클래스 내부가 아니라면, self가 필요 없습니다.)

######################################################################################################################

마지막으로, 저는 data_generator.py를 데이터를 생성하는 main.py의 역할을 하는 코드로 사용하고 있습니다만, 
저는 마지막 세부 조정을 포함할 목적으로 data_generator.py를 사용하고 있기 때문에 이는 중요하지 않습니다.

data_generator.py의 내용을 보면 data_count와 seed라는 변수값을 조정할 수 있는데,
data_count는 한번에 생성할 데이터의 개수를, seed는 hspice내에서 monte carlo방식으로 데이터를 생성할 때 사용되는 seed값을 변경합니다.

data_count와 seed값을 변경하는 방식은 모두 class1.change_file_content에 의해 이루어집니다.
이 또한 코드를 읽어보시면 쉽게 이해하실 수 있을 것입니다.