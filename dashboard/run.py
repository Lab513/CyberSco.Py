#!/usr/bin/env python
# encoding: utf-8

"""

CyberScoPy Dashboard

python -m dashboard.run

"""

from dashboard.modules.server import *
from modules.util_misc import *
##
from dashboard.flask_app import *
##
from dashboard.modules.init.init_params import *
from dashboard.modules.init.init_paths import *
from dashboard.modules.init.init_system import *
##
from dashboard.modules.connect.login import *
from dashboard.modules.connect.auth import *
from dashboard.modules.connect.forms import *

from dashboard.modules.booking import *

from dashboard.modules.page_interf.index import *



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
