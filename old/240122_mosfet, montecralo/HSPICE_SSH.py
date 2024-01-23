import SSHManager
import hspice_data_preprocessing

def get_server_info_from_txt(path):

    """
    서버 정보가 저장된 텍스트 파일을 읽어와 반환한다. 텍스트 파일에는 서버의 주소, 포트, 계정, 비밀번호가 줄바꿈으로 구분되어 저장되어 있어야 한다.

    Args:
        path (str): 서버 정보가 저장된 텍스트 파일의 경로

    Returns:
        (list): 서버 정보가 저장된 리스트
    """

    with open(path, 'r') as f:
        server_info = [line.strip() for line in f.readlines()]
    
    return server_info

class HSPICE_SSH(SSHManager.SSHManager):

    """SSHManager를 이용해 HSPICE 작동을 더 손쉽게 하기 위해 만든 클래스."""

    model_file_path:str
    sp_file_path:str
    
    def get_hspice_data(self):

        """
        HSPICE를 작동 시킨 후 데이터를 읽어와 반환한다.

        Returns:
            data (numpy.ndarray): 데이터
            label (numpy.ndarray): 데이터의 라벨
        """

        data = self.send_command(f'hspice {self.sp_file_path}')
        return hspice_data_preprocessing.data_extract(data)
    
    def repeat_count_change(self, repeat_count):

        """
        HSPICE를 작동시킬 때, monte carlo 횟수를 변경한다.

        Args:
            repeat_count (int): 반복 횟수
        """

        r = open('count.txt', 'r')
        record = r.read()
        self.change_file_content(self.sp_file_path, f'monte={record}', f'monte={repeat_count}')
        r.close()
        r = open('count.txt', 'w')
        r.write(str(repeat_count))
        r.close()

    def seed_change(self, seed):

        """
        HSPICE를 작동시킬 때, seed를 변경한다.

        Args:
            seed (int): seed
        """

        r = open('seed.txt', 'r')
        record = r.read()
        self.change_file_content(self.sp_file_path, f'seed={record}', f'seed={seed}')
        r.close()
        r = open('seed.txt', 'w')
        r.write(str(seed))
        r.close()

    def drain_volt_change(self, volt):

        """
        HSPICE를 작동시킬 때, seed를 변경한다.

        Args:
            seed (int): seed
        """

        r = open('drain_volt.txt', 'r')
        record = r.read()
        self.change_file_content(self.sp_file_path, f'd gnd {record}', f'd gnd {volt}')
        r.close()
        r = open('drain_volt.txt', 'w')
        r.write(str(volt))
        r.close()   

    def parameter_change(self, *value):

        """
        HSPICE를 작동시킬 때, 파라미터를 변경한다.
        """

        r = open('parameter.txt', 'r')
        record = r.readlines()
        if len(record) != len(value):
            raise ValueError('The number of parameters and values does not match.')
        for i in range(len(record)):
            record[i] = record[i].strip().split(',')
        r.close()
        
        content=''
        for i in range(len(record)):
            content += f'{record[i][0]},{value[i]}\n'
            self.change_file_content(self.sp_file_path, f'{record[i][0]}_change={record[i][1]}', f'{record[i][0]}_change={value[i]}')
        w = open('parameter.txt', 'w')
        w.write(content)
        w.close()