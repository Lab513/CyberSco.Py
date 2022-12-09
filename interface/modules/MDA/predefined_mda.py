'''
Interface predef actions..
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.MDA.params_mda import *
from interface.modules.MDA.prepare_mda import *
from interface.modules.init.init_devices import *
from modules.mda import MDA
from interface.modules.connect.login import *
import importlib


def find_exp_name(add_name, debug=[]):
    '''
    Extract the name of the predefined
    experiment from the predefined python experiment file..
    '''
    if 0 in debug:
        print(add_name)
    expr = 'name :'
    with open(add_name) as f_r:
        ll = f_r.readlines()
        name_exp = None
        for l in ll:
            if expr in l:
                name_exp = l.split(expr)[1].strip()
    return name_exp


def find_exp_descr(add_descr, debug=[]):
    '''
    Retrieve the description for the tooltip
    from the python predefined experiment file
    '''
    if 0 in debug:
        print(add_descr)
    expr = 'description :'
    with open(add_descr) as f_r:
        ll = f_r.readlines()
        descr = ""
        take_line = False
        for l in ll:
            if expr in l:
                descr = l.split(expr)[1]
                take_line = True
            elif take_line and not ((expr in l) or ("'''" in l)):
                descr += l
            if "'''" in l:
                take_line = False
                if descr:
                    break
    if 0 in debug:
        print(f'descr {descr}')
    return descr


def sending_predef(debug=[]):
    '''
    Preset experiments
    '''
    addr_plugins = opj('modules', 'predef', 'plugins')
    # list addresses plugins
    lplugs = glob.glob(f'{addr_plugins}/*.py')
    list_plugins = [p for p in lplugs if '__init__' not in p]
    # association name_exp to name plugin, description etc..
    dic_exp = {}
    for addr in list_plugins:
        # retrieving the preset experiment name
        name_exp = find_exp_name(addr)
        descr_exp = find_exp_descr(addr)
        if name_exp:
            # if name exists add to dictionary
            dic_exp[name_exp] = {'name_plugin': opb(addr)[:-10],
                                 'descr_plugin': descr_exp}
    dic_plugins = json.dumps(dic_exp)
    emit('predef_mdas', dic_plugins, broadcast=True)
    if 1 in debug:
        print(f'sending the plugins')
        print(f'dic_plugins = {dic_plugins}')


def save_list_pos(mda_protocol):
    '''
    Save the list of positions for predefined MDAs
    '''
    print(f'mda_protocol.lxyz {mda_protocol.lxyz} ')
    all_pos = opj('mda_temp', 'mda_init', 'lxyz.yaml')
    with open(all_pos, "w") as f_w:
        yaml.dump(mda_protocol.lxyz, f_w)


def save_list_offsets(mda_protocol):
    '''
    Save the list of the offsets
    '''
    print(f'mda_protocol.loffsets {mda_protocol.loffsets} ')
    all_pos = opj('mda_temp', 'mda_init', 'loffsets.yaml')
    with open(all_pos, "w") as f_w:
        yaml.dump(mda_protocol.loffsets, f_w)


def save_list_SC_ET(mda_protocol):
    '''
    Save the list of SC and ET for predefined MDAs
    '''
    print(f'mda_protocol.list_SC_ET {mda_protocol.list_SC_ET} ')
    all_SC_ET = opj('mda_temp', 'mda_init', 'list_SC_ET.yaml')
    with open(all_SC_ET, "w") as f_w:
        yaml.dump(mda_protocol.list_SC_ET, f_w)


def save_list_AF(mda_protocol, debug=[0]):
    '''
    Save the list of AF for predefined MDAs
    The default autofocus is afml_sweep
    '''
    if 0 in debug:
        print('Saving the AF parameters for predef')
        print(f'mda_protocol.list_AF = {mda_protocol.list_AF}')
    # by default afml_sweep
    mda_protocol.list_AF = ['afml_sweep' if af is None else af for af
                            in mda_protocol.list_AF ]
    print(f'mda_protocol.list_AF {mda_protocol.list_AF} ')
    all_AF = opj('mda_temp', 'mda_init', 'list_AF.yaml')
    with open(all_AF, "w") as f_w:
        yaml.dump(mda_protocol.list_AF, f_w)


def save_list_gates(mda_protocol):
    '''
    Save the list of the gates for predefined MDAs
    '''
    print(f'mda_protocol.list_gates {mda_protocol.list_gates} ')
    all_gates = opj('mda_temp', 'mda_init', 'list_gates.yaml')
    with open(all_gates, "w") as f_w:
        yaml.dump(mda_protocol.list_gates, f_w)


def passing_from_tree_to_predefined(mda_protocol, debug=[]):
    '''
    Write in yaml files the informations from the tree
    to inject them after in the mda..
    '''
    mda_protocol.load_tree_protocol('@predef_prot.yaml')
    if 0 in debug:
        print(f'dir(mda_protocol) {dir(mda_protocol)} ')
    save_list_id(mda_protocol)
    save_list_pos(mda_protocol)
    save_list_offsets(mda_protocol)
    try:
        save_list_AF(mda_protocol)
    except:
        print('In predef, not using AF parameters from tree !!!')
    save_list_gates(mda_protocol)
    save_list_SC_ET(mda_protocol)


def launch_mda_predef(cam):
    '''
    Launch predefined experiment
    '''
    global current_user
    chosen_plugin = f'modules.predef.plugins.{curr_mda_scenario}_plugin'
    module = importlib.import_module(chosen_plugin)
    mda_protocol = getattr(module,
                           f'{curr_mda_scenario}'.upper())(
                             ldevices=[ol, pr, cam, co, xc, ga, se],
                             user=current_user)
    # attaching the current segmentation model to the microscope for focus
    ol.mod_afml = mda_protocol.mod0
    mda_params(mda_protocol)
    ##
    passing_from_tree_to_predefined(mda_protocol)
    ####
    mda_protocol.get_positions()        # retrieve the positions
    mda_protocol.get_gates()            # retrieve the gates association
    mda_protocol.get_chan_set()         # retrieve the channels settings
    mda_protocol.get_focus()            # set positions focus kind..

    mda_protocol.define()


@socketio.on('choice_mda_scenario')
def choice_mda_scenario(msg,debug=[0]):
    '''
    Retrieve the MDA scenario from the interface
    '''
    global curr_mda_scenario
    msgsplit = msg.split('select')
    if 0 in debug:
        print(f'msgsplit is {msgsplit} ')
    if msgsplit[0] != 'de':
        curr_mda_scenario = msgsplit[1].strip()
    else:
        curr_mda_scenario = None
    print(Fore.YELLOW + '************** ')
    print('')
    print(f'Selected scenario is {curr_mda_scenario} ')
    print('')
    print('************** ')
    print(Style.RESET_ALL)
