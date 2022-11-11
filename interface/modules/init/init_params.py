# Init Parameters

# displacement in x,y steps
prior_step = 100.0
# displacement in z with small steps
z_small_step = 200
# displacement in z with big steps
z_big_step = 10000
dic_mv = {'right': [-1, 0], 'left': [1, 0],
          'up': [0, -1], 'down': [0, 1]}
dic_mvz = {'up': 'N', 'down': 'F'}
list_pos = []              # list of the positions given to the mda
dic_pos_gate = {}          # dictionary pos <--> gate
modif_pos = 0
reload_pos = []
currview = 'simple'
dic_displ_obj = {'20x': 0.780, '40x': 0.390, '60x': 0.260, '100x': 0.156}
predefined_mda = True
monitor_params = {'mail': False, 'teams': False, 'delay_messages': 20}
kind_focus = 'afml_sweep'    # kind of autofocus used
afml_optim = 'max'     # 'steep_max_left' # 'steep_right' # 'max'
