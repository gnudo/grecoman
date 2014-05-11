###########################################################
###########################################################
####                                                   ####
####               SINGLE SLICE ROUTINE                ####
####                                                   ####
###########################################################
###########################################################


####  Routine called by the GUI -- GReco-man to perform
####  reconstruction of a single slice with ring removal
####  performed in advance on the sinogram ( optional ),
####  before submitting it to gridrec.
####
####  Example of bash command line to run the script:
####  ./singleSliceFunc.py -W "-y db2 -M sym -V 3:8 -E 12" -F shepp
####  -Z 0.5 -t 0 -a 0 -Di /sls/X02DA/data/e13657/Data10/disk1/mouseA_01_01_/sin/
####  -i mouseA_01_01_0001.sin.DMP



####  GENERIC PYTHON MODULES
import sys
import os
import numpy as np
import argparse




###########################################################
###########################################################
####                                                   ####
####                GET INPUT ARGUMENTS                ####
####                                                   ####
###########################################################
###########################################################

def getArgs():
    parser = argparse.ArgumentParser(description='''
                                                 Wrapper to run GRIDREC and
                                                 SIN2REC2 on multiple cores
                                                 ''' ,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument( '-Di' , dest='pathin' , default='./',
                        help = 'Path to the input sinogram' )
    parser.add_argument( '-i' , dest='sino' ,
                        help = 'Select filename of the sinogram to be reconstructed')
    parser.add_argument( '-Do' , dest='pathout' ,
                        help = 'Output folder' )
    parser.add_argument( '-o' , dest='reco' ,
                        help = 'Select filename of the ouput reconstruction' ) 
    parser.add_argument( '-F' , dest='filter' , default='shepp-logan' ,
                        help = 'Select filter for the reconstruction with gridrec' )
    parser.add_argument( '-Z' , dest='edgepad' , type=np.float32 , default=0.5 ,
                        help = 'Select edge padding for reconstruction with gridrec' )
    parser.add_argument( '-g' , dest='geometry' , default='1',
                        help = 'Specify projection geometry for gridrec:'
                               +' 0 (projections angles specified in'
                               +' a file, named angles.txt), 1 (homogeneous'
                               +' sampling between 0 and pi) and (homogeneous'
                               +' sampling between 0 and 2pi); default=1' )
    parser.add_argument( '-c' , dest='center' , type=np.float32 , 
                        help = 'Select the center of rotation axis' ) 
    parser.add_argument( '-t' , dest='file_type' , default = '0' ,
                        help = 'Select edge padding to the input sinogram (as '
                        +' percentage of the width of the sinogram)' )
    parser.add_argument( '-a' , dest='angle_start' , default = '0' ,
                        help = 'Select edge padding to the input sinogram (as '
                        +' percentage of the width of the sinogram)' )
    parser.add_argument( '-y' , dest='wavelet_type' , 
                        help = 'Specify wavelet type for ring removal' )
    parser.add_argument( '-M' , dest='edgepad_type' , 
                        help = 'Specify edge padding type for ring removal' )
    parser.add_argument( '-V' , dest='multiresol' , 
                        help = 'Specify start and end resolution level' )
    parser.add_argument( '-E' , dest='sigma' , 
                        help = 'Specify sigma of the gaussian smoothing for ring removal' )
    parser.add_argument( '-z' , dest='zinger' , 
                        help = 'do apply zinger removal' )
    parser.add_argument( '-H' , dest='zinger_thresh' , 
                        help = 'Specify Threshold used in zinger removal routine' )
    parser.add_argument( '-w' , dest='zinger_width' , 
                        help = 'Width of smoothing kernel used in zinger removal routine' )

    args = parser.parse_args()

    if args.sino is None:
        parser.print_help()
        sys.exit('\nERROR: Input sinogram name not specified!\n')
    
    return args




###########################################################
###########################################################
####                                                   ####
####                     MAIN PROGRAM                  ####
####                                                   ####
###########################################################
###########################################################

def main():
    ##  Get input arguments
    args = getArgs()


    
    ##  Get input/output folders
    pathin = args.pathin
    if pathin[len(pathin)-1] != '/':
        pathin += '/'

    if args.pathout is None:
        curr_dir = os.getcwd()
        os.chdir( pathin )
        
        if os.path.isdir('../viewrec') is True:
            os.chdir( '../viewrec' )
            pathout = os.path.abspath('./')
        else:
            os.makedirs( '../viewrec' )
            os.chdir( '../viewrec' )
            pathout = os.path.abspath('./') 

        os.chdir( curr_dir )

    else:
        pathout = args.pathout

    if pathout[len(pathout)-1] != '/':
        pathout += '/' 

    print '\nSelected input folder:\n', pathin
    print 'Selected output folder:\n', pathout


    
    ##  Get input sinogram
    sino_file = args.sino
    print '\nSelected input sinogram:\n', sino_file 


    
    ##  Ring removal
    flag_ring_removal = 0

    if args.wavelet_type is not None:
        command_line = 'python ring_removal_waveletfft.py '
        command_line += '-Di ' + pathin + ' '
        command_line += '-i ' + sino_file + ' '
        command_line += '-Do ' + pathout + ' '
        command_line += '-t ' + args.wavelet_type + ' '
        command_line += '-M ' + args.edgepad_type + ' '
        command_line += '-d ' + args.multiresol + ' '
        command_line += '-f ' + args.sigma + ' '

        print command_line

        os.system( command_line )
        flag_ring_removal = 1



    ##  Reconstruction with gridrec
    command_line = 'gridrec_64 '
    command_line += '-f ' + args.filter + ' '
    command_line += '-Z ' + str( args.edgepad ) + ' '
    if args.center is not None:
        command_line += '-c ' + str( args.center ) + ' '
    if args.angle_start is not None:
        command_line += '-r ' + str( args.angle_start ) + ' '
    if args.file_type is not None:
        command_line += '-t ' + args.file_type + ' '
    if args.zinger is not None:
        command_line += '-z ' + args.zinger + ' '
    if args.zinger_thresh is not None:
        command_line += '-T ' + args.zinger_thresh + ' '
    if args.zinger_width is not None:
        command_line += '-k ' + args.zinger_width + ' '
    command_line += '-O ' + pathout + ' '

    if flag_ring_removal:
        command_line += '-D ' + pathout + ' '
        name_file = sino_file[:len(sino_file)-4]
        command_line += name_file + '_destrip.DMP'
        print command_line
        os.system( command_line )
        print 'rm ' + pathout + name_file + '_destrip.DMP'
        os.system('rm ' + pathout + name_file + '_destrip.DMP')
        reco = pathout + name_file + '_destrip.rec.DMP'        
        reco_new = reco.replace('.sin_destrip','')
        print reco 
        os.system( 'mv ' + reco + ' ' + reco_new )
        print 'mv ' + reco + ' ' + reco_new         

    else:
        command_line += '-D ' + pathin + ' '
        command_line += sino_file
        os.system( command_line ) 

    return 0




###########################################################
###########################################################
####                                                   ####
####                     CALL TO MAIN                  ####
####                                                   ####
###########################################################
###########################################################

if __name__ == '__main__':

    ##  Call to main
    main()
