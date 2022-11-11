
from dashboard.modules.misc_import import *
from dashboard.flask_app import *
from dashboard.modules.connect.login import *
from dashboard.modules.init.init_paths import *
from bokeh.plotting import figure, output_file, save



@app.route('/infos_cyber', methods=['POST'])
def retrieve_infos(debug=[0]):
    '''
    Retrieve the information from the CyberScoPy servers
    and send the information to the Dashboard page..
    '''
    lobs = ['user', 'equip', 'time_elapsed',
            'mda_launched', 'available',
            'state_devices', 'nb_rep',
            'mda_time_elapsed',
            'pic_time', 'nb_pos',
            'sensors']
    dic_cyb = {}
    if request.method == 'POST':
        for obs in lobs:
            dic_cyb.update({obs: request.form.get(obs)})
        ##
        make_light_fig(dic_cyb)
        make_temp_fig(dic_cyb)
        ###
        dic_infos_cyber = json.dumps(dic_cyb)
        if 0 in debug:
            # check the information for dic_cyber..
            print(f'In dashboard retrieve_infos, dic_infos_cyber is { dic_infos_cyber }')
        socketio.emit('infos_dash', dic_infos_cyber, broadcast=True)

    return ''


def make_sensor_html_fig(dic_cyb, target):
    '''
    Html interactive figure for the sensor
    '''
    print('sensors items.. ')
    dic_sensors = json.loads(dic_cyb['sensors'])
    try:
        xtarg, ytarg = [],[]
        for k,v in dic_sensors.items():
            if v[target].strip() != 'null':
                xtarg.append(int(k))
                ytarg.append(float(v[target]))
        p = figure(title=f"{target} curve", plot_width=300, plot_height=200)
        p.line(xtarg, ytarg)
        p.toolbar.logo = None

        addr_fig_targ = f"dashboard/static/mda_temp_{dic_cyb['user']}/monitorings/{target}_curve.html"
        print(f'address curve light is {addr_fig_targ}')
        output_file(addr_fig_targ)
        save(p)
        print(f'Saved the figure at the address {addr_fig_targ}')
    except:
        print(f'Cannot plot the {target} monitoring..')


def make_light_fig(dic_cyb):
    '''
    Figure for the light monitoring..
    '''
    make_sensor_html_fig(dic_cyb, 'light')


def make_temp_fig(dic_cyb):
    '''
    Figure for the temp monitoring..
    '''
    make_sensor_html_fig(dic_cyb, 'temp')


def message_about_user():
    '''
    '''
    print(f'User last_login to Dashboard is {current_user.last_login}')
    try:
        print(f'User last_protocol is {current_user.last_protocol}')
    except:
        print('last protocol does not exist..')


@app.route('/interf', methods=['GET', 'POST'])
def interf(debug=[]):
    '''
    dashboard page
    '''
    message_about_user()
    now = dt.now()
    current_user.last_login = now
    # save the last login..
    db.session.commit()

    dip = define_index_page(user=current_user)
    if 1 in debug:
        print(f'dip is {dip.__dict__}')

    with open(settings_folder / 'equipements.yaml') as f_r:
        dic_equip = yaml.load(f_r, Loader=yaml.FullLoader)
        print(f'Equipements are : {dic_equip}')

    dip.__dict__.update(dic_equip)

    if 0 in debug:
        print(f'dip is {dip.__dict__}')

    return render_template('index_folder.html', **dip.__dict__)


@socketio.on('params')
def retrieve_params(prms):
    '''
    Retrieve the parameters from the dashboard
    '''
    global params
    params = json.loads(prms)
