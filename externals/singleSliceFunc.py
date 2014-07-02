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
####  python /afs/psi.ch/project/tomcatsvn/executeables/grecoman/externals/singleSliceFunc.py 
####  -F shepp -Z 0.5 -t 0 -a 0 --Di /sls/X02DA/data/e13657/Data10/disk1/mouseA_01_01_/sin/
####  -i mouseA_01_01_0001.sin.DMP -y db2 -M sym -V 3:8 -E 12



####  GENERIC PYTHON MODULES
import sys
import os
from optparse import OptionParser 





###########################################################
###########################################################
####                                                   ####
####                GET INPUT ARGUMENTS                ####
####                                                   ####
###########################################################
###########################################################

def getArgs():
    parser = OptionParser()
    
    parser.add_option( '--Di' , dest='pathin' , default='./',
                        help = 'Path to the input sinogram [default: %default]' )
    parser.add_option( '-i' , dest='sino' ,
                        help = 'Select filename of the sinogram to be reconstructed')
    parser.add_option( '--Do' , dest='pathout' ,
                        help = 'Output folder' )
    parser.add_option( '-o' , dest='reco' ,
                        help = 'Select filename of the ouput reconstruction' ) 
    parser.add_option( '-F' , dest='filter' , default='shepp-logan' ,
                        help = 'Select filter for the reconstruction with gridrec [default: %default]' )
    parser.add_option( '-Z' , dest='edgepad' , type='float' , default=0.5 ,
                        help = 'Select edge padding for reconstruction with gridrec [default: %default]' )
    parser.add_option( '-G' , dest='geometry' , default='1',
                        help = 'Specify projection geometry for gridrec:'
                               +' 0 (projections angles specified in'
                               +' a file, named angles.txt), 1 (homogeneous'
                               +' sampling between 0 and pi) and (homogeneous'
                               +' sampling between 0 and 2pi); [default: %default]' )
    parser.add_option( '-c' , dest='center' , type='float' , 
                        help = 'Select the center of rotation axis' ) 
    parser.add_option( '-t' , dest='file_type' , default = '0' ,
                        help = 'Select edge padding to the input sinogram (as '
                        +' percentage of the width of the sinogram) [default: %default]' )
    parser.add_option( '-a' , dest='angle_start' , default = '0' ,
                        help = 'Select edge padding to the input sinogram (as '
                        +' percentage of the width of the sinogram) [default: %default]' )
    parser.add_option( '-y' , dest='wavelet_type' , 
                        help = 'Specify wavelet type for ring removal' )
    parser.add_option( '-M' , dest='edgepad_type' , 
                        help = 'Specify edge padding type for ring removal' )
    parser.add_option( '-V' , dest='multiresol' , 
                        help = 'Specify start and end resolution level' )
    parser.add_option( '-E' , dest='sigma' , 
                        help = 'Specify sigma of the gaussian smoothing for ring removal' )
    parser.add_option( '-z' , dest='zinger' , 
                        help = 'do apply zinger removal' )
    parser.add_option( '-H' , dest='zinger_thresh' , 
                        help = 'Specify Threshold used in zinger removal routine' )
    parser.add_option( '-w' , dest='zinger_width' , 
                        help = 'WIdth of smoothing kernel used in zinger removal routine' )
    parser.add_option( '-x' , dest='machine' , 
                        help = 'target machine, where the calculation takes place (Merlin or x02da)' )
    

    args , options = parser.parse_args()

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



    ##  Get input sinogram
    sino_file = args.sino
    print '\nSelected input sinogram:\n', sino_file

    
    
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


    
    ##  Set name of the output reconstruction and
    ##  check whether the reconstruction file already
    ##  exists: if yes, the reconstruction file gets 
    ##  deleted
    reco_new = pathout + sino_file[:len(sino_file)-7] + 'rec.DMP'

    if os.path.exists( reco_new ):
        os.remove( reco_new )
        print '\nFile: ', reco_new, 'already existing ---> it gets deleted'



    ##  Ring removal
    flag_ring_removal = 0
    
    if args.wavelet_type is not None:
        if args.machine == 'x02da':
            command_line = 'module load xbl/epd_free/7.3-2-2013.06; ' + \
                           'module load xbl/PyWavelets/0.2.2; '
        elif args.machine == 'Merlin':
            command_line = 'module use /opt/xbl-software/modulefiles-private; ' + \
                           'module load xbl/epd; ' + \
                           'module use /opt/xbl-software/modulefiles; ' + \
                           'module load xbl/PyWavelets; '
        else:
            parser.print_help()
            sys.exit('\nERROR: No target machine specified \n')
        
        command_line += 'python /afs/psi.ch/project/TOMCAT_pipeline/Beamline/tomcat_pipeline/src/Reconstruction/' + \
                       'waveletFFT.py '
#python waveletFFT.py -t db2 -d 8 -O h -f 5.0 -p ds_ -M sym -o /afs/psi.ch/user/s/studer_a1/BeamLines/Tomcat/tifFiles/corTest/ /afs/psi.ch/user/s/studer_a1/BeamLines/Tomcat/tifFiles/corTest/Hornby_a1661.tif                       
        command_line += '-t ' + args.wavelet_type + ' '
        command_line += '-d ' + args.multiresol + ' '
        command_line += '-O v '
        command_line += '-f ' + args.sigma + ' '
        command_line += '-M ' + args.edgepad_type + ' '         
        command_line += '-o ' + pathout + ' '        
        command_line += pathin + sino_file

        print command_line
        
        os.chdir(pathin)
        os.system( command_line )
        flag_ring_removal = 1



    ##  Reconstruction with gridrec
    if args.machine == 'x02da':
        command_line = 'gridrec_64 '
    elif args.machine == 'Merlin':
        command_line = '/afs/psi.ch/project/TOMCAT_pipeline/Merlin/tomcat_pipeline/src/Reconstruction/lib/gridRec '
        
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
    if args.geometry is not None:
        command_line += '-g ' + args.geometry + ' '
    command_line += '-O ' + pathout + ' '

    if flag_ring_removal:
        command_line += '-D ' + pathout + ' '
        command_line += 'x' + sino_file
        print command_line
        os.system( command_line )
        print 'rm ' + pathout + 'x' + sino_file
        os.system('rm ' + pathout + 'x' + sino_file )
        os.system('rm ' + pathout + 'difference.tif') 
        reco = pathout + 'x' + sino_file[:len(sino_file)-7] + 'rec.DMP'        
        print reco
        print reco_new
        os.system( 'mv ' + reco + ' ' + reco_new )
        print 'mv ' + reco + ' ' + reco_new         

    else:
        command_line += '-D ' + pathin + ' '
        command_line += sino_file
        os.chdir(pathin)
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
