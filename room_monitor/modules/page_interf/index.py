
from room_monitor.modules.misc_import import *
from room_monitor.flask_app import *
from room_monitor.modules.init.init_paths import *
from room_monitor.modules.init.init_devices import *



@app.route('/')
def interf(debug=[]):
    '''
    Room monitoring page
    '''

    dip = define_index_page()
    if 1 in debug:
        print(f'dip is {dip.__dict__}')

    return render_template('index_folder.html', **dip.__dict__)
