from interface.flask_app import *
from interface.modules.misc_import import *


def save_list_id(mda_protocol):
    '''
    Save the list of the ids for predefined MDAs
    '''
    print(f'mda_protocol.lpos_id {mda_protocol.lpos_id} ')
    all_id = opj('mda_temp', 'mda_init', 'lpos_id.yaml')
    with open(all_id, "w") as f_w:
        yaml.dump(mda_protocol.lpos_id, f_w)
