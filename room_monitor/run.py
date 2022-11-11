#!/usr/bin/env python
# encoding: utf-8

"""

CyberScoPy Room monitoring server..

python -m room_monitor.run

"""

from room_monitor.modules.server import *
from modules.util_misc import *
##
from room_monitor.flask_app import *
##
from room_monitor.modules.init.init_params import *
from room_monitor.modules.init.init_paths import *
from room_monitor.modules.init.init_system import *

from room_monitor.modules.page_interf.index import *


if __name__ == '__main__':

    set_IP()
    init(app.config)      # clean last processings and upload folders
    with open(settings_folder / 'server_address.yaml') as f_r:
        addr = yaml.load(f_r, Loader=yaml.FullLoader)
    PORT = addr['port']
    HOST = addr['host'] if platf == 'win' else '0.0.0.0'
    launch_browser(PORT, HOST, platf)
    message_at_beginning(HOST, PORT)
    print(Style.RESET_ALL)
    app.env = "development"

    socketio.run(app, port=PORT, host=HOST)
