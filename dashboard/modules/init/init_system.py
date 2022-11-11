'''
Init system
'''

from dashboard.flask_app import *
from dashboard.modules.misc_import import *
# import socket

addr_book_infos = opj('dashboard','settings','book_infos.yaml')
addr_list_equip = opj('dashboard','settings','list_equip.yaml')

# def sending_ip():
#     '''
#     Send the Ip
#     '''
#     global ip
#     ip = socket.gethostbyname(socket.gethostname())
#     emit('ip_used', ip, broadcast=True)

def send_list_equip():
    '''
    '''
    with open(addr_list_equip) as f_r:
        list_equip = yaml.load(f_r, Loader=yaml.FullLoader)
    print(f'In run, list_equip is { list_equip }')
    emit('list_equip', json.dumps(list_equip))

@socketio.on('connect')
def test_connect(debug=[0]):
    '''
    Websocket connections
    Sending informations to the client
    '''
    send_list_equip()
    if 0 in debug:
        print('In init_system.text_connect..')
        print('Connexion achieved !!!')
    emit('response', {'data': 'Connected'})
    # sending_ip()
