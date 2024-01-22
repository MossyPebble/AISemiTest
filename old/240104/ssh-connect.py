import paramiko
import time

host = "103.218.163.120"
port = 3391
userId = "user_00"
password = "!!)#Kyung-Bae1103"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, userId, password)

    sftp = ssh.open_sftp()
except:
    print("something wrong!")
    exit(1)

def get_file(src, dst):
    try:
        sftp.get(src, dst)
    except:
        print("something wrong!")
        exit(1)

def put_file(src, dst):
    try:
        sftp.put(src, dst)
    except:
        print("something wrong!")
        exit(1)

def send_command(cmd):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("리턴:", stdout.read().decode())
    except:
        print("something wrong!")
        exit(1)

# send_command(r'hspice -i /data2/Users/cws/2.NSFET_models(new)/2.Spice examples/2.inverter/one_nmos.sp > /data2/Users/cws/2.NSFET_models(new)/2.Spice examples/2.inverter/res.txt')
# time.sleep(0.1)
get_file(r'/data2/Users/cws/2.NSFET_models(new)/2.Spice examples/2.inverter/res.txt', r'C:\temp\res.txt')

sftp.close()
ssh.close()