import SSHManager
import hspice_data_preprocessing
import json

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

    sp_file_path:str
    workspace_path:str

    def __init__(self, host:str=None, port:int=None, username:str=None, password:str=None):

        with open('settings.json', 'r') as f:
            settings = json.load(f)
        
        if host is None and port is None and username is None and password is None:
            super().__init__(*settings["default_server_info"].values())
            print("settings.json에 기록된 기본 서버 정보로 접속합니다.")
        else:
            super().__init__(host, port, username, password)
        
        try:
            self.sp_file_path = settings["default_sp_file_path"]
            self.workspace_path = settings["default_server_workspace_path"]
        except:
            pass
    
    def get_hspice_data(self, local_path:str=None):

        """
        HSPICE를 작동 시킨 후 데이터를 읽어와 반환한다.
        path가 None이면 서버에서 넘어온 데이터를 반환하고, path가 None이 아니면 해당 경로에 데이터를 저장한다.

        Args:
            local_path (str): 데이터를 저장할 경로

        Returns:
            str: HSPICE의 실행 결과
        """

        if local_path is None:
            return self.send_command(f'hspice {self.sp_file_path}')
        else:
            self.send_command(f'hspice {self.sp_file_path} > {self.workspace_path}/result.txt')
            self.get_file(f'{self.workspace_path}/result.txt', local_path)