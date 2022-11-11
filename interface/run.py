#!/usr/bin/env python
# encoding: utf-8

"""

CyberScoPy

python -m interface.run

"""


from interface.modules.server import *
from modules.util_misc import *
##
from interface.flask_app import *

## Protocols

from interface.modules.protocoles.protocoles import *

## Initialisations

from interface.modules.init.init_params import *
from interface.modules.init.init_paths import *
from interface.modules.init.init_devices import *
from interface.modules.init.init_system import *

## Devices

from interface.modules.setting_channels import *
from interface.modules.AF import *
from interface.modules.camera import *
from interface.modules.valves import *
from interface.modules.objective import *
from interface.modules.move_xyz import *
from interface.modules.DMD.dmd import *

## Tools

from interface.modules.tools.sweep_chip import *
from interface.modules.tools.snap_and_live import *

## Machine Learning

from interface.modules.ML.models import *

## MDAs

from interface.modules.MDA.predefined_mda import *
from interface.modules.MDA.tree_mda import *
from interface.modules.MDA.infos_mda import *
from interface.modules.MDA.launch_mda import *

## Login

from interface.modules.connect.login import *
from interface.modules.connect.auth import *
from interface.modules.connect.forms import *

from interface.modules.page_interf.index import *


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
