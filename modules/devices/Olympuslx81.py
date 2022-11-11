import serial
import time
import yaml
##
try:
    from modules.devices.serial_basics import SERIAL_BASICS as SB
except:
    from devices.serial_basics import SERIAL_BASICS as SB
##
try:
    from devices.modules_Olymp.Olymp_lamp import LAMP as LP
    from devices.modules_Olymp.Olymp_zpos import ZPOS as ZP
    from devices.modules_Olymp.Olymp_shutter import SHUT as SH
    from devices.modules_Olymp.Olymp_wheel import WHEEL as WH
    from devices.modules_Olymp.Olymp_objective import OBJ as OB
    from devices.modules_Olymp.Olymp_autofocus import AF
    from devices.modules_Olymp.Olymp_focus_segment import FOCUS_SEGM as FS
except:
    from modules.devices.modules_Olymp.Olymp_lamp import LAMP as LP
    from modules.devices.modules_Olymp.Olymp_zpos import ZPOS as ZP
    from modules.devices.modules_Olymp.Olymp_shutter import SHUT as SH
    from modules.devices.modules_Olymp.Olymp_wheel import WHEEL as WH
    from modules.devices.modules_Olymp.Olymp_objective import OBJ as OB
    from modules.devices.modules_Olymp.Olymp_autofocus import AF
    from modules.devices.modules_Olymp.Olymp_focus_segment import FOCUS_SEGM as FS

class OLYMP(SB, LP, ZP, SH, WH, OB, AF, FS):
    '''
    '''
    def __init__(self, port=None):
        '''
        '''

        self.name = 'olympus'
        self.lamp = True
        self.shut_ctrl = -1
        self.cntrl = 0
        self.shut = 0
        self.zpos = -1
        self.zpos_cntrl = 0
        self.offset = 0
        self.afml_optim = 'max'
        cl_name = self.__class__.__name__
        self.port_init(f'{cl_name}'.lower(), port=port)
        lcls = [SB, LP, ZP, SH, WH, OB, AF, FS]
        [cl.__init__(self) for cl in lcls]

    def test_response(self):
        '''
        Check the communication
        '''
        self.emit('2POS?')
        answer = self.receive(11)
        return answer

    def set_off(self):
        '''
        '''
        self.emit('1LOG IN')
        self.emit("1SHUT1 IN")
        self.emit('1LOG OUT')
        self.shutter = False

    def reset(self):
        '''
        '''
        self.emit('1LOG OUT')
        self.emit("2LOG OUT")

    def set_channel(self):
        '''
        '''
        self.emit('1LOG IN');
        if self.shut:
            self.emit("1SHUT1 OUT")                    # shutter out
        else:
            self.emit("1SHUT1 IN")                     # shutter in
        if self.lamp:
            self.emit("1LMPSW ON")                     # light on
        else:
            self.emit("1LMPSW OFF")                    # light off
        self.emit('1LMP '+ str(int(self.intens*10)))   # intensity

        if self.timeout != -1:
            pass
        else:
             self.emit('1LOG OUT')

    def get(self):
        '''
        '''
        cmds = ['1LOG IN',
                '1MU?',
                '1SHUT1?',
                '1LMPSW?',
                '1LMP?',
                '1LOG OUT',
                '2LOG IN',
                '2AFFLMT?',
                '2AFNLMT?',
                '2FARLMT?',
                '2NEARLMT?',
                '2AFTBL?',
                '2POS?',
                '2LOG OUT']
        for cmd in cmds:
            self.emit(cmd)

    def get_zpos(self):
        '''
        '''
        self.emit('2POS?')

    def give_access_back(self):
        '''
        Permits to reuse manually the microscope for setting the z position
        '''
        self.emit('2JOG ON')
        self.emit('2JOGSNS 10')
        self.emit('2joglmt ON')
