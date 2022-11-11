'''
Move x,y
'''

from interface.flask_app import *
from interface.modules.init.init_devices import *
from interface.modules.misc_import import *
from interface.modules.init.init_params import *

@socketio.on('fast_xy_pos')                     # move fast to x,y
def fast_xy_pos(xypos):
    '''
    fast_xy_pos
    '''
    dic_pos_xy = json.loads(xypos)
    print(f'dic_pos_xy is {dic_pos_xy}')
    x, y = float(dic_pos_xy['x']), float(dic_pos_xy['y'])
    pr.absolute_move_to(x, y)
    sending_pos()


@socketio.on('set_stepxy')                          # step xy
def set_stepxy(stepxy):
    '''
    stepxy
    '''
    global prior_step
    dic_stepxy = json.loads(stepxy)
    print(f'dic_stepxy is {dic_stepxy}')
    prior_step = int(dic_stepxy['stepxy'])/100     # step xy in µm


@socketio.on('fast_z_pos')              # move fast on the z axis
def fast_z_pos(zpos):
    '''
    fast_z_pos
    '''
    ol.set_zpos(int(zpos), move_type='d')          # move to the pos z
    sleep(1)
    print(f'value received for fast_z_pos is  {zpos}')
    sending_posz()              # send the z position to the interface


@socketio.on('set_stepz')                          # step z
def set_stepz(stepz, debug=[]):
    '''
    stepz
    '''
    global z_small_step
    dic_stepz = json.loads(stepz)
    if 0 in debug:
        print(f'dic_stepz is {dic_stepz}')
    z_small_step = int(dic_stepz['stepz'])


@socketio.on('goto_position')
def go_pos(posxyz, debug=[]):
    '''
    go to the pos posxyz from the tree
    '''
    if 0 in debug:
        print(f'######### Go to the position {posxyz}')
    dic_posxyz = json.loads(posxyz)
    try:
        # refresh MDA picture
        with open(opj('mda_temp', 'mda_init', 'lpos_id.yaml')) as f_r:
            # list of the positions id
            lid = yaml.load(f_r, Loader=yaml.FullLoader)
        # current position (pos selected in the tree)
        curr_pos = lid.index(dic_posxyz['id'])
        print(f'curr_pos obtained from Id is {curr_pos} ')
        # change the current observed positon in the interface
        emit('watch_currpos', curr_pos)
    except:                                        # goto x,y,z
        print('no lpos_id.yaml file yet')
        # move in xy
        pr.absolute_move_to(float(dic_posxyz['x']), float(dic_posxyz['y']))
        if 3 in debug:
            print(f"dic_posxyz['z'] = {dic_posxyz['z']} ")
        # move in z
        ol.set_zpos(dic_posxyz['z'])
        sending_pos()


#  move to x,y
@socketio.on('moveto')
def moveto(pos):
    '''
    Move to the position
    '''
    print(f'position is {pos}')
    newpos = json.loads(pos)
    x, y = newpos[0], newpos[1]        # x,y floats in µm
    pr.absolute_move_to(x, y)


@socketio.on('return_z_pos')           # move fast on the z axis
def return_z_pos(msg):
    '''
    Set the pos z of the objective to the saved position in z
    '''
    addr_posz = settings_folder / 'posz.yaml'
    with open(addr_posz) as f_r:
        zpos = yaml.load(f_r, Loader=yaml.FullLoader)
        # move to the pos z
        ol.set_zpos(int(zpos), move_type='d')
        sleep(1)
        print(f'value received for return_z_pos is  {zpos}')
        # pos z sent to the interface in µm
        posz_sent = round(zpos/100, 1)
        emit('posz', f'{posz_sent}', broadcast=True)


@socketio.on('update_position')
def update_pos(node_id, debug=[]):
    '''
    update the pos with id : node_id
    '''
    print(f'######### Updating the position from the tree !!!!')
    posx, posy, posz = pr.ask_pos('x'), pr.ask_pos('y'), ol.ask_zpos()
    if 1 in debug:
        print(f'node_id is {node_id} ')
    if 2 in debug:
        print(f'posx is {posx}, posy is {posy}, posz is {posz} ')
    # refresh the infos in the tree
    idxyz = f'{node_id};{posx};{posy};{posz}'
    emit('update_xyz_infos', idxyz)


def double_sending_pos():
    '''
    '''
    sending_pos()
    sending_pos()


def retrievexy(debug=[]):
    '''
    Retrieve positions x and y
    '''
    posx = pr.ask_pos('x')
    posy = pr.ask_pos('y')
    if 0 in debug:
        print(f'posx is {posx}; posy is {posy}')
    return posx, posy


