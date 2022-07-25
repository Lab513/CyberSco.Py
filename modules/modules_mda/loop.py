from time import sleep, time


class LOOP():
    '''
    Loop over positions
    '''

    def __init__(self, nb_rep, time_rep):
        '''
        nb_rep : number of repetions of the loop
        time_rep : time between repetitions in the loop (in minutes)
        '''
        self.list = []                  # list of elements over which to loop
        self.nb_rep = int(nb_rep)              # number of repetitions
        self.time_rep = float(time_rep)        # repetition time

    def loop(self):
        '''
        execute the loop
        '''
        for _ in range(self.nb_rep):
            t0 = time()
            for elem in self.list:
                elem.loop()                   # trigger the loop of elem
            # delay between the iterations in minutes
            t1 = time()
            t_meas = round(t1-t0,2)
            print(f'time for measurement is {t_meas}')
            # removing measurement time from repetition delay..
            tsleep = self.time_rep*60-t_meas
            sleep(tsleep)
