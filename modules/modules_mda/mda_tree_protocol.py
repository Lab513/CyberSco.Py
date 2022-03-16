'''
Translate tree protocol from the corresponding
yaml file to CyberScoPy instructions
'''

from datetime import datetime
import oyaml as yaml
import os
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join

try:
    from modules_mda.retrieve_tree_protocol\
            import RETRIEVE_TREE_PROTOCOL as RTP
except:
    from modules.modules_mda.retrieve_tree_protocol\
                    import RETRIEVE_TREE_PROTOCOL as RTP


class MDA_TREE_PROTOCOL(RTP):
    '''
    mda protocol tree
    '''
    def __init__(self):
        '''
        '''
        RTP.__init__(self)
        self.pos_ind = 0

    def load_tree_protocol(self, curr_prot, debug=[0, 1]):
        '''
        Load recursively the tree protocol
        '''
        if 0 in debug:
            print(f'in load_tree_protocol, retrieving protocol { curr_prot }')
        self.curr_prot = curr_prot
        addr_yaml = opj('interface', 'static', 'mda_protocols', curr_prot)
        with open(addr_yaml) as f_r:
            yaml_file = yaml.load(f_r, Loader=yaml.FullLoader)
        ##
        self.first_time = datetime.now()
        if 1 in debug:
            print('will build the tree recursively !!')
        self.iterdict(self, [yaml_file])    # recursively build the protocol

    def launch(self):
        '''
        Launch the protocol
        '''
        self.loop()                                # launch the first loop

    def iterdict(self, obj, l, debug=[0,2]):
        '''
        Applying recursivity for building the MDA hierarchical object
        '''
        if 0 in debug:
            print(f'The whole protocol is {l}')
        for d in l:
            if 1 in debug:
                print(f'in iterdict, d is {d}')
            for k, v in d.items():
                if 2 in debug:
                    print(f'in iterdict, dealing with k {k} and v {v}')

                # root
                if k == 'title' and v == 'root':
                    self.retrieve_root(d, obj)

                # Protocol
                if k == 'type' and v == 'PROT':
                    self.retrieve_protocol(d, obj)

                # Loop
                if k == 'type' and v == 'LOOP':
                    self.retrieve_loop(d, obj)

                # Position
                if k == 'type' and v == 'XYZ':
                    self.retrieve_position(d, obj)

                # Settings channel: SPSC or SPSCM
                if k == 'type' and (v == 'SPSC' or v == 'SPSCM'):
                    mask = 'M' in v         # True if mask
                    self.retrieve_take_picture(d, obj, mask)

                # Autofocus
                if k == 'type' and v == 'AF':
                    self.retrieve_AF(d, obj)
