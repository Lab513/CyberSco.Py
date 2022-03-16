from time import sleep


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
            for elem in self.list:
                elem.loop()                   # trigger the loop of elem
            # delay between the iterations in minutes
            sleep(self.time_rep*60)
