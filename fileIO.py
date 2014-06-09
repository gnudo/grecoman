import ConfigParser


class FileIO(object):
    '''
    class for handling loading and saving of config-files
    '''
    def __init__(self, cfgfile):
        '''
        Constructor
        '''
        self.cfgfile = str(cfgfile)
        self.heading = 'GRecoMan Config'
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform=str
       
        
    def writeFile(self,parent,ParameterWrap):
        '''
        read all "registered" parameters from main GUI and write to config file
        '''
        self.config.add_section(self.heading)
        
        for key,param in ParameterWrap.par_dict.iteritems():
            name_handle = getattr(parent,param.name)
            
            if type(name_handle).__name__ == 'QLineEdit':
                self.config.set(self.heading, key, name_handle.text())
            if type(name_handle).__name__ == 'QCheckBox':
                if name_handle.isChecked():
                    self.config.set(self.heading, key, 'true')
                else:
                    self.config.set(self.heading, key, 'false')
            if type(name_handle).__name__ == 'QComboBox':
                self.config.set(self.heading, key, name_handle.currentIndex())
        
        with open(self.cfgfile, 'wb') as configfile:
            self.config.write(configfile)
        
        
    def loadFile(self,parent,ParameterWrap):
        '''
        load config file and write "registered" parameters to GUI fields/attributes
        '''
        self.config.read(self.cfgfile)
        
        for param in self.config.options(self.heading):
            name_handle = getattr(parent,param)
            
            if type(name_handle).__name__ == 'QLineEdit':
                txt = self.config.get(self.heading, param)
                name_handle.setText(txt)
            if type(name_handle).__name__ == 'QCheckBox' or type(name_handle).__name__ == 'QRadioButton':
                checkstatus = self.config.getboolean(self.heading, param)
                name_handle.setChecked(checkstatus)
            if type(name_handle).__name__ == 'QComboBox':
                val = self.config.get(self.heading, param)
                name_handle.setCurrentIndex(int(val))
        

if __name__ == "__main__":
    # TESTING ground
    file_obj = FileIO('/Users/goranlovric/Desktop/test.txt')
    par_dict = {"test":"1", "test":"2", "test3":"3"}
    file_obj.writeFile([], par_dict)