import numpy as np


class Image(object):
    '''
    Image class for loading and manipulating preview images in
    GRecoMan.
    '''
    def __init__(self,img_path):
        self.min_val = []
        self.max_val = []
        self.path = img_path
        self.img_mat = []
        self.img_width = []
        self.img_height = []
        self.img_disp = []
       
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

    
    def normalizeImage(self, min = None, max = None):
        ''' Rescale gray values of image by min and max values '''
        if min is None:
            min = self.min_val
        if max is None:
            max = self.max_val
        
        img_tmp = self.img_mat[:][:] - min
        img_tmp /= max
        
        # img_32bit_to_8bit
        self.img_disp = (img_tmp * 255).astype(np.uint32)
        self.img_disp = (255 << 24 | (self.img_disp) << 16 | (self.img_disp) << 8 | (self.img_disp)).flatten()
    
    