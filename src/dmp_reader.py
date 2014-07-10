import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def DMPreader(file):
    '''
    This function opens the DMP-file file and normalizes it by its
    min and max value
    TODO: has to be rewritten completely (next release)
    '''
    fd = open(file, 'rb' )
    datatype = 'h'
    numberOfHeaderValues = 3
    headerData = np.zeros(numberOfHeaderValues)
    headerData = np.fromfile(fd, datatype, numberOfHeaderValues)
    imageShape = (headerData[1], headerData[0])
    imageData = np.fromfile(fd, np.float32, -1)
    imageData = imageData.reshape(imageShape)
    
    # Normalize image
    imageData = imageData[:][:]-np.min(imageData)
    imageData /= np.max(imageData)

    img_32bit_to_8bit = (imageData * 255).astype(np.uint32)
    
    packed_img_array = (255 << 24 | (img_32bit_to_8bit) << 16 | (img_32bit_to_8bit) << 8 | (img_32bit_to_8bit)).flatten()
    img = QImage(packed_img_array, imageData.shape[1], imageData.shape[0], QImage.Format_RGB32)
    return QPixmap.fromImage(img)


if __name__ == "__main__":
    # TESTING ground
    asdf = DMPreader('/afs/psi.ch/user/l/lovric_g/slsbl/x02da/e13657/Data10/disk1/mouseA_01_01_/fltp/mouseA_01_01_0001.fltp.DMP')
