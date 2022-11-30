
class MDA_SIMU():
    '''
    '''
    def __init__(self):
        '''
        '''
    def simulation_launch_loop(self, debug=[]):
        '''
        Simulation for testing plateaux
        No action..
        '''
        self.first_time = datetime.now()
        self.num_plat = 0
        self.lthr_cells = [250,500,600]        # list of thresholds
        self.plateau_duration = 1              # plateau duration in minutes
        ##
        ##
        pos = POS(self.ldevices, self.mod0)
        pos.num = 0
        pos.num_gate = 1
        pos.dir_mda_temp = self.dir_mda_temp
        self.list_pos = [pos]                                         # instantiate the positions and fill them with the devices
        ##
        for rep in range(self.repeat):                             # Loop
            print(f'measurement n° {int(rep) + 1} ...')
            self.take_elapsed_time()
            for pos in self.list_pos:
                sleep(0.1)
                pos.nb_cells += 20
                pos.list_nb_cells += [pos.nb_cells]
            self.check_conditions(rep)                             # apply the conditions
            self.plot_nbcells_positions(rep)                       # plot the number of cells
            self.message_end_measurement(rep)
            if rep < self.repeat-1:
                self.delay_sleep()                                 # respect delay between each beginning of measurments
        self.save_nbcells_positions()                              # save the list of nb cells in yaml file
        self.save_experim()                                        # save the mda with the date
        self.close_devices()                                       # close the serial port of all the devices

    def simulation_lag_sucrose(self, debug=[]):
        '''
        Simulation for testing lag sucrose
        No action..
        '''
        self.first_time = datetime.now()
        self.lthr_cells = [20, 50, 100, 250, 500]        # list of thresholds
        ##
        self.list_pos = []
        for i in range(5):
            self.list_pos += [POS(self.ldevices, self.mod0)]
            self.list_pos[i].num = i
            self.list_pos[i].thresh_cells = self.lthr_cells[i]
            self.list_pos[i].num_gate = i+1
            self.list_pos[i].dir_mda_temp = self.dir_mda_temp
        for rep in range(self.repeat):                             # Loop
            print(f'measurement n° {int(rep) + 1} ...')
            self.take_elapsed_time()
            for pos in self.list_pos:
                sleep(0.1)
                pos.nb_cells += 4
                pos.list_nb_cells += [pos.nb_cells]
            self.check_conditions(rep)                             # apply the conditions
            self.plot_nbcells_positions(rep)                       # plot the number of cells
            self.message_end_measurement(rep)
            if rep < self.repeat-1:
                self.delay_sleep()                                 # respect delay between each beginning of measurments
        self.save_nbcells_positions()                              # save the list of nb cells in yaml file
        self.save_experim()                                        # save the mda with the date
        self.close_devices()                                       # close the serial port of all the devices
