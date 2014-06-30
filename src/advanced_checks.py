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
        
        
    def initInputDirectory(self):
        '''
        method that is called when a new inputdirectory is set
        '''
        self.inputdir = os.path.join(str(self.parent.inputdirectory.text()),'')
        
        ## Clear old sino dirs
        self.parent.sinogramdirectory.setText('')
        self.sinodir = ''
        
        if not self.inputdir:
            return
        
        self.parent.lastdir = self.getParentDir(str(self.inputdir))
        
        if self.determineInputType():
            self.determinePrefix()
        
        ## TODO: check SIN folder (and set if necessary to standard)
        self.checkSinFolder()
        
        ## TODO: check CPR folder (and set if necessary to standard)
        self.checkCprFolder()  

        ## TODO: check FLTP folder (and set if necessary to standard)
        self.checkFltpFolder()
        
        ## TODO: check rec8bit folder (and set if necessary to standard)
        self.checkRecoFolder()     
        
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
        self.sinodir = self.parent.sinogramdirectory.text()
        
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
            
            
    def checkCprFolder(self):
        '''
        check whether cpr folder exists etc.
        '''
        tmp_dir = os.path.split(str(self.inputdir))
        self.cprdir = os.path.join(tmp_dir[0],'cpr')
        if os.path.exists(self.cprdir):
            self.parent.displayErrorMessage('Existing cpr-directory','Rename the destination')
            
        self.parent.cprdirectory.setText(self.cprdir)
                
        
    def checkFltpFolder(self):
        '''
        check whether fltp folder exists etc.
        TODO: all 3 methods: checkFltpFolder,checkCprFolder,checkSinFolder > too similar!
        '''
        tmp_dir = os.path.split(str(self.inputdir))
        self.fltpdir = os.path.join(tmp_dir[0],'fltp')
        if os.path.exists(self.fltpdir):
            self.parent.displayErrorMessage('Existing fltp-directory','Rename the destination')
            
        self.parent.fltpdirectory.setText(self.fltpdir)
                
        
    def checkRecoFolder(self):
        '''
        check whether reco folder exists etc.
        '''
        tmp_dir = os.path.split(str(self.inputdir))
        self.recodir = os.path.join(tmp_dir[0],'rec_8bit')
        if os.path.exists(self.recodir):
            self.parent.displayErrorMessage('Existing fltp-directory','Rename the destination')
            
        self.parent.recodirectory.setText(self.recodir)
        
        
    def checkSinFolder(self):
        '''
        check whether sinograms exist and if yes populate the respective combobox
        '''
        if not self.sinodir:
            tmp_dir = os.path.split(str(self.inputdir))
            sinfolder = os.path.join(tmp_dir[0],'sin')
            self.parent.sinogramdirectory.setText(sinfolder)
            
        self.initSinDirectory()
            
            
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
                
    
    def checkNumberOfProjs(self):
        '''
        for consecutive scans check whether all raw data is present (according to log-file).
        otherwise throw an error or
        '''
    
    
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


if __name__ == "__main__":
    # TESTING ground
    print os.path.exists('/Users/goranlovric/Desktop/asdf')
    print os.path.exists('/Users/goranlovric/Desktop/')
    print os.path.split('/Users/goranlovric/Desktop')