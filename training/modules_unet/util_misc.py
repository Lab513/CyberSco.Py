import os
import pathlib
import shutil as sh
import time
import tensorflow as tf
from tensorflow.python.client import device_lib

def copy_dir(src, dst):
    '''
    '''
    dst.mkdir(parents=True, exist_ok=True)
    for item in os.listdir(src):
        s = src / item
        d = dst / item
        if s.is_dir():
            copy_dir(s, d)
        else:
            sh.copy2(str(s), str(d))

def get_name_gpu(s):
    '''
    '''
    sspl = s.split(',')
    for elem in sspl:
        print('##### elem is ',elem)
        if 'name' in elem:
            return elem.split(':')[1]
    return 'none'

def get_computing_infos():
    '''
    '''
    try:
        dl = device_lib.list_local_devices()[2]
        gpu_id = get_name_gpu(dl.physical_device_desc)
        gpu_mem = str(round(int(dl.memory_limit)/1e9,2)) + ' MB'
        soft_hard_infos = { 'id': gpu_id, 'mem': gpu_mem, 'tf_version': tf.__version__ }
        return soft_hard_infos
    except:
        print('issue with computing_infos')

def timing(func):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        func(*args, **kwargs)
        t1 = time.time()
        time_tot = round((t1-t0)/60,2)
        args[0].time_tot = time_tot  # time_tot on self
        print(f'time elapsed is {time_tot} min')
    return wrapper
