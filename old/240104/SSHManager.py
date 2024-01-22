import paramiko

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

class SSHManager:
    
    """어떤 ssh 서버에 접속하고 그 안에서 명령어 실행, 파일 송수신을 담당하는 클래스"""

    def __init__(self, host, port, userId, password):

        """
        ssh 서버에 접속한다.

        Args:
            host (str): 접속할 ssh 서버의 주소
            port (int): 접속할 ssh 서버의 포트
            userId (str): ssh 서버에 접속할 계정
            password (str): ssh 서버에 접속할 계정의 비밀번호
        """

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, port, userId, password)
        self.sftp = self.ssh.open_sftp()

    def get_file(self, src, dst):

        """
        ssh 서버로부터 파일을 다운로드한다.

        Args:
            src (str): 다운로드할 파일의 경로
            dst (str): 다운로드한 파일을 저장할 경로
        """

        self.sftp.get(src, dst)

    def put_file(self, src, dst):

        """
        ssh 서버로 파일을 업로드한다.

        Args:
            src (str): 업로드할 파일의 경로
            dst (str): 업로드할 파일을 저장할 경로
        """

        self.sftp.put(src, dst)

    def send_command(self, cmd):

        """
        ssh 서버에 명령어를 전송한다.

        Args:
            cmd (str): 전송할 명령어

        Returns:
            str: 명령어의 실행 결과
        """

        print("명령어:", cmd)
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdout.read().decode()
    
    def change_file_content(self, file_path, old, new):

        """
        ssh 서버에 있는 파일의 내용을 변경한다.

        Args:
            file_path (str): 내용을 변경할 파일의 경로
            old (str): 변경할 내용 중 변경 전 내용
            new (str): 변경할 내용 중 변경 후 내용

        Returns:
            str: 명령어의 실행 결과
        """

        return self.send_command(f"sed -i \"s/{old}/{new}/g\" {file_path}")

    def close(self):
        self.sftp.close()
        self.ssh.close()

    def __del__(self):
        self.sftp.close()
        self.ssh.close()