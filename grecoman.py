from gui import Ui_reco_mainwin
from dmp_reader import DMPreader
from arguments import ParameterWrap
from connector import Connector
from advanced_checks import AdvancedChecks
from fileIO import FileIO
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import os.path


class MainWindow(QMainWindow, Ui_reco_mainwin):
    '''
    main class containing methods for ideally all window actions in the main app. other specific
    methods should be contained in other classes
    '''
 
    def __init__(self):        
        QMainWindow.__init__(self)
        self.setupUi(self)  # set up User Interface (widgets, layout...)
        
        QObject.connect(self.setinputdirectory,
            SIGNAL("clicked()"),self.getInputDirectory)  # data input directory
        QObject.connect(self.inputdirectory,
            SIGNAL("returnPressed()"),self.initInputDirectory)  # data input through keyboard
        QObject.connect(self.setsinogramdirectory,
            SIGNAL("clicked()"),self.getSinogramDirectory)  # sinogram output
        QObject.connect(self.setuprecoutputdir,
            SIGNAL("clicked()"),self.setRecOutputDir)  # sinogram output
        QObject.connect(self.submit,
            SIGNAL("released()"),self.submitToCluster)  # BUTTON submit button
        QObject.connect(self.clearfields,
            SIGNAL("released()"),self.clearAllFields)  # BUTTON clear all fields method
        QObject.connect(self.testbutton,
            SIGNAL("released()"),self.test_button)  # BUTTON test button
        QObject.connect(self.singleslice,
            SIGNAL("released()"),self.calcSingleSlice)  # BUTTON Single Slice calculation
        QObject.connect(self.menuloadsettings,
            SIGNAL("triggered()"),self.loadConfigFile)  # MENU load settings
        QObject.connect(self.menusavesettings,
            SIGNAL("triggered()"),self.saveConfigFile)  # MENU save settings
 
        self.registerAllParameters()  # we register all command line arguments
        self.job = Connector(self)  # connector object for submitting the command
        self.homedir = os.path.expanduser('~')
        
    def registerAllParameters(self):
        '''
        here we register all command line parameters (arguments) by creating <Parameter> objects
        and setting appropriate properties. Objects are created each time ParameterWrap() is called
        and they are stored in the class property "ParameterWrap.par_dict" (python dictionary). see
        "arguments.py" for more info
        '''
        ParameterWrap()(self,'inputdirectory','',[],True)
        ParameterWrap()(self,'prefix','-p',[],True)
        ParameterWrap()(self,'raws','',[],True)
        ParameterWrap()(self,'darks','',[],True)
        ParameterWrap()(self,'flats','',[],True)
        ParameterWrap()(self,'interflats','',[],True)
        ParameterWrap()(self,'flatfreq','',[],True)
        ParameterWrap()(self,'preflatsonly','-u',[],False)
        ParameterWrap()(self,'firstindex','-i',[],False)
        ParameterWrap()(self,'roion','-r',['roi_left','roi_right','roi_upper','roi_lower'],False)
        ParameterWrap()(self,'roi_left','',[],False)
        ParameterWrap()(self,'roi_right','',[],False)
        ParameterWrap()(self,'roi_upper','',[],False)
        ParameterWrap()(self,'roi_lower','',[],False)
        ParameterWrap()(self,'binsize','-b',[],False)
        ParameterWrap()(self,'scaleimagefactor','-s',[],False)
        ParameterWrap()(self,'correctionOnly','-C',[],False)
        ParameterWrap()(self,'createMissing','-d',[],False)
        ParameterWrap()(self,'steplines','-j',[],False)
        ParameterWrap()(self,'sinogramdirectory','-o',[],True)
        ParameterWrap()(self,'paganinon','-Y',['pag_energy','pag_delta','pag_beta','pag_pxsize','pag_distance'],False)
        ParameterWrap()(self,'pag_energy','',[],False)
        ParameterWrap()(self,'pag_delta','',[],False)
        ParameterWrap()(self,'pag_beta','',[],False)
        ParameterWrap()(self,'pag_pxsize','',[],False)
        ParameterWrap()(self,'pag_distance','',[],False)
        ParameterWrap()(self,'runringremoval','',['waveletdecompositionlevel', 'sigmaingaussfilter'],False)
        ParameterWrap()(self,'waveletdecompositionlevel','-V',[],False)
        ParameterWrap()(self,'sigmaingaussfilter','-E',[],False)
        ParameterWrap()(self,'reconstructon','-R',['reconstruct'],False)
        ParameterWrap()(self,'reconstruct','',[],False)
        ParameterWrap()(self,'cutofffrequency','-U',[],False)
        ParameterWrap()(self,'edgepadding','-Z',[],False)
        ParameterWrap()(self,'centerofrotation','-c',[],False)
        ParameterWrap()(self,'shiftcorrection','-q',[],False)
        ParameterWrap()(self,'rotationangle','-a',[],False)
        ParameterWrap()(self,'recoutputdir','-O',[],False)
        ParameterWrap()(self,'zingeron','-z',['zinger_thresh','zinger_width'],False)
        ParameterWrap()(self,'zinger_thresh','-H',[],False)
        ParameterWrap()(self,'zinger_width','-w',[],False)
        
        # we also register Comboboxes in order to use them in fileIO etc.
        ParameterWrap()(self,'inputtype','-I',[],False)
        ParameterWrap()(self,'correctiontype','-g',[],False)
        ParameterWrap()(self,'keepsinograms','-k',[],False)
        ParameterWrap()(self,'wavelettype','-y',[],False)
        ParameterWrap()(self,'waveletpaddingmode','-M',[],False)
        ParameterWrap()(self,'filter','-F',[],False)
        ParameterWrap()(self,'outputtype','-t',[],False)
        ParameterWrap()(self,'geometry','-G',[],False)
        
 
    def submitToCluster(self):
        '''
        method that launches all the checks and if successful submits the
        command to cons-2 for starting the job
        '''
        if not self.checkAllParamters():
            return
        
        # (1) Create command line string
        self.createCommand() 
        
        # (2) run SSH-connector and check all account credentials
        if not self.job.performInitalCheck():
            return
        
        # (3) run SSh-connector to launch the job
        print self.cmd_string
        self.job.submitJobViaGateway(self.cmd_string+'\n','x02da-gw','x02da-cons-2','random name')  # TODO: set job-name also in GUI
            
            
    def calcSingleSlice(self):
        '''
        method for renconstructing a single slice for a given sinogram.
        '''
        if not hasattr(self, 'input_dir'):
            self.displayErrorMessage('Missing input directory', 'No input directory was set')
            return
        
        ## (1) check whether we have defined the location from where we run the reconstruction
        if not self.checkComputingLocation():
            return
        
        ## (2) before calculating on x02da-cons-2, we need to rewrite the path of the sino dir
        if self.afsaccount.isChecked():
            single_sino = self.checks.afsPath2Cons2(self.sinogramdirectory.text())
        elif self.cons2.isChecked():
            single_sino = self.sinogramdirectory.text()
        
        ## (3) create the command line string for single slice reconstruction
        self.cmd_string = 'python singleSliceFunc.py '
        
        combos_single = ['filter']  # removed: 'outputtype' (let's always have DMP!)
        for combo in combos_single:
            if ParameterWrap.par_dict[combo].performCheck():
                self.cmd_string += ParameterWrap.par_dict[combo].flag+' '+self.getComboBoxContent(combo)+' ' 
        
        if self.zingeron.isChecked():
            self.setZingerParameters()
        
        optional_single = ['cutofffrequency','edgepadding','centerofrotation','rotationangle']
        for param in optional_single:
            if not getattr(self,param).text() == '':
                self.cmd_string += ParameterWrap.par_dict[param].flag+' '+getattr(self,param).text()+' '
        
        if self.runringremoval.isChecked():  # the wavelet parameters are composed separately
            self.setWavletParameters()
        
        self.cmd_string += '-Di '+single_sino+' -i '+self.sinograms.currentText()
        
        ## (4) now we check credentials
        if not self.job.performInitalCheck():
            self.displayErrorMessage('Unsuccessful authentification', 'Could not login with AFS and/OR eaccount credentials')
            return
        
        ## (5) after all checks completed, Filippos wrapper is called to perform
        print self.cmd_string
        self.job.submitJobViaGateway(self.cmd_string+'\n','x02da-gw','x02da-cons-2','random name')
        
        ## (6) we display the image
        new_filename = self.sinograms.currentText()[:-7]+'rec.'
        img = self.checks.cons2Path2afs(single_sino[:-3]+'viewrec/'+new_filename+self.sinograms.currentText()[-3:])
        self.displayImageBig(img)
 

    def createCommand(self):
        '''
        main method for creating the command line string. for consistency reasons the flags are
        defined in the registerAllParameters() method only (and only there!)
        TODO: after having understood how the "prj2sinSGE" script really works this method has to
        be completely rewritten
        '''        
        self.cmd_string = "prj2sinSGE "
        pureflags = ['correctionOnly', 'createMissing', 'preflatsonly', 'shiftcorrection']
        
        ## (1) Compose first pure flags 
        for pureflag in pureflags:
            if getattr(self,pureflag).isChecked():
                self.cmd_string += ParameterWrap.par_dict[pureflag].flag+' '
        
        ## (2) Non-mandatory parameters with children (wavelet we do separately)
        non_madatory_with_child = ['roion', 'paganinon', 'reconstructon']
        for param in non_madatory_with_child:
            if getattr(self,param).isChecked():
                self.cmd_string += ParameterWrap.par_dict[param].flag+' '
                for child in ParameterWrap.par_dict[param].child_list:
                    self.cmd_string += getattr(self,child).text()+','
                self.cmd_string = self.cmd_string[:-1]+' '
            
        ## (3) Optional parameters that should only be added if they are non-empty
        optional = ['firstindex', 'binsize', 'scaleimagefactor', 'steplines', 'cutofffrequency',
                    'edgepadding', 'centerofrotation','rotationangle']
        for param in optional:
            if not getattr(self,param).text() == '':
                self.cmd_string += ParameterWrap.par_dict[param].flag+' '+getattr(self,param).text()+' '
        
        if self.runringremoval.isChecked():  # the wavelet parameters are composed separately
            self.setWavletParameters()
            
        if self.zingeron.isChecked():  # the zinger parameters are composed separately as well
            self.setZingerParameters()
                
        ## (4) Comboboxes with respective dictionaries (except wavelet comboboxes)
        comboboxes = ['correctiontype', 'keepsinograms', 'filter', 'outputtype', 'geometry','inputtype']
        
        for combo in comboboxes:
            if ParameterWrap.par_dict[combo].performCheck():
                self.cmd_string += ParameterWrap.par_dict[combo].flag+' '+self.getComboBoxContent(combo)+' '        
        
        ## (5) Compose all mandatory
        self.cmd_string += '-f '+self.raws.text()
        self.cmd_string += ','+self.darks.text()
        self.cmd_string += ','+self.flats.text()
        self.cmd_string += ','+self.interflats.text()
        self.cmd_string += ','+self.flatfreq.text()+' '
        
        self.cmd_string += ParameterWrap.par_dict['prefix'].flag+' '+getattr(self,'prefix').text()+' '
        if self.afsaccount.isChecked():
            sinodir_mod = self.checks.afsPath2Cons2(str(getattr(self,'sinogramdirectory').text()))
            inputdir_mod= self.checks.afsPath2Cons2(str(self.inputdirectory.text()))
            self.cmd_string += ParameterWrap.par_dict['sinogramdirectory'].flag+' '+sinodir_mod+' '
            ## (6) Append input directory
            self.cmd_string += inputdir_mod
        elif self.cons2.isChecked():
            self.cmd_string += ParameterWrap.par_dict['sinogramdirectory'].flag+' '+getattr(self,'sinogramdirectory').text()+' '
            ## (6) Append input directory
            self.cmd_string += self.inputdirectory.text()
        
        
    def checkAllParamters(self):
        '''
        method for checking whether all parameters are set in the GUI. only if it returns
        <True>, the command can be created to be submitted to the cluster
        '''
        color_list = []
        self.resetAllStyleSheets()
        
        if not self.checkComputingLocation():
            return
    
        # (1) all parameters that are mandatory (they cannot have any child parameters)
        for key,param in ParameterWrap.par_dict.iteritems():
            if param.ismandatory and not param.performCheck():
                color_list.append(param.name)
        # (2) all parameters that are NOT mandatory, but are set anyways --> then we need to
        # perform a check of their children because in that case those must be set as well
        for key,param in ParameterWrap.par_dict.iteritems():
                if not param.ismandatory and param.performCheck():
                    for child_param in param.child_list:
                        if not ParameterWrap.par_dict[child_param].performCheck():
                            color_list.append(child_param)
        # (3) color the boxes
        for param in color_list:
            missing_param = getattr(self,param)
            missing_param.setStyleSheet("QLineEdit { border : 2px solid red;}")
        
        if not color_list:
            return True
        
        
    def checkComputingLocation(self):
        '''
        make sure the radiobox from the the computing takes place has been set
        '''
        if not self.afsaccount.isChecked() and not self.cons2.isChecked():
            self.displayErrorMessage('Missing radio box', 'From where are you running the application?')
            return False
        return True
            
    
    def resetAllStyleSheets(self):
        '''
        delete all custom stylesheet settings for all class properties
        '''
        for key,param in ParameterWrap.par_dict.iteritems():
            handle = getattr(self,param.name)
            handle.setStyleSheet("")
            
            
    def clearAllFields(self):
        '''
        method for clearing all fields in the GUI
        '''
        for key,param in ParameterWrap.par_dict.iteritems():
            param.resetField()
        self.sinograms.clear()
        self.resetAllStyleSheets()
            
            
    def saveConfigFile(self):
        '''
        method when pressing Menu item for loading config file
        '''
        savefile = QFileDialog.getSaveFileName(self,
                        'Select where the config file should be saved',self.homedir)
        if not savefile:
            return
        file_obj = FileIO(savefile)
        file_obj.writeFile(self, ParameterWrap)
        
        
    def loadConfigFile(self):
        '''
        method for loading config-file (from Menu item)
        '''
        loadfile = QFileDialog.getOpenFileName(self,
                        'Select where the config file is located',self.homedir)
        if not loadfile:
            return
        file_obj = FileIO(loadfile)
        file_obj.loadFile(self,ParameterWrap)
        
        self.input_dir = self.inputdirectory.text()
        # TODO: find a better way >> in fact we should call initInputDirectory, but then the prefix
        #       gets reset. if we call like this, then we don't look for sinograms...
        self.checks = AdvancedChecks(self,self.input_dir)  # we need to create the object
        
        
    def getComboBoxContent(self,box):
        '''
        method for getting content from ComboBox and containing custom dictionaries
        '''
        if box is 'correctiontype':
            types_dict = {"0":"7", "1":"1", "2":"2", "3":"3"}
        elif box is 'keepsinograms':
            types_dict = {"0":"0", "1":"1", "2":"2"}
        elif box is 'filter':
            types_dict = {"0":"schepp", "1":"hanning", "2":"hamming", "3":"ramlak", "4":"parzen",
                          "5":"lanczos", "6":"dpc", "7":"none"}     
        elif box is 'outputtype':
            types_dict = {"0":"8", "1":"0", "2":"1", "3":"16"}
        elif box is 'geometry':
            types_dict = {"0":"1", "1":"0", "2":"2"}
        elif box is 'waveletpaddingmode':
            types_dict = {"0":"zpd", "1":"cpd", "2":"sym","3":"ppd", "4":"sp1"}
        elif box is 'inputtype':
            types_dict = {"0":"0", "1":"2", "2":"1", "3":"3"}
         
        corr_str = str(getattr(self,box).currentIndex())
        return types_dict[corr_str]
        
    
    def getInputDirectory(self):
        '''
        dialog for setting the input directory
        '''
        self.input_dir = QFileDialog.getExistingDirectory(self,
                            'Select direcory for the projection data',self.homedir)
        if not self.input_dir:
            return
        self.inputdirectory.setText(self.input_dir)
        self.initInputDirectory()
        
        
    def initInputDirectory(self):
        '''
        method that is run after the input directory is set. it's separated from getInputDirectory()
        so that we can initialize the input directory by "pasting" the path to the field or by
        loading a config file 
        '''
        
        # TODO: since setting the input directory is the most crucial step,
        # here we can perform all further checks
        # 1.) e.g. search and parse a log file and populate GUI fields from the log-file
        # 2.) check number of projections and alert if it is not correct
        # 3.) check whether fltp folder exists and set GUI accordingly
        # 4.) ...
        
        self.input_dir = self.inputdirectory.text()
        if not self.input_dir:
            return
 
        self.checks = AdvancedChecks(self,self.input_dir)  # object for performing all checks 
        
        ## check for sinos
        self.checks.checkSinFolder()
        
        ## PRELIMINARY: find input type
        if not self.checks.determineInputType():
            return
        
        ## PRELIMINARY: find prefix and set
        self.checks.determinePrefix()
    
    
    def getSinogramDirectory(self):
        '''
        dialog for setting the sinogram output directory 
        '''
        self.sino_dir = QFileDialog.getExistingDirectory(self,
                            'Select direcory for sinograms',self.homedir)
        self.sinogramdirectory.setText(self.sino_dir)
        
        
    def setRecOutputDir(self):
        '''
        sets the output directory if this option is checked in the GUI
        '''
        recoutput = QFileDialog.getExistingDirectory(self,
                        'Select direcory for the projection data',self.homedir)
        self.recoutputdir.setText(recoutput)
            
        
    def setWavletParameters(self):
        '''
        method for adding the wavelet correction to the command line string
        '''
        combos = ['wavelettype','waveletpaddingmode']
        textedit = ['waveletdecompositionlevel','sigmaingaussfilter']
        
        self.cmd_string += ParameterWrap.par_dict[combos[0]].flag+' '+str(getattr(self,combos[0]).currentText())+' '
        self.cmd_string += ParameterWrap.par_dict[textedit[0]].flag+' '+getattr(self,textedit[0]).text()+' '
        self.cmd_string += ParameterWrap.par_dict[textedit[1]].flag+' '+getattr(self,textedit[1]).text()+' '
        self.cmd_string += ParameterWrap.par_dict[combos[1]].flag+' '+self.getComboBoxContent(combos[1])+' '
        
        
    def setZingerParameters(self):
        '''
        method for adding zinger removal parameters
        '''
        self.cmd_string += '-z 1 '
        self.cmd_string += ParameterWrap.par_dict['zinger_thresh'].flag+' '+str(getattr(self,'zinger_thresh').text())+' '
        self.cmd_string += ParameterWrap.par_dict['zinger_width'].flag+' '+str(getattr(self,'zinger_width').text())+' '
                
        
    def displayErrorMessage(self,head,msg):
        '''
        method to display random error messages with QMessageBox
        '''
        QMessageBox.warning(self, head, msg)
        
        
    def displayImageBig(self,img_file):
        '''
        method for displaying a single image in the big frame
        '''
        if img_file[-3:].lower() == 'tif':
            myPixmap = QPixmap(img_file)
        elif img_file[-3:].lower() == 'dmp':
            myPixmap = DMPreader(img_file)
            
        
        myScaledPixmap = myPixmap.scaled(self.ImgViewer.size(), Qt.KeepAspectRatio)
        self.ImgViewer.setPixmap(myScaledPixmap)
    
    
    def test_button(self):
        '''
        playground for testing of new code
        '''
        

if __name__ == "__main__":
    mainapp = QApplication(sys.argv,True)  # create Qt application
    win = MainWindow()  # create main window
    win.show()
 
    # Connect signals for mainapp
    mainapp.connect(mainapp, SIGNAL("lastWindowClosed()"), mainapp, SLOT("quit()"))
    mainapp.connect(win.exitapp, SIGNAL("triggered()"), mainapp, SLOT("quit()"))
 
    # Start up mainapp
    sys.exit(mainapp.exec_())