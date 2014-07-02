import ConfigParser


class FileIO(object):
    '''
    The "FileIO" class is used for loading/saving config files from
    GUI-fields (CLA-s) in order to quickly start reproducible
    pipeline operations. Every "FileIO" instance takes both the main
    application object and the OS path to the config file as arguments.
    In the current version no special characters (in the GUI-fields)
    are supported.
    '''
    def __init__(self, parent, cfgfile):
        self.parent = parent  # main app object
        self.cfgfile = str(cfgfile)
        self.heading = 'GRecoMan Config'
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform=str
       
        
    def writeFile(self,ParameterWrap):
        '''
        This method writes a full configuration file by iterating
        through all parameters (CLA-s) from the GUI that are saved in
        the class variable (dictionary) "ParameterWrap.CLA_dict" (see
        arguments.py) and calling "writeSingleParameter" method.
        '''
        self.config.add_section(self.heading)
        
        for key,param in ParameterWrap.CLA_dict.iteritems():
            self.writeSingleParameter(key,param)
        
        with open(self.cfgfile, 'wb') as configfile:
            self.config.write(configfile)
        
        
    def loadFile(self,ParameterWrap,overwrite):
        '''
        This method loads all parameters from a configuration file into
        the available GUI-fields. Here we iterate through config-file
        options rather than "ParameterWrap.CLA_dict". In doing so we
        make sure that if we add new GUI-fields in the future, old
        config files will still be compatible.
        '''
        self.config.read(self.cfgfile)
        
        for param in self.config.options(self.heading):
            self.loadSingleParamter(param,overwrite)
                
                
    def writeSingleParameter(self,key,param):
        '''Method for writing a single Parameter to a config file.'''
        name_handle = getattr(self.parent,param.name)
        
        if type(name_handle).__name__ == 'QLineEdit':
            self.config.set(self.heading, key, name_handle.text())
        if type(name_handle).__name__ == 'QCheckBox':
            if name_handle.isChecked():
                self.config.set(self.heading, key, 'true')
            else:
                self.config.set(self.heading, key, 'false')
        if type(name_handle).__name__ == 'QComboBox':
            self.config.set(self.heading, key, name_handle.currentIndex())
        
        
    def loadSingleParamter(self,param,overwrite):
        '''Method for loading a single parameter from a config file.'''
        try:
            name_handle = getattr(self.parent,param)
        except AttributeError:
            return
        
        if type(name_handle).__name__ == 'QLineEdit':
            txt = self.config.get(self.heading, param)
            if overwrite or txt:
                name_handle.setText(txt)
        if type(name_handle).__name__ == 'QCheckBox' or \
            type(name_handle).__name__ == 'QRadioButton':
            checkstatus = self.config.getboolean(self.heading, param)
            name_handle.setChecked(checkstatus)
        if type(name_handle).__name__ == 'QComboBox':
            val = self.config.get(self.heading, param)
            name_handle.setCurrentIndex(int(val))