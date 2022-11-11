from dashboard.modules.init.init_system import *
from dashboard.modules.misc_import import *
from dashboard.flask_app import *

@socketio.on('book_infos')
def save_booking_infos(book_infos):
    '''
    '''
    print(f'dic_book_infos {book_infos}')
    dic_book_infos = json.loads(book_infos)
    #print(os.getcwd())
    addr_book_infos = opj('dashboard','settings','book_infos.yaml')
    with open(addr_book_infos, "w") as f_w:
        yaml.dump(dic_book_infos, f_w)


@socketio.on('ask_book_infos')
def send_book_infos():
    '''
    '''
    send_booking_infos()


def send_booking_infos():
    '''
    '''
    try:
        with open(addr_book_infos) as f_r:
            book_infos = yaml.load(f_r, Loader=yaml.FullLoader)
    except:
        book_infos = {}
    print(f'In run, book_infos is { book_infos }')
    emit('curr_book_infos', json.dumps(book_infos))
