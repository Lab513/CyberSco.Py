'''
Utilities for the dashboard
'''

import os
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join
import glob
import shutil as sh
import subprocess
from sys import platform as _platform

def find_platform(debug=[]):
    '''
    Find which platform is currently used
    '''
    if 0 in debug:
        print('platform is ', _platform)
    if _platform == "linux" or _platform == "linux2":
        platf = 'lin'
    elif _platform == "darwin":
        platf = 'mac'
    elif _platform == "win32":
        platf = 'win'
    return platf


def try_nb(s):
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def translate_params(p):
    '''
    '''
    print(f"##### p is {p}")
    if ':' in p:
        ps = p.split(':')
        if ',' in ps[1]:
            return {ps[0]: '[{}]'.format(ps[1])}             # list case
        else:
            if '&' in ps[1]:
                if ps[0] == 'select_model':
                    part = ps[1].split('&')
                    dic_mod_with_event = {'model': part[0],
                                           'model_events': part[1]}
                    print(f"dic is {dic_mod_with_event} ")
                    return dic_mod_with_event
            else:
                return {ps[0]: try_nb(ps[1])}              # return key/value
    else:
        return {p: True}                                    # return a boolean


def clean_dir(dir):
    '''
    Clear folder dir
    '''
    try:
        for f in glob.glob(opj(dir, '*.*')):
            os.remove(f)
    except:
        print(f"can't clean {dir}")


def open_folder(path):
    '''
    Open folder
    '''
    if platf == 'win':
        os.startfile(path)
    elif platf == 'mac':
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def rm_make_upload(config, debug=[]):
    '''
    '''
    upload = 'dashboard/upload'
    try:
        sh.rmtree(upload)                  # Reinitializes the upload folder
    except:
        print(f"cannot find {upload}")
    os.mkdir(upload)
    print('upload folder done.. ')


def init(config):
    '''
    Prepare dashboard.
    '''
    rm_make_upload(config)


def save_with_date(dest='previous_proc', debug=0):
    '''
    Save the processing with full structure in previous_proc
    Folders saved are Processings and Controls
    File saved is list_proc.json
    '''
    now = dt.now()
    path_static = opj(os.getcwd(), 'static')
    dproc = opj(path_static, 'processings')
    dctrl = opj(path_static, 'controls')
    dlist_proc = opj(path_static, 'list_proc.json')
    dest_path = opj(path_static, dest)
    try:
        os.mkdir(dest_path)                    # path for previous processings
        print("########## made new dest_path !!!! ")
    except:
        print("Possible issue with previous_proc")
    #path_static = opj(os.getcwd(), 'static')
    date = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"
    ppdate = opj(dest_path, date)
    try:
        sh.copytree(dproc, opj(ppdate,'processings'))
    except:
        print("yet existing folder")
    if debug > 0:
        print("copied dproc")
    try:
        sh.copytree(dctrl, opj(ppdate,'controls'))
    except:
        print("yet existing folder")
    try:
        sh.copy(dlist_proc, ppdate)
    except:
        print("yet existing file")
    if debug > 0:
        print("copied dlist_proc")
    sh.make_archive(ppdate, "zip", ppdate) # Zip the archive
    return ppdate + '.zip'


def find_chrome_path(platf):
    '''
    '''
    # MacOS
    if platf == 'mac':
        chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    # Linux
    elif platf == 'lin':
        chrome_path = '/usr/bin/google-chrome %s'
    else:
        chrome_path = False
    return chrome_path


def launch_browser(port, host, platf, debug=[]):
    '''
    Launch Chrome navigator
    '''
    if 0 in debug:
        print('Launch the browser..')
    chrome_path = find_chrome_path(platf)
    url = f"http://{host}:{port}"
    if platf != 'win':
        b = webbrowser.get(chrome_path)
        # open a page in the browser.
        threading.Timer(1.25, lambda: b.open_new(url)).start()
    else:
        try:
            if 1 in debug:
                print('using first path')
            subprocess.Popen(f'"C:\Program Files\Google\Chrome\Application\chrome.exe" {url}')
        except:
            print('using second path')
            subprocess.Popen(f'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" {url}')
