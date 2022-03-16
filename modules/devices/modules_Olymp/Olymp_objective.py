import time
import yaml

class OBJ():
    '''
    Objective of Olympus IX81
    '''
    def __init__(self, debug=[]):
        '''
        '''
        self.nbbytes = 11
        try:
            with open(f'devices/modules_Olymp/nn/nn.yaml') as f_r:
                obj = yaml.load(f_r, Loader=yaml.FullLoader)    # read yaml
                if 1 in debug:
                    print(f"obj is {obj}")
        except:
            with open(f'modules/devices/modules_Olymp/nn/nn.yaml') as f_r:
                obj = yaml.load(f_r, Loader=yaml.FullLoader)    # read yaml
                if 1 in debug:
                    print(f"obj is {obj}")
        # reversed dictionary  obj name --> num
        self.dic_obj_rev = {v: k for k, v in obj.items()}
        if 1 in debug:
            print(f'############# self.dic_obj_rev {self.dic_obj_rev}')

        try:
            with open(f'devices/modules_Olymp/dic_obj/dic_obj.yaml') as f_r:
                # read yaml
                self.dic_curr_obj = yaml.load(f_r, Loader=yaml.FullLoader)
        except:
            with open(f'modules/devices/modules'
                      '_Olymp/dic_obj/dic_obj.yaml') as f_r:
                # read yaml
                self.dic_curr_obj = yaml.load(f_r, Loader=yaml.FullLoader)
        if 1 in debug:
            print(f"self.dic_curr_obj is {self.dic_curr_obj}")

        # num x --> num, eg 20x --> 36
        self.dic_obj = {k: self.dic_obj_rev[v]
                        for k, v in self.dic_curr_obj.items()}

        try:
            # objectives position in the tourelle
            with open(f'devices/modules_Olymp/pos_obj/pos_obj.yaml') as file:
                # read yaml, 20x --> position in the wheel
                self.dic_obj_pos = yaml.load(file, Loader=yaml.FullLoader)
                if 1 in debug:
                    print(f"dic_obj_pos is {self.dic_obj_pos}")
        except:
            with open(f'modules/devices/modules'
                      '_Olymp/pos_obj/pos_obj.yaml') as file:
                # read yaml, 20x --> position in the wheel
                self.dic_obj_pos = yaml.load(file, Loader=yaml.FullLoader)
                if 1 in debug:
                    print(f"dic_obj_pos is {self.dic_obj_pos}")
        # position --> 20x
        self.dic_pos_obj = {v: k for k, v in self.dic_obj_pos.items()}
        if 1 in debug:
            print(f"dic_pos_obj is {self.dic_pos_obj}")
        # retrieve the objective value
        self.objective = self.ask_objective()

    def ask_aftbl(self):
        '''
        Ask for the objective
        '''
        self.flush()
        self.emit('2AFTBL?')
        answer = self.receive(self.nbbytes)
        print(f'## ask_aftbl answer is {answer}')
        try:
            val = answer.split()[1].strip()
            self.aftbl = int(val)
        except:
            print("identification of the objective not working")

    def set_aftbl(self, objective, debug=[]):
        '''
        Set the objective
        objective : 20x etc..
        '''
        # num x --> ZDC num
        num = self.dic_obj(objective)
        if 1 in debug:
            print(f'num corresponding to the objective is {num}')
        self.emit('2LOG IN')
        self.emit('2AFTBL ' + str(num))
        self.emit('2LOG OUT')

    def ask_objective(self, debug=[]):
        '''
        Ask which objective
        Answer : 1,2,3 ...
        return 4x, 10x, 20x etc..
        '''
        self.flush()
        self.emit('2LOG IN')
        if 0 in debug:
            print('ask for objective')
        self.flush()
        self.emit('1OB?')
        answer = self.receive(self.nbbytes)
        if 1 in debug:
            print(f'## ask_objective answer is {answer} ')
        prefix = answer.split()[0].strip()
        if prefix == '1OB':
            num_obj = int(answer.split()[1].strip())
            curr_obj = self.dic_pos_obj[num_obj]
            print(f'curr_obj is {curr_obj}')
        else:
            curr_obj = self.objective      # keep the current objective..
        self.emit('2LOG OUT')
        return curr_obj

    def select_obj(self, obj, debug=[]):
        '''
        Set the objective
        num : 1,2,3 ...
        obj : 10x, 20x etc..
        '''
        self.objective = obj
        self.flush()
        # num of the position in the wheel
        num = self.dic_obj_pos[obj]
        self.emit('2LOG IN')
        self.emit('1OB ' + str(num))
        if 0 in debug:
            print(f'changing to obj num {num}')
        self.emit('2LOG OUT')
