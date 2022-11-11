
class STEP():
    '''
    Step
    '''
    def __init__(self, val, kind, attr=None):
        '''
        Unit of action
        '''
        self.kind = kind     # kind of action
        self.val = val       # value for the action
        if attr:
            for k, v in attr.items():
                setattr(self, k, v)


class MDA_ACTIONS():
    '''
    '''

    def __init__(slef):
        '''
        '''
        pass

    def focus(self, all=True, debug=[0]):
        '''
        Refocus on the first position (all=False)
         or all the positions (all=True) ..
        '''
        if 0 in debug:
            print(f'len(self.list_pos) = {len(self.list_pos)} ')
        if all:
            for pos in self.list_pos:
                pos.list_steps['refocus'] = STEP(None, kind='refocus')
        else:
            self.list_pos[0].list_steps['refocus'] = STEP(None, kind='refocus')

    def take_pic(self, debug=[0]):
        '''
        Take a picture in BF
        '''
        for pos in self.list_pos:
            pos.list_steps['take_pic'] = STEP(val=pos.chan_set, kind='cam')
            if 0 in debug:
                print(f'pos.list_steps.keys() = {pos.list_steps.keys()}')

    def take_pic_fluo(self, kind_fluo,
                      mask=None,
                      mask_exp_time=None):
        '''
        Take a picture in fluorescence
        pos.chan_set : list with dictionary
                       containing the name and exp time
                       of the SC
        '''
        for pos in self.list_pos:
            pos.list_steps[f'fluo_{kind_fluo}'] =\
                STEP(val=pos.chan_set, kind='fluo',
                     attr={'kind_fluo': kind_fluo,
                           'mask': mask,
                           'mask_exp_time': mask_exp_time})

    def analyse_pic(self):
        '''
        Analyse the resulting image
        '''
        for pos in self.list_pos:
            # analysis when at last image
            pos.list_steps['cells_analysis'] =\
                  STEP(None, kind='cells_analysis')
