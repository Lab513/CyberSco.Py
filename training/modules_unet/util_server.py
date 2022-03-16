from sys import platform as _platform

def find_platform():
    '''
    Find which platform is currently used
    '''
    print('platform is ',_platform)
    if _platform == "linux" or _platform == "linux2":
       platf = 'lin'
    elif _platform == "darwin":
       platf = 'mac'
    elif _platform == "win32":
       platf = 'win'
    return platf

def chose_server(platf):
    '''
    '''
    if platf =='win':
        import gevent as server
        from gevent import monkey
        monkey.patch_all()
    else:
        import eventlet as server
        server.monkey_patch()
    return server
