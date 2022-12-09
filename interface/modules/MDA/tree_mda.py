'''
Tree MDA
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from interface.modules.MDA.params_mda import *
from interface.modules.protocoles.protocoles import *
from interface.modules.MDA.prepare_mda import *
from modules.mda import MDA
from interface.modules.connect.login import *


@socketio.on('launch_tree_protocol')
def launch_tree_protocol(curr_prot):
    '''
    Protocol from the tree
    '''
    global yaml_prot
    yaml_prot = curr_prot + '.yaml'
    print(Fore.GREEN + f"Launch the protocol"
                       f" {curr_prot} from the tree panel !!!!")
    print(Style.RESET_ALL)
    current_user.last_protocol = yaml_prot
    db.session.commit()


def launch_mda_tree(cam, debug=[1]):
    '''
    Launch the protocol from the Tree tool
    '''
    print(f'In launch_mda_tree, current_user is {current_user}')
    # MDA protocol with attached devices
    mda_protocol = MDA(ldevices=[ol, pr, cam, co, xc, ga, se],
                       user=current_user)
    mda_params(mda_protocol)
    ol.mod_afml = mda_protocol.mod0
    ol.ref_posz = ol.ask_zpos()
    if 1 in debug:
        print(f'in launch_mda_tree, yaml_prot is {yaml_prot}')
    # Protocol from the tree
    mda_protocol.load_tree_protocol(yaml_prot)
    # list id for goto
    save_list_id(mda_protocol)
    # launch the protocol
    mda_protocol.launch()
