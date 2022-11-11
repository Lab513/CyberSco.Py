'''
Autofocus
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from interface.modules.init.init_paths import *


def save_offset_and_posz():
    '''
    Save the offset, the z after autofocus and z at focus
    '''
    zpos = ol.ask_zpos()
    print(f'zpos : {zpos} type(zpos) {type(zpos)}, '
          'ol.offset : {ol.offset} type(ol.offset) {type(ol.offset)} ')
    dic_z_offset = {'z': zpos,
                    'offset': ol.offset,
                    'zfocus': zpos + int(ol.offset),
                    'ref_posz': ol.ref_posz}
    print(f'** dic_z_offset is {dic_z_offset} ')
    with open('interface/settings/offset_and_posz.yaml', 'w') as f_w:
        # save the offset, the autofocus
        # position and the focused position in yaml
        yaml.dump(dic_z_offset, f_w)


@socketio.on('update_af')
def update_af(node_id, debug=[]):
    '''
    update the pos with id : node_id
    '''
    print(f'######### Updating the offset for the ZDC AF from the tree !!!!')
    if 1 in debug:
        print(f'node_id is {node_id} ')
    posz = ol.ask_zpos()
    ol.calc_offset()
    ol.set_zpos(posz)
    print(f'Offset for id {node_id} is {ol.offset} ')
    # refresh the infos in the tree
    emit('update_af_infos', f'{node_id};{str(ol.offset)};{ol.objective}' )


@socketio.on('change_AF')
def change_AF(af):
    '''
    Choose the aufocus method
    '''
    # kind of autofocus used.. set from interface
    global kind_focus
    print(f'Using the AF method {af}')
    kind_focus = af


@socketio.on('offset')
def calc_offset(msg):
    '''
    Find the offset
    '''
    ol.calc_offset()      # calculation of the offset
    save_offset_and_posz()  # save the offset and pos z after autofocus in yaml
    sending_posz()           # position after autofocus
    emit('offset', ol.offset, broadcast=True)


@socketio.on('reset_offset')
def reset_offset(msg):
    '''
    recalculate the offset
    '''
    posz = ol.ask_zpos()
    ol.offset = posz - ol.af_pos     # Adapting the offset position
    print(Fore.YELLOW + f'offset is {ol.offset}')
    print(Style.RESET_ALL)
    emit('offset', ol.offset, broadcast=True)


#  refocusing
@socketio.on('refocus')
def refocus(msg):
    '''
    Refocus using the offset
    '''
    ol.refocus()            # go back to focused position
    sending_posz()          # send pos z to the interface


#  refocusing
@socketio.on('access_back')
def access_back(msg):
    '''
    Give access back to the manual focus
    '''
    ol.give_access_back()             # go back to focused position


def reload_offset(debug=[]):
    '''
    '''
    addr_offset_and_posz = settings_folder / 'offset_and_posz.yaml'
    # offset and z position
    with open(addr_offset_and_posz) as f_r:
        dic_zoff = yaml.load(f_r)
        ol.offset = dic_zoff['offset']         # offset
        ol.ref_posz = dic_zoff['ref_posz']     # reference position for refocus
        ol.set_lim_af_sup_and_inf()                  # set excursion limits
    if 1 in debug:
        print(f'dic_zoff is {dic_zoff}')


@socketio.on('save_z_pos')            # move fast on the z axis
def save_z_pos(zpos):
    '''
    Save z position
    '''
    addr_posz = settings_folder / 'posz.yaml'
    with open(addr_posz, 'w') as f_w:
        yaml.dump(zpos, f_w)
    ol.ref_posz = zpos           # save ol.ref_posz for Autofocus
    # arbitrary value for offset for prog to work with AF_ML
    ol.offset = 10
    emit('saved_z', f'{zpos}', broadcast=True)
