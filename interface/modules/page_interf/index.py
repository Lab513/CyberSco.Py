
from interface.modules.init.init_params import *
import interface.modules.init.init_glob_vars as g
from interface.modules.misc_import import *
from interface.flask_app import *
from interface.modules.connect.login import *
from interface.modules.init.init_system import *
from threading import Thread


def find_mac_addr():
    '''
    Mac address to identify the equipement..
    '''
    mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

    return mac_addr


def begin_dash_time(debug=[0]):
    '''
    Beginning point of the time for the dashboard..
    '''
    global time_dash0
    time_dash0 =  round(time.time(),1)
    if 0 in debug:
        print(f'time_dash0 is {time_dash0}')

dic_infos_dash  = {}

def time_for_dashboard(debug=[]):
    '''
    Time elapsed
    '''
    try:
        ttot = round(time.time()-time_dash0,1)
        ttot_hrs = int(ttot//3600)
        sec_resting = int(ttot%3600)
        ttot_min = int(sec_resting//60)
        ##
        telapsed = f'{ttot_hrs}h{ttot_min}m'
        dic_infos_dash['time_elapsed'] = telapsed
    except:
        if 1 in debug:
            print('time_dash0 is probably not defined.. ')
        dic_infos_dash['time_elapsed'] = f'00h00m'
    if 1 in debug:
        print(f'telapsed is {telapsed}')


def time_mda_ran(debug=[]):
    '''
    MDA time elapsed
    '''
    if g.mda_time_start:
        ttot = round(time.time()-g.mda_time_start,1)
        ttot_hrs = int(ttot//3600)
        sec_resting = int(ttot%3600)
        ttot_min = int(sec_resting//60)
        ##
        mdat_elapsed = f'{ttot_hrs}h{ttot_min}m'
        dic_infos_dash['time_mda_elapsed'] = mdat_elapsed
        if 0 in debug:
            print(f'mdat_elapsed is {mdat_elapsed}')
    else:
        dic_infos_dash['time_mda_elapsed'] = 'none'


def is_mda_launched(debug=[]):
    '''
    info about mda running or not..
    '''
    if 0 in debug:
        print(f"in is_mda_launched, g.mda_launched = {g.mda_launched}")
    if g.mda_launched:
        dic_infos_dash['mda_launched'] = 'true'
    else:
        dic_infos_dash['mda_launched'] = 'false'


def is_available(debug=[0]):
    '''
    Is the equipement available..
    '''
    if g.equipement_booked:
        dic_infos_dash['available'] = 'false'
    else:
        dic_infos_dash['available'] = 'true'


def count_mda_nb_rep(debug=[]):
    '''
    '''
    if g.mda_launched:
        try:
            dir_mda_temp = opj(os.getcwd(), 'mda_temp')
            with open(opj(dir_mda_temp, 'monitorings', 'nb_rep.txt'), "r") as f_r:
                nb_rep = f_r.readline()
                dic_infos_dash['nb_rep'] = nb_rep
            if 0 in debug:
                print(f'nb_rep = {nb_rep}')
        except:
            print('Cannot read nb_rep..')


def send_nb_pos(debug=[]):
    '''
    '''
    if g.mda_launched:
        try:
            dir_mda_temp = opj(os.getcwd(), 'mda_temp')
            with open(opj(dir_mda_temp, 'monitorings', 'nb_pos.txt'), "r") as f_r:
                nb_pos = f_r.readline()
                dic_infos_dash['nb_pos'] = nb_pos
            if 0 in debug:
                print(f'nb_pos = {nb_pos}')
        except:
            if 0 in debug:
                print('Cannot read nb_pos..')


def send_sensors(debug=[]):
    '''
    Send the sensors information..
    '''
    if g.mda_launched:
        dir_mda_temp = opj(os.getcwd(), 'mda_temp')
        addr_sensors = opj(dir_mda_temp, 'monitorings', 'sensors.yaml')
        if ope(addr_sensors):
            with open(addr_sensors, "r") as f_r:
                info_sensors = yaml.load(f_r, Loader=yaml.FullLoader)
                dic_infos_dash['sensors'] = json.dumps(info_sensors)
            if 0 in debug:
                print(f'info_sensors = {info_sensors}')
        else:
            if 0 in debug:
                print('Cannot read sensors.yaml ..')


def send_rep_pos_time(debug=[]):
    '''
    Send the times of acquisition for each picture from the beginning of the MDA
    '''
    if g.mda_launched:
        dir_mda_temp = opj(os.getcwd(), 'mda_temp')
        addr_pic_time = opj(dir_mda_temp, 'monitorings', 'pic_time.yaml')
        if ope(addr_pic_time):
            with open(addr_pic_time, "r") as f_r:
                dic_pic_time = yaml.load(f_r, Loader=yaml.FullLoader)
                dic_infos_dash['pic_time'] = json.dumps(dic_pic_time)
        else:
            print('Cannot read pic_time.yaml file .. ')


def list_device_state():
    '''
    Register the devices state
    '''
    try:
        dic_infos_dash['state_devices'] = json.dumps(state_devices)
    except:
        print('##** Cannot access to state_devices... **##')


def init_equipement():
    '''
    Link the equipement to the mac address
    '''
    dic_equip = {'a4:bb:6d:d3:ee:86' : 'Miss_Marple'}
    mac_addr = find_mac_addr()
    equip = dic_equip[mac_addr]
    return equip


def init_infos_for_dashboard():
    '''
    Make the dictionary for the dashboard..
    '''
    global dic_infos_dash
    ##
    user = current_user.name
    print(f'current_user.name is {current_user.name}')
    print(f'current_user.snap_addr is {current_user.snap_addr}')
    print(f'current_user.last_protocol is {current_user.last_protocol}')
    ##
    equip = init_equipement()
    ## init the dictionary
    dic_infos_dash = {'user': user,
                      'equip': equip,
                      'time_elapsed':'00h00m',
                      'mda_launched':'false',
                      'available':'false',
                      'state_devices':'{}',
                      'nb_rep':'0',
                      'pic_time':"{'0':{'0':'0'}}",
                      'nb_pos':'none',
                      'sensors':'{}'}


def mess_curr_user():
    '''
    '''
    print(f'User last_login is {current_user.last_login}')
    try:
        print(f'User last_protocol is {current_user.last_protocol}')
    except:
        print('last protocol does not exist..')


def save_last_login_date():
    '''
    Save the user last login date..
    '''
    now = dt.now()
    current_user.last_login = now
    # save the last login..
    db.session.commit()


@app.route('/interf', methods=['GET', 'POST'])
def interf(debug=[]):
    '''
    Interface page
    '''
    begin_dash_time()
    mess_curr_user()
    save_last_login_date()
    init_infos_for_dashboard()

    dip = define_index_page(user=current_user)
    if 0 in debug:
        print(f'dip is {dip.__dict__}')
    return render_template('index_folder.html', **dip.__dict__)


def thread_dash(debug=[]):
    '''
    '''
    while 1:
        time_for_dashboard()
        is_mda_launched()
        is_available()
        list_device_state()
        count_mda_nb_rep()
        send_nb_pos()
        send_sensors()
        time_mda_ran()
        send_rep_pos_time()
        if 0 in debug:
            print(f'In send_infos_dash, dic_infos_dash is {dic_infos_dash}')
        socketio.emit('infos_dash', dic_infos_dash, broadcast=True)
        socketio.sleep(1)
        sleep(10)


thread_dash_launched = False


@socketio.on('ask_infos_dash')
def send_infos_dash(msg, debug=[0]):
    '''
    Transmit the infos for dashboard
     to the image_refresh.html page..
     Launch the thread only once..
    '''
    global thread_dash_launched
    if not thread_dash_launched:
        socketio.start_background_task(target=lambda: thread_dash())
        # thread_dash_info = Thread(target=thread_dash)
        # thread_dash_info.start()
        thread_dash_launched = True


@socketio.on('params')
def retrieve_params(prms):
    '''
    Retrieve the parameters from the interface
    '''
    global params
    params = json.loads(prms)
