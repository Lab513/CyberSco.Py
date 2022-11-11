'''
Init system
'''

from room_monitor.flask_app import *
from room_monitor.modules.misc_import import *

try:
    os.mkdir('/static/monitorings')
except:
    print('Probably, the folder monitorings still exists.. ')

@socketio.on('connect')
def test_connect(debug=[0]):
    '''
    Websocket connections
    Sending informations to the client
    '''
    if 0 in debug:
        print('In init_system.text_connect..')
        print('Connexion achieved !!!')
    emit('response', {'data': 'Connected'})
    # sending_ip()
