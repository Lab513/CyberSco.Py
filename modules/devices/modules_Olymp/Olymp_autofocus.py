# https://neurodiscovery.harvard.edu/files/hndc/files/ix81_zdc.pdf page 3
from time import time
from time import sleep
from colorama import Fore, Back, Style
import yaml

class AF():
    '''
    Autofocus of Olympus IX81
    # https://neurodiscovery.harvard.edu/files/hndc/files/ix81_zdc.pdf page 3
    # https://documents.epfl.ch/users/r/ro/ross/www/fjr0021-ix81_command.html
    '''
    def __init__(self, debug=[]):
        '''
        '''
        # list of optimal z for ZDC method
        self.list_focusZDC_zpos = []
        self.nbbytes = 11
        self.offset = None
        self.jump_down = 800
        try:
            with open(f'devices/modules_Olymp/wd/wd.yaml') as file:
                # read yaml port file
                dic_wd = yaml.load(file, Loader=yaml.FullLoader)
                if 0 in debug:
                    print(f"dic_wd is {dic_wd}")
        except:
            with open(f'modules/devices/modules_Olymp/wd/wd.yaml') as file:
                # read yaml port file
                dic_wd = yaml.load(file, Loader=yaml.FullLoader)
                if 0 in debug:
                    print(f"dic_wd is {dic_wd}")

        if self.objective in ['60x', '100x']:
            fact = 10000
            # toward up direction (ratio), toward down (1-ratio)
            self.ratio_af = 0.3
        else:
            fact = 5000             # orig 5000
            # toward up direction (ratio), toward down (1-ratio)
            self.ratio_af = 0.5
        # total range (min to max) of search for autofocus 30000 for 20x
        # excursion limits according to the objective
        self.delta_af = int(dic_wd[self.objective]*fact)
        if 1 in debug:
            print(f"### current objective is {self.objective}")
        if 2 in debug:
            print(f"### self.delta_af is {self.delta_af}")

    def ask_far_limit(self):
        '''
        Ask FAR limit
        '''
        self.flush()
        self.emit('2FARLMT?')
        answer = self.receive(self.nbbytes+5)
        print(f'## ask_far_limit answer is {answer}')
        val = answer.split()[1].strip()
        self.farLmt = int(val) if val!='X' else 'X'

    def ask_near_limit(self):
        '''
        Ask NEAR limit()
        '''
        self.flush()
        self.emit('2NEARLMT?')
        answer = self.receive(self.nbbytes+5)
        print(f'## ask_near_limit answer is {answer}')
        val = answer.split()[1].strip()
        self.nearLmt = int(val) if val!='X' else 'X'

    def ask_af_far_limit(self):
        '''
        Ask autofocus FAR limit
        '''
        self.flush()
        self.emit('2AFFLMT?')
        answer = self.receive(self.nbbytes+3)
        print(f'## ask_af_far_limit answer is {answer}')
        val = answer.split()[1].strip()
        self.affLmt = int(val) if val!='X' else 'X'

    def ask_af_near_limit(self):
        '''
        Ask autofocus NEAR limit
        '''
        self.flush()
        self.emit('2AFNLMT?')
        answer = self.receive(self.nbbytes+3)
        print(f'## ask_af_near_limit answer is {answer}')
        val = answer.split()[1].strip()
        self.afnLmt = int(val) if val!='X' else 'X'

    def set_afnLmt(self):
        '''
        Set autofocus limit
        '''
        self.emit('2LOG IN')
        self.emit('2AFNLMT ' + str(int(self.afnLmt)))
        self.emit('2LOG OUT')

    def af(self):
        '''
        Autofocus
        '''
        self.emit('2LOG IN')
        self.emit('2FARLMT 10')                  # lim inf for microscope
        self.emit('2NEARLMT 3000000')            # lim sup for microscope
        # lim autofocus inf, decided at offset
        self.emit(f'2AFFLMT {self.AFFLMT}')
        # lim autofocus sup, decided at offset
        self.emit(f'2AFNLMT {self.AFNLMT}')
        self.emit('2aftim 4')
        print(f'2AFTBL {self.dic_obj[self.objective]}')
        self.emit(f'2AFTBL {self.dic_obj[self.objective]}')
        print('2AF SHOT')
        self.emit('2AF SHOT')
        self.emit('2LOG OUT')
        sleep(2)

    def set_lim_af_sup_and_inf(self):
        '''
        Set the inf and sup limits for autofocus
        '''
        posz = self.ask_zpos()
        delta_inf = int(self.delta_af*(1-self.ratio_af))
        delta_sup = int(self.delta_af*self.ratio_af)
        self.AFFLMT = posz - delta_inf                    # lim AF inf
        self.AFNLMT = posz + delta_sup                    # lim AF sup
        print(f'self.AFFLMT is {self.AFFLMT}')
        print(f'self.AFNLMT is {self.AFNLMT}')
        print('----------')
        print(f'delta_inf is {delta_inf/100} µm')
        print(f'delta_sup is {delta_sup/100} µm')

    def posz_jump_down(self):
        '''
        Jump down for the focus in the cases > 60x
        '''
        self.set_zpos(self.jump_down, 'F')   # if >=60x, go under the lowest AF
        print(Fore.YELLOW + f'jumping down !!!!')
        pos_after_jump = self.ask_zpos()
        print(Fore.YELLOW + f'pos_after_jump {pos_after_jump}')
        print(Style.RESET_ALL)

    def jump_to_ref(self):
        '''
        Jump to ref position for making a reproducible AF.
        '''
        self.set_zpos(self.ref_posz, 'd')   # if >=60x, go under the lowest AF
        print(Fore.YELLOW + f'jump to ref posz !!!!')
        pos_after_jump = self.ask_zpos()
        print(Fore.YELLOW + f'pos_after_jump {pos_after_jump}')
        print(Style.RESET_ALL)

    def make_af(self, use_channel=False, debug=[1]):
        '''
        Make the focus
        use_channel: if True make the focus in the channel
         else make the focus in place.
        '''
        if use_channel:
            self.pr.relative_move_to(0,-300)          # go in the channel
        self.af()
        if use_channel:
            self.pr.relative_move_to(0,300)       # come back from the channel

    def calc_offset(self, debug=[]):
        '''
        Find the offset
        '''
        # finding the kind of objective 4x, 10x, 20x etc..
        self.objective = self.ask_objective()
        # define sup and inf limit for autofocus
        self.set_lim_af_sup_and_inf()
        print("searching the offset !!!!")
        # focused position
        posz = self.ask_zpos()
        self.ref_posz = posz #-self.jump_down
        self.posz_jump_down()
        print(f'posz before autofocus {posz}')
        sleep(1)
        self.make_af()                             # perform autofocus
        if 1 in debug: sleep(5)                    # check image at AF
        new_posz = self.ask_zpos()                 # position after autofocus
        self.af_pos = new_posz                     # save autofocus position
        print(f'posz {posz}, pos after autofocus {new_posz}')
        self.offset = self.ref_posz-new_posz       # calculation of the offset
        if 2 in debug:
            print('#####')
            print(Fore.YELLOW + f'the offset is {self.offset}')
            print(Style.RESET_ALL)
            print('#####')

    def zdc_refocus(self, num='', debug=[1,2,3]):
        '''
        Refocus using the offset
        Go back to reference zpos, make the autofocus and add the offset
        There can be an intermediate position for stabilizing the autofocus..
        num : position index
        '''
        t0 = time()
        self.num = num
        print("refocusing !!!!")
        self.jump_to_ref()                         # return to ref position
        self.make_af()                             # make the AF
        sleep(0.5)
        if 0 in debug: sleep(5)                   # delay to check AF position
        new_posz = self.ask_zpos()
        if 1 in debug:
            print(Fore.YELLOW + f'####### new_posz, '
                                f'just after AF is {new_posz} !!! ')
            print(Style.RESET_ALL)
        try:
            # focus = AF position + offset
            pos_focus = new_posz + int(self.offset)
        except:
            print("Make the focus before !!!")
        if 2 in debug:
            print(Fore.YELLOW + f'offset used for refocusing is {self.offset}')
            print( f'####### curr pos {new_posz} '
                   f'pos targetted for focus {pos_focus}')
            print(Style.RESET_ALL)
        # return to the focused position
        self.set_zpos(pos_focus, move_type='d')
        if 3 in debug:
            print(Fore.YELLOW + f'pos AF is {self.af_pos}')
            print(f'offset is {self.offset}')
            print(Style.RESET_ALL)
        t1 = time()
        self.messages_refocus_zdc(t0,t1,pos_focus)

        return pos_focus

    def messages_refocus_zdc(self, t0, t1, pos_focus):
        '''
        time for focusing with ZDC,
        '''
        print(f'time elapsed for the focus ZDC is {round((t1-t0) , 1)} s')
        print(Fore.YELLOW + '------------------')
        print(f'pos_focus ZDC is {pos_focus}')
        print(Style.RESET_ALL)
