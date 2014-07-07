from os import listdir
import os.path


class AdvancedChecks(object):
    '''
    class for implementing all methods that can be used for further advanced checking,
    once the INPUT directory has been set.
    '''
    def __init__(self,parent):
        '''
        constructor
        '''
        self.inputdir = []
        self.sinodir = []
        self.fltpdir = []
        self.cprdir = []
        self.recodir = []
        self.homedir = os.path.expanduser('~')
        self.runningdir = self.getParentDir(os.path.dirname(os.path.realpath(__file__)))
        self.parent = parent
        self.merlin_mount_dir = []
        self.merlin_base = '/gpfs/home/'
        
        
    def initInputDirectory(self):
        '''
        method that is called when a new inputdirectory is set
        '''
        self.inputdir = os.path.join(str(self.parent.inputdirectory.text()),'')
        
        ## Clear old sino dirs
        self.parent.sindirectory.setText('')
        self.sinodir = ''
        
        if not self.inputdir or not os.path.isdir(self.inputdir):
            return
        
        self.parent.lastdir = self.getParentDir(str(self.inputdir))
        
        if self.determineInputType():
            self.determinePrefix()
        
        # We set all I/O folders
        dirs = ['sin','cpr','fltp','reco']
        for item in dirs:
            self.checkFolder(idem)
        
        ## TODO: check scan parameters from log file etc. etc.
        self.loadAndParseLogFile()
        
        
    def initSinDirectory(self):
        '''
        method that is run when a sinogram directory is set, either through
        user or automatically when setting input directory.
        if the sinogram-directory exist it populates the sino-combobox, otherwise it displays an
        error message
        '''
        self.parent.sinograms.clear()  # clear sin combo box
        self.sinodir = os.path.join(str(self.parent.sindirectory.text()),'')
        
        if not os.path.exists(self.sinodir):
            self.parent.displayErrorMessage('"sin" folder missing','No sinograms found in standard sin folder')
            return
        
        tif_list = [name for name in os.listdir(self.sinodir)
                    if name.lower().endswith('.tif') and not name.startswith('.')]
        dmp_list = [name for name in os.listdir(self.sinodir)
                    if name.lower().endswith('.dmp') and not name.startswith('.')]
        
        dmp_list = tif_list + dmp_list
        dmp_list.sort()
        for item in dmp_list:
            self.parent.sinograms.addItem(item)
            
            
    def checkFolder(self,mode):
        '''
        This method sets the respective I/O directory ("mode"),
        checks whether it exists and issues a warning. In case of the
        reco-output dir, the correct suffix is appended according to
        the combo-box (outputtype) and in case of the sin-directory,
        the "initSinDirectory" is launched.
        '''
        inputdir = os.path.join(str(self.inputdir),'')
        dir = os.path.join(self.getParentDir(inputdir),mode)
        setattr( self, mode+'dir', os.path.join(dir,'') )
        dir_handle = getattr(self,mode+'dir')
        if os.path.exists(dir_handle):
            self.parent.displayErrorMessage('Existing directory',\
                    'You should probably rename the '+mode+'-directory!')
        
        getattr(self.parent,mode+'directory').setText(dir_handle)
        
        if mode == 'reco':
            self.setOutputDirectory('rec_8bit')
        elif mode == 'sin':
            self.initSinDirectory()
        
        
    def setOutputDirectory(self,newname):
        '''
        Methods sets the correct output directory for reconstructions
        according to the respective combo-box.
        '''
        outputpaths = os.path.join(str(self.parent.recodirectory.text()),'')
        outputpaths = self.splitOsPath(outputpaths)
        newpathlist = outputpaths[:-2]+[newname]
        pathstr = self.glueOsPath(newpathlist)
        self.parent.recodirectory.setText(pathstr)
            
            
    def afsPath2Cons2(self,path):
        '''
        transforms a blmount-filepath to the file path that can be run from a beamline computer
        such as cons2
        '''
        splitted_dir = self.splitOsPath(str(path))
        splitted_dir.append('')
        sls_base_dir = self.splitOsPath('/sls/X02DA/data/')
        tmp_list = sls_base_dir+splitted_dir[8:]
        return os.path.join(*tmp_list)
    
    
    def cons2Path2afs(self,path):
        '''
        transforms a cons2 file path to a filepath that can be opened from an AFS account
        '''
        splitted_dir = self.splitOsPath(str(path))
        home = os.path.expanduser("~")
        afs_base = self.splitOsPath(home+'/slsbl/x02da/')
        tmp_list = afs_base+[splitted_dir[4]]+splitted_dir[5:]
        return os.path.join(*tmp_list)
    
    
    def sshfsPath2Merlin(self,path):
        '''
        transforms a mounted Merlin path to the original Merlin path 
        '''        
        split_merlin_mount = self.splitOsPath(str(self.merlin_mount_dir))
        splitted_dir = self.splitOsPath(str(path))
        tmp_list = [self.merlin_base+self.parent.job.merlinuser]+splitted_dir[len(split_merlin_mount)-1:]
        return os.path.join(*tmp_list)
    
    def merlin2SshfsPath(self,path):
        '''
        transforms original Merlin path to a mounted Merlin path 
        '''
        split_merlin_base = self.splitOsPath(str(self.merlin_base))
        splitted_dir = self.splitOsPath(str(path))
        tmp_list = [self.merlin_mount_dir]+splitted_dir[len(split_merlin_base):]
        return os.path.join(*tmp_list)
        
        
    def splitOsPath(self, path):
        '''
        OS path splitter
        '''
        parts = []
        while True:
            path_tmp, rest = os.path.split(path)
            if path_tmp == path:
                assert not rest
                if path:
                    parts.append(path)
                break
            parts.append(rest)
            path = path_tmp
        parts.reverse()
        return parts
    
    
    def glueOsPath(self, pathlist):
        '''
        join list to an OS path
        '''
        newpath = pathlist[0]
        for item in pathlist[1:]:
            newpath = os.path.join(newpath,item)
        return newpath
    
    
    def getParentDir(self,directory):
        '''
        method that returns the parent directory of a directory
        '''
        directory = os.path.join(directory,'')
        tmp_dir = os.path.split(directory[:-1])
        return os.path.join(tmp_dir[0],'')
        
        
    def loadAndParseLogFile(self):
        '''
        load log-file and set GUI fields from the log-file automatically
        '''
        for name in os.listdir(self.inputdir):
            if name.lower().endswith('.log') and not name.startswith('.'):
                logfile = name
                break
        else: # if for-loop is run w/o break
            return
        
        logfile_handle = open(os.path.join(str(self.inputdir),logfile), 'r')
        # Go through all the lines in the logfile
        for line in logfile_handle:
            # Only do this for existing lines
            if len(line.split()) > 0:
                
                # Scan parameters
                if (line.split()[0] == 'Number' and
                        line.split()[2] == 'projections'):
                    self.parent.raws.setText(str(line.split(':')[1]).strip())
                elif (line.split()[0] == 'Number' and line.split()[2] == 'darks'):
                    self.parent.darks.setText(str(line.split(':')[1]).strip())
                elif (line.split()[0] == 'Number' and line.split()[2] == 'flats'):
                    self.parent.flats.setText(str(line.split(':')[1]).strip())
                elif (line.split()[0] == 'Number' and line.split()[2] == 'inter-flats'):
                    self.parent.interflats.setText(str(line.split(':')[1]).strip())
                elif (line.split()[0] == 'Flat' and line.split()[1] == 'frequency'):
                    self.parent.flatfreq.setText(str(line.split(':')[1]).strip())
                
                # Beam Energy
                elif (line.split()[0] == 'Beam' and line.split()[1] == 'energy'):
                    self.parent.pag_energy.setText(str(line.split(':')[1]).strip())
                    
                # Magnification and pixel size
                elif (line.split()[0] == 'Actual' and line.split()[1] == 'pixel'):
                    self.parent.pag_pxsize.setText(str(line.split(':')[1]).strip()+'E-6')
    
    
    def determineInputType(self):
        '''
        method for checking and setting input type
        '''
        for imgfile in listdir(self.inputdir):
            if imgfile.lower().endswith(".tif"):
                self.parent.inputtype.setCurrentIndex(2)
                self.filetype = 'tif'
                return True
            elif imgfile.lower().endswith(".dmp"):
                self.parent.inputtype.setCurrentIndex(0)
                self.filetype = 'dmp'
                return True
            elif imgfile.lower().endswith(".HD5"):
                self.parent.inputtype.setCurrentIndex(1)
                self.filetype = 'hd5'
                return True
        else:
            self.parent.displayErrorMessage('No images found', 'There are no tif, dmp, nor hd5 files in the input folder!')
            return False

            
    def determinePrefix(self):
        '''
        the prefix is determined from the parent directory name of the tif-folder
        '''
        prefix = self.splitOsPath(str(self.inputdir))[-3]
        self.parent.prefix.setText(prefix)
        self.parent.jobname.setText(prefix)
        
        
    def rewriteDirectoryPath(self,path,mode):
        '''
        This method should rewrite any absolute directory path to a
        correct path for the target machine. We distinguish two modes:
        (i) forward means that the paths are given on the local machine
        and are transformed to work on the remote machine.
        (ii) backward means the paths from the remote machine are
        transformed to be used on the local machine
        '''
        path = os.path.join(str(path),'')
        if mode == 'forward':
            if self.parent.afsaccount.isChecked():
                if self.parent.target == 'x02da':
                    path = self.afsPath2Cons2(path)
                elif self.parent.target == 'Merlin':
                    path = self.sshfsPath2Merlin(path)
            elif self.parent.cons2.isChecked():
                pass
            return path
        elif mode == 'backward':
            if self.parent.afsaccount.isChecked():
                if self.parent.target == 'x02da':
                    path = self.cons2Path2afs(path)
                elif self.parent.target == 'Merlin':
                    path = self.merlin2SshfsPath(path)
            elif self.cons2.isChecked():
                pass
            return path


if __name__ == "__main__":
    # TESTING ground
    print os.path.exists('/Users/goranlovric/Desktop/asdf')
    print os.path.exists('/Users/goranlovric/Desktop/')
    print os.path.split('/Users/goranlovric/Desktop')
    test = AdvancedChecks('asdf')
    print test.sshfsPath2Merlin('/afs/psi.ch/user/l/lovric_g/Desktop/merlin2/Data10/disk1/mouseB_03_01_/sin-3/mouseB_03_01_1065.sin.DMP')