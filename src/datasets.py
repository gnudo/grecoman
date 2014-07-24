from os import listdir, name
import os.path


class DatasetFolder(object):
    '''
    The "DatasetFolder" class represents the central frame for one
    complete tomographic dataset (including its directory paths and the
    log-file from the measurement). Thus it serves the purpose of
    performing all kinds of operations on input/output directories,
    mainly in terms of directory path operations.
    '''
    def __init__(self,parent):
        self.inputdir = []  ## probably also obsolete
        self.homedir = os.path.expanduser('~')
        self.runningdir = self.getParentDir(os.path.dirname(os.path.realpath(__file__)))
        self.parent = parent
        self.merlin_mount_dir = []
        self.afs_base = self.homedir+'/slsbl/x02da/'
        self.merlin_base = '/gpfs/home/'
        self.sls_base_dir = '/sls/X02DA/data/'
        
        if os.uname()[1] == 'x02da-cons-2':  # set computing location based on computer name
            parent.cons2.setChecked(1)
        
        if self.homedir[0:16] == '/afs/psi.ch/user':  # set location based on PSI/AFS home-dir
            parent.afsaccount.setChecked(1)
        
    def initInputDirectory(self):
        '''
        This method is called when a new input directory is set either
        by opening a file dialog from main.py or by copying the path
        in the respective field and pressing RETURN.
        It first determines the Input type from the file prefixes, then
        it runs "checkFolder" method for each subfolder. Finally it
        launches "loadAndParseLogFile" method for populating GUI fields
        from the log-file.
        '''
        self.inputdir = os.path.join(str(self.parent.inputdirectory.text()),'')
        
        if not self.inputdir or not os.path.isdir(self.inputdir):
            return
        
        self.parent.lastdir = self.getParentDir(str(self.inputdir))
        
        if self.determineInputType():
            self.determinePrefix()
        
        subdirs = ['sin','cpr','fltp','reco']
        for item in subdirs: # set all I/O folders and initialize
            self.checkFolder(item)
        
        self.loadAndParseLogFile()  # load GUI-fields from log-file
        
        
    def initSinDirectory(self):
        '''
        This method is run when a new sinogram directory is set either
        by opening a file dialog from main.py or by copying the path
        in the respective field and pressing RETURN. If the sinogram-
        directory exists, it populates the sinogram combobox with all
        file-names or displays an error if no sinograms exist. Then it
        sets the min and max range for the sino slider.
        '''
        self.parent.sinograms.clear()  # clear sinogram combo box
        self.sinodir = os.path.join(str(self.parent.sindirectory.text()),'')
        
        if not os.path.exists(self.sinodir):
            self.parent.displayErrorMessage('"sin" folder missing', \
                            'No sinograms found in standard sin folder')
            return
        
        tif_list = [name for name in os.listdir(self.sinodir)
                    if name.lower().endswith('.tif') and not name.startswith('.')]
        dmp_list = [name for name in os.listdir(self.sinodir)
                    if name.lower().endswith('.dmp') and not name.startswith('.')]
        
        dmp_list = tif_list + dmp_list
        dmp_list.sort()
        self.parent.sinograms.addItems(dmp_list) # Populate sino comboxbox
        
        self.parent.sinoslider.setMinimum(0)
        self.parent.sinoslider.setMaximum(len(dmp_list)-1)
        
            
    def checkFolder(self,subdir):
        '''
        This method sets the respective I/O directory ("subdir"),
        checks whether it exists and issues a warning. In case of the
        reco-output dir, the correct suffix is appended according to
        the combo-box (outputtype) and in case of the sin-directory,
        the "initSinDirectory" method is launched.
        '''
        dir = self.glueOsPath([self.getParentDir(self.inputdir),subdir,''])
        if os.path.exists(dir):
            self.parent.displayErrorMessage('Existing directory',\
                    'You should probably rename the '+subdir+'-directory!')
        
        getattr(self.parent,subdir+'directory').setText(dir)
        
        if subdir == 'reco':
            self.setOutputDirectory('rec_8bit')
        elif subdir == 'sin':
            self.initSinDirectory()
        
        
    def setOutputDirectory(self,newname):
        '''
        This method sets the correct output directory for
        reconstructions according to the respective combo-box.
        '''
        outputpaths = os.path.join(str(self.parent.recodirectory.text()),'')
        outputpaths = self.splitOsPath(outputpaths)
        newpathlist = outputpaths[:-2]+[newname]
        pathstr = self.glueOsPath(newpathlist)
        self.parent.recodirectory.setText(pathstr)
        
        
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
            elif self.parent.cons2.isChecked():
                pass
            return path
            
            
    def afsPath2Cons2(self,path):
        '''
        Transforms a blmount-filepath to a file path that can be run
        from a beamline computer such as x02da-cons-2.
        '''
        splitted_dir = self.splitOsPath(str(path))
        splitted_dir.append('')
        sls_base_dir = self.splitOsPath(self.sls_base_dir)
        tmp_list = sls_base_dir+splitted_dir[8:]
        return os.path.join(*tmp_list)
    
    
    def cons2Path2afs(self,path):
        '''
        Transforms a beamline computer file path to a filepath that can
        be opened from an AFS account.
        '''
        afs_base = self.splitOsPath(self.afs_base)
        splitted_dir = self.splitOsPath(str(path))
        tmp_list = afs_base+[splitted_dir[4]]+splitted_dir[5:]
        return os.path.join(*tmp_list)
    
    
    def sshfsPath2Merlin(self,path):
        '''
        Transforms a mounted Merlin path to the original Merlin path. 
        '''
        self.merlin_mount_dir = os.path.join(str(self.merlin_mount_dir),'')
        split_merlin_mount = self.splitOsPath(self.merlin_mount_dir)
        splitted_dir = self.splitOsPath(str(path))
        tmp_list = [self.merlin_base+self.parent.job.merlinuser]+ \
                    splitted_dir[len(split_merlin_mount)-1:]
        return os.path.join(*tmp_list)
    
    
    def merlin2SshfsPath(self,path):
        '''
        Transforms the original Merlin path to a mounted Merlin path.
        '''
        self.merlin_mount_dir = os.path.join(str(self.merlin_mount_dir),'')
        split_merlin_base = self.splitOsPath(str(self.merlin_base))
        splitted_dir = self.splitOsPath(str(path))
        tmp_list = [self.merlin_mount_dir]+splitted_dir[len(split_merlin_base):]
        return os.path.join(*tmp_list)
        
        
    def splitOsPath(self, path):
        '''
        This method splits any OS path to a list of folders and should
        be compatible on all platforms.
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
        ''' This method is the reverse to the "splitOsPath" '''
        newpath = pathlist[0]
        for item in pathlist[1:]:
            newpath = os.path.join(newpath,item)
        return newpath
    
    
    def getParentDir(self,directory):
        ''' Returns the parent directory of a directory '''
        directory = os.path.join(str(directory),'')
        tmp_dir = os.path.split(directory[:-1])
        return os.path.join(tmp_dir[0],'')
        
        
    def loadAndParseLogFile(self):
        '''
        This method loads the log-file and sets GUI fields automatically.
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
            if len(line.split()) > 0: # Only do this for existing lines
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
        ''' Determines the input type based on the file extension '''
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
        This method determines the prefix from the parent directory
        name in respect to the tif folder.
        '''
        prefix = self.splitOsPath(str(self.inputdir))[-3]
        self.parent.prefix.setText(prefix)
        self.parent.jobname.setText(prefix)