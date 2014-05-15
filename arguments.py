class ParameterWrap(object):
    '''
    class where we have to register every parameter that we want to use later for building the
    command line string that is sent to the cluster. Instead of creating single instances of the
    class, we only call the "ParameterWrap" class and all instances are stored in its class
    attribute <par_dict>. the reason why it's chosen like this is in order to count all instances
    of the Parameter class later on.
    '''
    par_dict = {}
    def __call__(self,*args):
        par = Parameter( *args)
        self.par_dict[par.name] = par
        return par
     
class Parameter(object):
    '''
    class for every parameter (argument) that is appended to the
    command line when running the reconstruction
    '''
    def __init__(self,parent,name,flag,child_list,ismandatory):
        self.parent = parent  # parent object
        self.name = name  # name of the parameter
        self.ismandatory = ismandatory  # is the parameter mandatory
        self.flag = flag  # flag for command line
        self.child_list = child_list  # list of parameters that depend on this flag

        
    def performCheck(self):
        '''
        method to perform a check whether the a field was set correctly in the GUI
        '''
        name_handle = getattr(self.parent,self.name)
        
        if type(name_handle).__name__ == 'QCheckBox':
            if name_handle.isChecked():
                return True
        elif type(name_handle).__name__ == 'QLineEdit':
            if not str(name_handle.text()) == '':
                return True
        elif type(name_handle).__name__ == 'QComboBox':
            if not str(name_handle.currentText()) == 'none':
                return True
        elif type(name_handle).__name__ == 'QRadioButton':
            if name_handle.isChecked():
                return True
        return False
    
    
    def resetField(self):
        '''
        reset respective parameter dependent on the type
        '''
        name_handle = getattr(self.parent,self.name)
        
        if type(name_handle).__name__ == 'QCheckBox':
            name_handle.setChecked(False)
            return
        elif type(name_handle).__name__ == 'QLineEdit':
            name_handle.setText('')
            return
        elif type(name_handle).__name__ == 'QComboBox':
            name_handle.setCurrentIndex(0)
            return
        elif type(name_handle).__name__ == 'QRadioButton':
            name_handle.setAutoExclusive(False)
            name_handle.setChecked(False)
            name_handle.setAutoExclusive(True)
            return
        

if __name__ == "__main__":
    # TESTING ground
    aas = ParameterWrap()(1,'a',1)
    bas = ParameterWrap()(1,'b',1)
    print ParameterWrap.parameterlist
    print aas.name
    print bas.name
        