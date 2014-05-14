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
        self.parent = parent
        
        
    def initInputDirectory(self):
        '''
        method that is called when a new inputdirectory is set
        '''
        self.inputdir = self.parent.inputdirectory.text()
        
        ## Clear old sino dirs
        self.parent.sinogramdirectory.setText('')
        self.sinodir = ''
        
        if not self.inputdir:
            return
        
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
        if not os.path.exists(self.cprdir):
            self.parent.cprdirectory.setText(self.cprdir)
            return
        else:
            # TODO: maybe use different error handling >> create new dir or warn
            # that the older one will be deleted
            self.parent.displayErrorMessage('Existing cpr-directory','Rename the destination')
                
        
    def checkFltpFolder(self):
        '''
        check whether fltp folder exists etc.
        TODO: all 3 methods: checkFltpFolder,checkCprFolder,checkSinFolder > too similar!
        '''
        tmp_dir = os.path.split(str(self.inputdir))
        self.fltpdir = os.path.join(tmp_dir[0],'fltp')
        if not os.path.exists(self.fltpdir):
            self.parent.fltpdirectory.setText(self.fltpdir)
            return
        else:
            # TODO: maybe use different error handling >> create new dir or warn
            # that the older one will be deleted
            self.parent.displayErrorMessage('Existing fltp-directory','Rename the destination')
                
        
    def checkRecoFolder(self):
        '''
        check whether reco folder exists etc.
        '''
        tmp_dir = os.path.split(str(self.inputdir))
        self.recodir = os.path.join(tmp_dir[0],'rec_8bit')
        if not os.path.exists(self.recodir):
            self.parent.recodirectory.setText(self.recodir)
            return
        else:
            # TODO: maybe use different error handling >> create new dir or warn
            # that the older one will be deleted
            self.parent.displayErrorMessage('Existing fltp-directory','Rename the destination')
        
        
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
        
        
    def loadAndParseLogFile(self):
        '''
        load log-file and set GUI fields from the log-file automatically
        '''
    
    def checkNumberOfProjs(self):
        '''
        for consecutive scans check whether all raw data is present (according to log-file).
        otherwise throw an error or
        '''
    
    
    def determineInputType(self):
        '''
        method for checking and setting input type
        TODO: this is a very preliminary and unefficient method
        (just for concept)
        '''
        for imgfile in listdir(self.inputdir):
            if imgfile.lower().endswith(".tif"):
                self.parent.inputtype.setCurrentIndex(2)
                self.filetype = 'tif'
                break
            elif imgfile.lower().endswith(".dmp"):
                self.parent.inputtype.setCurrentIndex(0)
                self.filetype = 'dmp'
                break
            elif imgfile.lower().endswith(".HD5"):
                self.parent.inputtype.setCurrentIndex(1)
                self.filetype = 'hd5'
                break
            else:
                self.parent.displayErrorMessage('No images found', 'There are no tif, dmp, nor hd5 files in the input folder!')
                return False
        return True
            
    def determinePrefix(self):
        '''
        method for determining and setting prefix
        TODO: again very preliminary >> more elegant would be to read from log file
        (for this we need to implement a log-file parser)
        '''
        two_files_list = []
        for filename in listdir(self.inputdir):
            if filename.lower().endswith("."+self.filetype):
                two_files_list.append(filename)
                if len(two_files_list) >= 2:
                    break
                else:
                    continue
        com_str = self.common_substring_finder(two_files_list[0],two_files_list[1])
        self.parent.prefix.setText(com_str+"#")
        ## let's color it green for now since we know this method is not correct
        self.parent.prefix.setStyleSheet("QLineEdit { border : 2px solid green;}")
        
        
    def common_substring_finder(self,str_a, str_b):
        '''
        find longest common substring from the beginning
        TODO: just for testing purposes
        '''
        def _iter():
            for a, b in zip(str_a, str_b):
                if a == b:
                    yield a
                else:
                    return
        return ''.join(_iter())


if __name__ == "__main__":
    # TESTING ground
    print os.path.exists('/Users/goranlovric/Desktop/asdf')
    print os.path.exists('/Users/goranlovric/Desktop/')
    print os.path.split('/Users/goranlovric/Desktop')