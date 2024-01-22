import HSPICE_SSH
import numpy as np
from hspice_data_preprocessing import unit_remove, slice_data
import re

import torch
import torch.nn as nn

sp_file_path = r'/data2/Users/cws/one_nmos_test.sp'
server_info = HSPICE_SSH.get_server_info_from_txt(r'server_info.txt')

HspiceSSH = HSPICE_SSH.HSPICE_SSH(*server_info)
HspiceSSH.sp_file_path = sp_file_path

HspiceSSH.parameter_change('4.4511', '14m', '1.427n')