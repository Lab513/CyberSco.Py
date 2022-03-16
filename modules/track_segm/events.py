import numpy as np
from PIL import Image


class EVENTS():
    '''
    Events
    '''

    def __init__(self):
        '''
        '''


    def read_tiff(self, addr_img):
        '''

        '''

        img = Image.open(addr_img).convert('L')
        img = np.array(img).astype(np.double)

        return img

    def make_slices(self, w=30):
        '''
        Slices for capturing mitosis event
        '''

        py, px = self.pos_obs_cells
        print(f"#### posx, posy : {px}, {py}")
        sx, sy = slice(px-w, px+w), slice(py-w, py+w)

        return sx, sy

    def find_indices_events(self):
        '''
        Indices of cells associated to buds in buds detection etc..
        '''

        self.list_indices_events = []
        try:
            for i, pos in enumerate(self.list_pos_events):
                ind = self.find_nearest_index(i, self.list_pos_events)
                self.list_indices_events.append([ind, pos])
                # circle at event position
                self.circle_at_pos(pos, radius=20)
            print(f"self.list_indices_events is "
                  f"{self.list_indices_events} !!!")
            #self.extract_region_rfp(cell_nb=0)
        except:
            print('No events')
