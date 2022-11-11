'''
Settings channels
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_paths import *
from interface.modules.init.init_devices import *

@socketio.on('load_new_SC')
def change_set_chan(new_SC):
    '''
    '''
    print(f'new_SC is {new_SC}')
    sending_set_chan(new_SC)


def sending_set_chan(SC, debug=[]):
    '''
    Send the values of the setting channels from yaml to interface
    '''
    global dic_chan_set
    if 0 in debug:
        print('sending settings channel to the interface')
    addr_SC = settings_folder / 'settings_channels' / f'{SC}.yaml'
    if 0 in debug:
        print(f'addr_SC is {addr_SC}')
    with open(addr_SC) as f_r:
        dic_chan_set = yaml.load(f_r, Loader=yaml.FullLoader)
    if 0 in debug:
        print(f'In sending_set_chan, dic_chan_set is {dic_chan_set}')
    str_set_chan = json.dumps(dic_chan_set)
    emit('set_chan', f'{str_set_chan}', broadcast=True)


def sending_saved_set_chan(curr_SC='BF', debug=[]):
    '''
    Send the saved setting channels
    '''
    if 0 in debug:
        print('sending saved settings channel to the interface')
    list_yaml = os.listdir(settings_folder / 'settings_channels')
    list_SC = [sc.split('.yaml')[0] for sc in list_yaml]
    if 0 in debug:
        print(f'list_SC is {list_SC}')
    dic_SC = {'curr_SC': curr_SC, 'list_SC': list_SC}
    str_saved_set_chan = json.dumps(dic_SC)
    emit('saved_set_chan', f'{str_saved_set_chan}', broadcast=True)


@socketio.on('save_chan_dict')          # set_chan_dict
def save_chan(dic_chan, debug=[1]):
    '''
    Save the Settings channels dictionary in settings/settings_channels folder
    and refresh the list in the interface
    '''
    global dic_chan_set
    dic_chan_set = json.loads(dic_chan)     # loading from interface
    if 1 in debug:
        print(f'dic_chan_set is {dic_chan_set}')
    folder_SC = settings_folder / 'settings_channels'
    if not os.path.exists(folder_SC):
        os.mkdir(folder_SC)
    name_SC = dic_chan_set['name_set_chan']
    with open(folder_SC / f'{name_SC}.yaml', 'w') as f_w:
        # save set channels to the yaml file
        addr = yaml.dump(dic_chan_set, f_w)
    sending_saved_set_chan(curr_SC=name_SC)    # refresh the list of SC
    if name_SC == 'BF':
        # intensity retrieved from BF setting channel
        intens = int(dic_chan_set['BF'])
        ol.set_intens(intens)                 # change the µscope BF intensity
