'''
Experiment informations
'''


from interface.flask_app import *
from interface.modules.misc_import import *


def ask_experim_infos():
    '''
    Send message for retrieving the infos concerning the experiment
    '''
    emit('experim_infos')
    print('asked for experim infos..')


def ask_for_monitor_params():
    '''
    Send message for retrieving infos about how the experiment is monitored
    '''
    emit('monitor_settings')
    print('asked for monitor settings..')


@socketio.on('save_experim_infos')
def save_experim_infos(dic_infos):
    '''
    Save the infos about the MDA experiment
    '''
    experim_infos = json.loads(dic_infos)
    with open(Path('interface') / 'infos_mda' /
              'experiment_infos.yaml', 'w') as f_w:
        yaml.dump(experim_infos, f_w)
    print('experiment infos saved')


@socketio.on('monitor_params')
def monitor_params(dic_monitor_params, debug=[]):
    '''
    Parameters for monitoring the MDA
    '''
    global monitor_params
    monitor_params = json.loads(dic_monitor_params)
    if 0 in debug:
        print(f'monitor_params are {monitor_params} ')


@socketio.on('curr_rep')
def current_step(rep):
    '''
    Index of the current iteration
    '''
    print(f'Curr step is {rep} !!!!')


@socketio.on('time_elapsed')
def time_lapsed(time_elapsed):
    '''
    Time elapsed since the beginning of the MDA
    '''
    print(f'time elapsed is {time_elapsed} !!!!')
