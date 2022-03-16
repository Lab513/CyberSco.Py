class MASKS():
    '''
    Masks
    '''

    def make_mask_nuclei(self):
        '''
        '''
        self.img_mask_nuclei = self.img_mask.copy()
        self.img_mask_nuclei[ self.img_mask > self.thresh_nuclei ] = 255                         # enhance the prediction mask
        self.img_mask_nuclei[ self.img_mask < self.thresh_nuclei ] = 0

    def prepare_masks(self, debug=0):
        '''
        Thresholding, dilation and erosion
        '''
        if debug>0:
            print(f"##### in make_mask, self.thresh_after_pred is {self.thresh_after_pred}")
        if self.thresh_after_pred:
            self.img_mask[ self.img_mask > self.thresh_after_pred ] = 255                      # threshold up to 255
            try:
                self.img_mask_event[ self.img_mask_event > self.thresh_after_pred ] = 255
            except:
                print('cannot change mask for img_mask_event')

        if self.args.dilate_after_pred:
            self.dilate_mask_shapes()                                                          # dilate the shapes in the mask before finding contours
            self.morph_open(iter=10)

        if self.args.erode_after_pred:
            self.erode_mask_shapes(erd_size=self.erode_for_track, iter=self.iter_erode_for_track)                                                          # erode the shapes in the mask before finding contours
            #self.morph_open(iter=10)
