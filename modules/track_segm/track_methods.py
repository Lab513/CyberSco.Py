import copy
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.linalg import norm
from time import time


class TRACK_METH():
    '''
    '''
    def __init__(self):
        self.rint = np.random.randint
        self.simple_cntr = np.array([[2, 2], [7, 1],
                                    [15, 5], [25, 25], [10, 35]])
        #self.rec_perms = open('..processings')

    def swap(self, ind, ind_min, debug=[]):
        '''
        swapping ind and ind_min
        '''
        if 1 in debug:
            print(f'swapping {ind} with {ind_min}')
        if 2 in debug:
            print(f'** {ind_min} goes at place {ind}')
        list_obj_curr = [self.l_curr]
        try:
            list_obj_curr.append(self.curr_contours)
        except:
            print("no self.curr_contours")
        for obj in list_obj_curr:
            buff = copy.deepcopy(obj[ind])
            obj[ind] = copy.deepcopy(obj[ind_min])
            obj[ind_min] = copy.deepcopy(buff)

    def apply_min_corr(self, ind, ind_min):
        '''
        Swap and block
        '''
        if ind_min not in self.lmodif:
            try:
                self.swap(ind, ind_min)   # swap in self.list_imgs[i]
            except:
                print(f'cannot swap with {ind_min}')
            self.lmodif.append(ind)     # block the point repositionned

    def find_nearest_index(self, p):
        '''
        ind_min = index of the nearest point in the new list
        '''
        ldist = []
        for q in self.l_curr:    # new points
            ldist += [norm(p-q)**2]
        arr_dist = np.array(ldist)
        ind_min = np.argmin(arr_dist)

        return ind_min

    def find_nearest_index_reverse(self, ind_min):
        '''
        ind_min = index of the nearest point in the new list
        '''
        ldist = []
        p = self.l_curr[ind_min]
        for q in self.l_prev:    # prev points
            ldist += [norm(p-q)**2]
        arr_dist = np.array(ldist)
        ind_min_rev = np.argmin(arr_dist)

        return ind_min_rev

    def far_contours(self):
        '''
        Add a contour far away
        '''
        rand_cntr = self.simple_cntr + self.rint(1e3, 1e4, 1)
        # random contour very far away
        self.curr_contours.append(rand_cntr)

    def far_neighb(self, debug=0):
        '''
        Send the disappearing points far
        '''
        lprev = len(self.l_prev)
        lcurr = len(self.l_curr)
        if lcurr < lprev:
            for _ in range(lprev-lcurr):
                self.l_curr.append(np.array(self.rint(1e3, 1e4, 2)))
                try:
                    self.far_contours()
                except:
                    if debug > 0:
                        print("no contours to prolongate")

    def bijective_nearest(self, ind, p, debug=0):
        '''
        Find the nearest and check it is in both directons..
        '''
        ind_min = self.find_nearest_index(p)
        # must be equal to ind, bijective
        ind_min_rev = self.find_nearest_index_reverse(ind_min)
        if debug > 0:
            print(f'## ind {ind}, ind_min {ind_min},'
                  ' ind_min_rev {ind_min_rev}')
        biject = (ind_min_rev == ind)

        return biject, ind_min

    def adapt_lists(self, l_prev, l_curr, debug=[]):
        '''
        Pass from list of tuples to list of numpy arrays
        '''
        if 1 in debug:
            print(f"type(l_curr[0]) is {type(l_curr[0])}")
        if isinstance(l_curr[0], tuple):
            self.orig_type_l_curr = 'tuple'
            if 2 in debug:
                print("found the type tuple !!!")
            self.l_prev = [np.array(list(e)) for e in l_prev]
            self.l_curr = [np.array(list(e)) for e in l_curr]
        else:
            self.orig_type_l_curr = 'numpy_array'
            self.l_prev, self.l_curr = l_prev, l_curr

    def translate_to_tuple(self):
        '''
        Pass from list  of numpy arrays to list
         of tuples for track_segmentation format
        '''
        l_prev = [tuple(p) for p in self.l_prev]
        l_curr = [tuple(p) for p in self.l_curr]
        return l_prev, l_curr

    def pass_back_to_tuple(self, debug=0):
        '''
        '''
        if self.orig_type_l_curr == 'tuple':
            try:
                if debug > 0:
                    print('#**## passing back values'
                          ' of self.list_prev_pos and self.list_pos ')
                    print(f'**** self.list_pos is'
                          f' at the end {self.list_pos} ')
                self.list_prev_pos, self.list_pos = self.translate_to_tuple()
            except:
                print('cannot pass from array'
                      ' to tuple at the end of the tracking step')

    def meth_min(self, l_prev, l_curr, corr=False, debug=[]):
        '''
        Simple min method, finding the nearest point
        '''
        print('Greedy method')
        t0 = time()
        self.adapt_lists(l_prev, l_curr)
        self.lmodif = []
        self.far_neighb()         # send the disappearing element far away..
        for ind, p in enumerate(self.l_prev):    # previous points
            #print(f"type of p is {type(p)}")
            biject, ind_min = self.bijective_nearest(ind, p)
            if corr and biject:     # bijection
                self.apply_min_corr(ind, ind_min)
            if 1 in debug:
                print(f'{ind}/{ind_min}')
        self.pass_back_to_tuple()
        t1 = time()
        telapsed = round((t1-t0)/60, 2)
        print(f'time elapsed for tracking is {telapsed} min')

    def adapt_size(self, debug=0):
        '''
        Adapt size l_curr when shorter
        '''
        print("## adapt_size")
        lprev, lcurr = len(self.l_prev), len(self.l_curr)
        if lcurr < lprev:
            for _ in range(lprev-lcurr):
                self.l_curr.append(0)
                try:
                    self.curr_contours.append(self.simple_cntr)
                except:
                    if debug > 0:
                        print('no contours')
        print(f"### len(self.l_curr) =  {len(self.l_curr)}")

    def lcurr_shorter(self, debug=0):
        '''
        '''
        print('### shorter !!')
        self.hung_list = self.row_ind
        self.sorted_list = [np.array(self.rint(1e3, 1e4, 2))]*len(self.l_prev)
        self.sorted_list_cntrs = [self.simple_cntr]*len(self.l_prev)
        self.adapt_size()
        for i, j in enumerate(self.row_ind):
            self.sorted_list[j] = copy.deepcopy(self.l_curr[i])
            try:
                self.sorted_list_cntrs[j] =\
                    copy.deepcopy(self.curr_contours[i])
            except:
                if debug > 0:
                    print('no contours')

    def insert_new_points(self, debug=0):
        '''
        Add the new points at the end of the list
        '''
        for j in range(len(self.l_curr)):
            if j not in self.col_ind:
                for k in range(len(self.l_curr)):
                    if isinstance(self.sorted_list[k], int):  # k == 0
                        self.sorted_list[k] = copy.deepcopy(self.l_curr[j])
                        try:
                            self.sorted_list_cntrs[k] =\
                              copy.deepcopy(self.curr_contours[j])
                        except:
                            if debug > 0:
                                print('no contours')
                        break

    def lcurr_longer(self, debug=[]):
        '''
        '''
        print('### longer !!')
        self.hung_list = self.col_ind
        self.sorted_list = [0]*len(self.l_curr)
        self.sorted_list_cntrs = [0]*len(self.l_curr)
        #self.adapt_size()
        if 1 in debug:
            print((f"### self.row_ind, "
              "self.col_ind {self.row_ind, self.col_ind} "))
        for i, j in enumerate(self.col_ind):
            self.sorted_list[i] = copy.deepcopy(self.l_curr[j])   # old points
            try:
                self.sorted_list_cntrs[i] =\
                    copy.deepcopy(self.curr_contours[j])
            except:
                if 2 in debug:
                    print('no contours')
        self.insert_new_points()  # adding the new points at the end

    def assign_with_hung_mat(self, show_mat=False, debug=[]):
        '''
        '''
        hung_mat = []
        for p in self.l_prev:                              # previous points
            ldist = []
            for q in self.l_curr:                          # new points
                ldist += [norm(p-q)**2]
            hung_mat += [ldist]
        if show_mat:
            print(f"hung_mat {hung_mat}")
        self.row_ind, self.col_ind = linear_sum_assignment(hung_mat)
        if self.show_assign:
            print(f"## row_ind, col_ind {self.row_ind, self.col_ind}")

    def apply_permutations_correction(self, debug=0):
        '''
        '''
        for i, p in enumerate(self.sorted_list):
            self.l_curr[i] = copy.deepcopy(p)
        try:
            for i, c in enumerate(self.sorted_list_cntrs):
                self.curr_contours[i] = copy.deepcopy(c)
        except:
            if debug > 0:
                print('no contours')

    def debug_changes_found(self):
        '''
        '''
        for j, ind in enumerate(self.hung_list):
            print(f'{j}/{ind}')

    def meth_hung(self, l_prev, l_curr, corr=False,
                  show_assign=False, debug=[]):
        '''
        Hungarian method
        '''
        print('Hungarian method')
        self.show_assign = show_assign
        if 4 in debug:
            print(f'## l_prev {l_prev}')
            print(f'## l_curr {l_curr}')
        self.adapt_lists(l_prev, l_curr)
        diff = len(l_curr)-len(l_prev)
        print(f"diff (lcurr-lprev) is {diff}")
        if corr:
            if 1 in debug:
                print(f'## self.l_curr before {self.l_curr}')
            self.assign_with_hung_mat()
            if diff < 0:
                self.lcurr_shorter()
            else:
                self.lcurr_longer()
            if 2 in debug:
                print(f"len(self.sorted_list), len(self.l_curr) "
                      f"{len(self.sorted_list), len(self.l_curr)}")
            # change the initial vectors..
            self.apply_permutations_correction()
            if 1 in debug:
                print(f'## self.l_curr after {self.l_curr}')
            if 3 in debug:
                self.debug_changes_found()
        self.pass_back_to_tuple()
