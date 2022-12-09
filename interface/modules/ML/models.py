'''
Models
'''

from interface.flask_app import *
from interface.modules.misc_import import *


def sending_used_models(debug=[]):
    '''
    Send to the interface which main segmentation model is used
    '''

    with open('modules/settings/used_models.yaml') as f_r:
        used_models = yaml.load(f_r, Loader=yaml.FullLoader)
    dic_mod0 = json.dumps(used_models['mod0'])
    emit('mod0', dic_mod0, broadcast=True)
    dic_mod1 = json.dumps(used_models['mod1'])
    emit('mod1', dic_mod1, broadcast=True)
    if 0 in debug:
        print(f'sent the current model name : {curr_model} to the interface..')
    # send the models for AFML
    dic_models = json.dumps(used_models)
    emit('models_used', dic_models, broadcast=True)


def sending_all_models(debug=[]):
    '''
    Send to the interface all the models..
    '''
    with open('modules/settings/models.yaml') as f_r:
        all_models = yaml.load(f_r, Loader=yaml.FullLoader)
    if 0 in debug:
        print(f'all_models.keys() is {all_models.keys()}')
    # list of the models aliases
    list_models = json.dumps(list(all_models.keys()))
    emit('all_models', list_models, broadcast=True)
    if 0 in debug:
        print(f'sent all_models.keys()'
              f' : {all_models.keys()} to the interface..')
    sleep(1)
    sending_used_models()


@socketio.on('change_model')
def change_model(model, debug=[]):
    '''
    Inform the interface about the new loaded model..
    '''
    # with open('modules/settings/curr_model.yaml', 'w') as f_w:
    #     yaml.dump(model, f_w)
    if 0 in debug:
        print(f'Changed model to {model}')
    # emit('curr_model', model, broadcast=True)
    emit('new_model', model, broadcast=True)


@socketio.on('ask_nb_cells')
def ask_emit_nb_cells(msg):
    '''
    Send to the interface the nb of cells from yaml
    '''
    try:
        with open('interface/static/mda_pics/nb_cells.yaml') as f_r:
            nb_cells = yaml.load(f_r, Loader=yaml.FullLoader)
            emit('real_time_nb_cells', nb_cells)
    except:
        print('Probably cannot find the file : nb_cells.yaml')
