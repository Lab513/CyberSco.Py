'''
Server
'''

from dashboard.modules.util_interf import find_platform
platf = find_platform()

debug_server = False

if platf == 'win':
    import gevent as server
    from gevent import monkey
    monkey.patch_all()
    if debug_server:
        print('the current plateform is Windows')
        print('Using gevent')
else:
    import eventlet as server
    server.monkey_patch()
    if debug_server:
        print('Using eventlet')

from dashboard.modules.util_interf import launch_browser, init
from modules.util_misc import *
import webbrowser
import threading
import socket
from dashboard.flask_app import *
from dashboard.modules.misc_import import *
from dashboard.modules.init.init_paths import *

def shutdown_server():
    '''
    Quit the application
    called by method shutdown() (hereunder)
    '''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown')
def shutdown():
    '''
    Shutting down the server.
    '''
    shutdown_server()

    return 'Server shutting down...'


def message_at_beginning(host, port, debug_addr_server=False):
    '''
    '''
    print(Fore.YELLOW + """
                ***********************************

                    Dashboard for CyberSco.py

                ***********************************
    """)


    if debug_addr_server:
        print(f'address: {host}:{port}')


def set_IP():
    '''
    Savec the IP addresses with corresponding port..
    '''
    ip = socket.gethostbyname(socket.gethostname())
    # address for main dashboard
    dic_server = {'host': ip, 'port': 2001}
    with open(settings_folder / 'server_address.yaml', 'w') as f_w:
        yaml.dump(dic_server, f_w)         #
