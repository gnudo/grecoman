class ParameterWrap(object):
    '''
    The "ParameterWrap" class serves the purpose of registering all
    CLA-s (command line arguments) that are used in the GUI (either for
    loading/saving settings or color-highlighting) and that are part
    of the reconstruction pipeline. Each CLA (parameter) object is an
    instance of the "Parameter" class, however we never call these
    objects directly. Instead, they are all stored in the class
    attribute "CLA_dict" and called from therein. By doing so,
    we are able to count all "Parameter" instances and iterate
    through all CLA-s. The other class variable "parent" stores the
    main application object.
    '''
    CLA_dict = {}
    parent = []
    
    @classmethod
    def registerAllParameters(cls,parent):
        '''
        When initializing the main application we need to call this
        method once (and only once). It is the only place to adapt
        (new) command line arguments (CLA-s) for the pipeline that are
        used in the GUI.
        '''
        cls.parent = parent
        
        cls.addParameter('inputdirectory','',[],True)
        cls.addParameter('prefix','-p',[],True)
        cls.addParameter('raws','',[],True)
        cls.addParameter('darks','',[],True)
        cls.addParameter('flats','',[],True)
        cls.addParameter('interflats','',[],True)
        cls.addParameter('flatfreq','',[],True)
        cls.addParameter('preflatsonly','-u',[],False)
        cls.addParameter('roion','-r',['roi_left','roi_right','roi_upper','roi_lower'],False)
        cls.addParameter('roi_left','',[],False)
        cls.addParameter('roi_right','',[],False)
        cls.addParameter('roi_upper','',[],False)
        cls.addParameter('roi_lower','',[],False)
        cls.addParameter('binsize','-b',[],False)
        cls.addParameter('scaleimagefactor','-s',[],False)
        cls.addParameter('steplines','-j',[],False)
        cls.addParameter('sinogramdirectory','-o',[],True)
        cls.addParameter('paganinon','-Y',['pag_energy','pag_pxsize','pag_delta','pag_beta','pag_distance','fltpdirectory'],False)
        cls.addParameter('pag_energy','',[],False)
        cls.addParameter('pag_delta','',[],False)
        cls.addParameter('pag_beta','',[],False)
        cls.addParameter('pag_pxsize','',[],False)
        cls.addParameter('pag_distance','',[],False)
        cls.addParameter('runringremoval','',['waveletdecompositionlevel', 'sigmaingaussfilter'],False)
        cls.addParameter('waveletdecompositionlevel','-V',[],False)
        cls.addParameter('sigmaingaussfilter','-E',[],False)
        cls.addParameter('cutofffrequency','-U',[],False)
        cls.addParameter('edgepadding','-Z',[],False)
        cls.addParameter('centerofrotation','-c',[],False)
        cls.addParameter('shiftcorrection','-q',[],False)
        cls.addParameter('rotationangle','-a',[],False)
        cls.addParameter('zingeron','-z',['zinger_thresh','zinger_width'],False)
        cls.addParameter('zinger_thresh','-H',[],False)
        cls.addParameter('zinger_width','-w',[],False)
        cls.addParameter('cpron','',['cprdirectory'],False)
        cls.addParameter('cprdirectory','',[],False)
        cls.addParameter('fltpdirectory','',[],False)
        cls.addParameter('sinon','',['sinogramdirectory'],False)
        cls.addParameter('sinogramdirectory','',[],False)
        cls.addParameter('reconstructon','',['recodirectory'],False)
        cls.addParameter('recodirectory','',[],False)
        cls.addParameter('withlog','',[],False)
        cls.addParameter('tifmin','-n',[],False)
        cls.addParameter('tifmax','-x',[],False)
        cls.addParameter('jobname','',[],False) 
        
        # we also register Comboboxes in order to use them in fileIO etc.
        cls.addParameter('inputtype','-I',[],False)
        cls.addParameter('wavelettype','-y',[],False)
        cls.addParameter('waveletpaddingmode','-M',[],False)
        cls.addParameter('filter','-F',[],False)
        cls.addParameter('outputtype','-t',[],False)
        cls.addParameter('geometry','-G',[],False)
        cls.addParameter('stitchingtype','-S',[],False)
        
        # we add radio box as well in order to require certain input directories
        cls.addParameter('sin_fromtif','',['inputdirectory'],False)
        cls.addParameter('sin_fromcpr','',['cprdirectory'],False)
        cls.addParameter('sin_fromfltp','',['fltpdirectory'],False)
        cls.addParameter('fltp_fromcpr','',['cprdirectory'],False)
        cls.addParameter('fltp_fromtif','',['inputdirectory'],False)
        cls.addParameter('rec_fromtif','',['inputdirectory'],False)
        cls.addParameter('rec_fromsino','',['sinogramdirectory'],False)
    
    
    @classmethod
    def addParameter(cls,*args):
        '''
        This method registers a new CLA by creating a "Parameter"
        object and storing it to the class attribute "CLA_dict" (python
        dictionary) under its name.
        '''
        par = Parameter( *args)
        cls.CLA_dict[par.name] = par

     
class Parameter(object):
    '''
    The "Parameter" class represents a standard command line argument
    (CLA) from the GUI and/or pipeline with its respective properties.
    Every instance of the "Parameter" class is saved in the class
    attribute "CLA_dict" of the "ParameterWrap" class.
    The main application object is hard-coded as "ParameterWrap.parent".
    '''
    def __init__(self,name,flag,child_list,ismandatory):
        self.name = name  # name of the parameter (CLA)
        self.ismandatory = ismandatory  # flag for defining the parameter as mandatory
        self.flag = flag  # flag for the command line argument (CLA)
        self.child_list = child_list  # list of parameters that depend from this one

        
    def performCheck(self):
        '''
        This method performs a check whether the respective field was
        set correctly in the GUI. Depending on the GUI-type the checks
        are performed in different ways.
        '''
        gui_field = getattr(ParameterWrap.parent,self.name)
        
        if type(gui_field).__name__ == 'QCheckBox':
            if gui_field.isChecked():
                return True
        elif type(gui_field).__name__ == 'QLineEdit':
            if not str(gui_field.text()) == '':
                return True
        elif type(gui_field).__name__ == 'QComboBox':
            if not str(gui_field.currentText()) == 'none':
                return True
        elif type(gui_field).__name__ == 'QRadioButton':
            if gui_field.isChecked():
                return True
        return False
    
    
    def resetField(self):
        '''
        This method resets the respective GUI-field dependent on its
        type.
        '''
        gui_field = getattr(ParameterWrap.parent,self.name)
        
        if type(gui_field).__name__ == 'QCheckBox':
            gui_field.setChecked(False)
            return
        elif type(gui_field).__name__ == 'QLineEdit':
            gui_field.setText('')
            return
        elif type(gui_field).__name__ == 'QComboBox':
            gui_field.setCurrentIndex(0)
            return
        elif type(gui_field).__name__ == 'QRadioButton':
            gui_field.setAutoExclusive(False)
            gui_field.setChecked(False)
            gui_field.setAutoExclusive(True)
            return        