import numpy as np


class Image(object):
    '''
    Image class for loading and manipulating preview images in
    GRecoMan.
    '''
    def __init__(self, img_path):
        self.min_val = np.float
        self.max_val = np.float
        self.path = img_path
        self.img_mat = []  # image matrix from reconstructed single slice
        self.img_width = []
        self.img_height = []
        self.img_disp = []  # image matrix for displaying in GRecoMan

        # (1) Read DMP
        self.readDMP()

        # (2) Standard normalization
        self.normalizeImage()

    def readDMP(self):
        ''' Opens DMP-file from the path stored in "path" property '''
        fd = open(self.path, 'rb')
        datatype = 'h'
        numberOfHeaderValues = 3
        headerData = np.zeros(numberOfHeaderValues)
        headerData = np.fromfile(fd, datatype, numberOfHeaderValues)
        imageShape = (headerData[1], headerData[0])
        self.img_mat = np.fromfile(fd, np.float32, -1)
        self.img_mat = self.img_mat.reshape(imageShape)

        self.min_val = np.min(self.img_mat)
        self.max_val = np.max(self.img_mat)

        self.img_width = imageShape[1]
        self.img_height = imageShape[0]

    def normalizeImage(self, min_str='', max_str=''):
        ''' Rescale gray values of image by min and max values '''
        if min_str == '':
            min = self.min_val
        else:
            min = np.float(min_str)
        if max_str == '':
            max = self.max_val
        else:
            max = np.float(max_str)

        img_tmp = self.img_mat[:][:] - min
        img_tmp /= max

        img_tmp[img_tmp < 0] = 0
        img_tmp[img_tmp > 1] = 1
        
        # img_32bit_to_8bit
        self.img_disp = (img_tmp * 255).astype(np.uint32)
        self.img_disp = (255 << 24 | (self.img_disp) << 16 | (self.img_disp)
                         << 8 | (self.img_disp)).flatten()
                         
    def intMinMax2FloatMinMax(self, int_min, int_max, range):
        '''
        Takes inter min/max values as well as an integer range value
        and rescales these values to min/max float values from the
        image object.
        '''
        range_float = self.max_val - self.min_val
        scale_min = np.float(int_min)/range
        scale_max = np.float(int_max)/range
        
        min = self.min_val + scale_min * range_float
        max = self.min_val + scale_max * range_float
        
        return min, max
    
    def floatMinMax2IntMinMax(self, float_min, float_max, range):
        '''
        Takes float min/max values as well as an int range value
        and rescales these values to min/max int values from the
        image object.
        '''
        range_float = self.max_val - self.min_val
        
        min = ( np.float(float_min) - self.min_val ) / \
                range_float * np.float(range)
        max = ( np.float(float_max) - self.min_val ) / \
                range_float * np.float(range)
        
        if min < 0:
            min = 0
        if max >10000:
            max = range
        
        return int(min), int(max)