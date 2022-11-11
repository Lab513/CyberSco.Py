from interface.modules.init.init_params import *
from interface.flask_app import *
from interface.modules.misc_import import *

#  save the associations pos <--> gate
@socketio.on('pos_gate')
def save_pos_gate(pgate):
    '''
    Saving gate associated to each position
    '''
    global dic_pos_gate
    dic_pgate = json.loads(pgate)
    for k, v in dic_pgate.items():
        dic_pos_gate[int(k)] = int(v)
    print(f'dic_pos_gate is {dic_pos_gate}')
