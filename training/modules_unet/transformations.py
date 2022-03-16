import cv2

class TRANSFORMATIONS():
    '''
    Modify shapes
    '''

    def morph_open(self, iter=3):
        '''
        open shapes in the mask
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        self.img_mask = cv2.morphologyEx(self.img_mask, cv2.MORPH_OPEN, kernel, iterations=iter)

    def dilate_mask_shapes(self, dil_size=3, iter=1):
        '''
        dilate prediction mask
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ( dil_size, dil_size ))
        #kernel = np.ones((dil_size,dil_size), np.uint8); square kernel
        self.img_mask = cv2.dilate(self.img_mask, kernel, iterations = iter)

    def erode_mask_shapes(self, erd_size=3, iter=1):
        '''
        erode prediction mask
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ( erd_size, erd_size ))
        #kernel = np.ones((dil_size,dil_size), np.uint8); square kernel
        self.img_mask = cv2.erode(self.img_mask, kernel, iterations = iter)