def sending_pos(debug=[]):
    '''
    Send the position to the interface
    '''
    if 0 in debug:
        print('sending the position x and y to the interface')
    posx, posy = retrievexy()
    while posx == posy:                    # avoid x = y
        posx, posy = retrievexy()
    emit('new_posx', f'{posx}', broadcast=True)
    emit('new_posy', f'{posy}', broadcast=True)


def sending_posz(debug=[]):
    '''
    Send the position in axis z to the interface
    '''
    if 0 in debug:
        print('sending the position z to the interface')
    # ask for current pos z
    posz = ol.ask_zpos()
    if 0 in debug:
        print(f'current posz is {posz}')
    # pos z sent to the interface in µm
    posz_sent = round(posz/100, 1)
    emit('posz', f'{posz_sent}', broadcast=True)      # emit pos z


def sending_steps(debug=[]):
    '''
    Send the steps for x, y and z displacements to the interface
    '''
    if 0 in debug:
        print('sending the steps values to the interface')
    str_steps = json.dumps({"stepxy": prior_step, "stepz": z_small_step})
    emit('steps_xyz', f'{str_steps}', broadcast=True)


def move_in_direct(direct):
    '''
    Move in the direction "direct" with step prior_step
    '''
    x = dic_mv[direct][0]*prior_step   # x relative move
    y = dic_mv[direct][1]*prior_step   # y relative move
    pr.relative_move_to(x, y)


def try_move_in_direct(direct):
    '''
    '''
    try:
        move_in_direct(direct)
    except:
        print('cannot send the move')


def movez_in_direct(direct, debug=[]):
    '''
    Move in the z direction ..
    '''
    if 1 in debug:
        print(f'z_small_step is {z_small_step}')
        print(f'dic_mvz[direct] is {dic_mvz[direct]}')
    # make a step in the z direction
    ol.set_zpos(z_small_step, move_type=dic_mvz[direct])


@socketio.on('move')
def move(direct, debug=[]):
    '''
    Move right, left up, down with command from interface
    '''
    if 1 in debug:
        print(f'message is {direct}')
    try_move_in_direct(direct)     # move the prior
    sending_pos()                  # send position to interface


@socketio.on('movez')
def movez(direct, debug=[]):
    '''
    Move on z axis up down with command from interface
    '''
    if 1 in debug:
        print(f'message is {direct}')
    movez_in_direct(direct)           # move in z
    sending_posz()                    # send position to interface


def save_all_pos():
    '''
    Save the positions for the mda in settings folder
    '''
    addr_list_pos = settings_folder / 'list_pos.yaml'
    with open(addr_list_pos, 'w') as f_w:
        yaml.dump(list_pos, f_w)


# save the positions
@socketio.on('save_pos')
def save_pos(msg):
    '''
    Save, change, reload the positions
    '''
    global list_pos
    if not reload_pos:
        posx = pr.ask_pos('x')
        posy = pr.ask_pos('y')
        new_pos = [posx, posy]            # current position
    else:
        new_pos = reload_pos                # reload position
    if modif_pos:
        list_pos[curr_numpos] = new_pos         # change the existing position
        num_pos = curr_numpos
    else:
        list_pos += [new_pos]         # add a new position
        num_pos = len(list_pos)-1
    print(f'list_pos is {list_pos}')
    str_new_pos = json.dumps({"pos": new_pos, "numpos": num_pos})
    save_all_pos()
    emit('position_saved', str_new_pos)


@socketio.on('curr_numpos')                    #
def retrieve_curr_numpos(numpos):
    '''
    Retrieve the current position index
    '''
    global curr_numpos
    curr_numpos = int(numpos)
    print(f'num position is {curr_numpos}')


@socketio.on('modif_pos')                    #
def allow_modif_pos(modif):
    '''
    Allowing position modif
    '''
    global modif_pos
    modif_pos = int(modif)
    print(f'modif_pos is {modif_pos}')


@socketio.on('reload_pos')
def reload_positions(pos_reload):
    '''
    Reloading the positions
    '''
    global reload_pos
    print(f'reloading the registered positions !!!')
    reload_offset()
    addr_list_pos = settings_folder / 'list_pos.yaml'
    with open(addr_list_pos) as f_r:        # list of the positions
        lpos = yaml.load(f_r)
    print(f'lpos is {lpos}')
    for pos in lpos:
        reload_pos = [pos[0], pos[1]]
        save_pos('')              # inlcude the pos in the current experiment
    reload_pos = []
