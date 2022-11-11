'''
interface protocoles actions..
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.page_interf.index import *


def make_protocol_list(debug=[]):
    '''
    List of the protocols
    '''
    addr_prot = 'interface/static/mda_protocols/*.yaml'
    # list of the yaml protocols
    protocols_list = [opb(f).split('.yaml')[0] for f in glob.glob(addr_prot)]
    protocols_list.remove('temp0')
    if 1 in debug:
        print(f'protocols_list {protocols_list}')

    return protocols_list


@socketio.on('save_protocol')
def save_protocol(dicp, debug=[0]):
    '''
    Save  the protocol as a yaml file
    '''
    if 0 in debug:
        print('#### Save the protocole !!!!')
    # new created protocol
    dic_prot = json.loads(dicp)
    addr_prot_saved = opj('interface', 'static',
                          'mda_protocols', dic_prot['newname'])
    prot_saved = opb(addr_prot_saved).split('.yaml')[0]
    if prot_saved[0].isalpha() or prot_saved == '@predef_prot':
        print(f'### addr_prot_saved : {addr_prot_saved} ')
        with open(addr_prot_saved, 'w') as f_w:
            yaml.dump(dic_prot['tree'],
                      f_w,
                      allow_unicode=True,
                      default_flow_style=False)
    else:
        print('First letter must be alphabetical..')
    # recreate list of protocols
    protocols_list = make_protocol_list()
    # refresh the list in the select list
    emit('refresh_list_protocols', json.dumps(protocols_list))

    return redirect(url_for('interf'))


@socketio.on('delete_protocol')
def delete_protocol(dicp):
    '''
    Delete the current protocol
    '''
    dic_prot = json.loads(dicp)
    file_to_remove = opj('interface', 'static',
                         'mda_protocols', dic_prot['nameprotoc'])
    print(f'### file_to_remove {file_to_remove} ')
    if '@predef_prot' not in file_to_remove:      # protecting @predef_prot
        os.remove(file_to_remove)
    protocols_list = make_protocol_list()
    # refresh the list in the select list
    emit('refresh_list_protocols', json.dumps(protocols_list))

    return redirect(url_for('interf'))


@socketio.on('read_yaml')
def read_yaml(name_yaml, debug=[1]):
    '''
    Read_yaml and send the json for loading the protocol in the tree
    '''
    addr_yaml = opj('interface', 'static', 'mda_protocols', name_yaml)
    if 1 in debug:
        print(f'addr_yaml {addr_yaml}')
    try:
        with open(addr_yaml) as f_r:
            yaml_file = yaml.load(f_r, Loader=yaml.FullLoader)
            # transmit with json
            emit('prot_json', json.dumps(yaml_file))
    except:
        print('Cannot read the yaml file')
    # corrections in the tree for predef
    if name_yaml == 'temp0.yaml':
        emit('correct_tree', '')
