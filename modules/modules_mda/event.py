

class EVENT():
    '''
    Event
    '''
    def __init__(self, name=None):
        '''
        Object event
        '''
        self.name = name  # kind of action
        self.happened = False
        self.exists = False
