from ui_main import Ui_reco_mainwin
from ui_dialogs import DebugCommand, Postfix
from io_img import Image
from arguments import ParameterWrap
from connector import Connector
from datasets import DatasetFolder
from prj2sin import Prj2sinWrap
from fileIO import ConfigFile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep,strftime # TODO: preliminary
import sys


class MainWindow(QMainWindow, Ui_reco_mainwin):
    '''
    Main class containing methods for ideally all window actions in
    the main application. All methods, which affect GUI-behavior
    should be included/changed here whereas other specific methods
    should be placed elsewhere.
    '''
 
    def __init__(self):
        '''
        Initializing method for main application: when launched, all
        necessary objects are created, GUI events and actions are set,
        tabulator ordering is aligned etc. 
        '''
        QMainWindow.__init__(self)
        self.setupUi(self)  # set up User Interface (widgets, layout...)

        ParameterWrap.registerAllParameters(self)  # we register all command line arguments
        self.job = Connector(self)  # connector object for submitting the command
        self.dirs = DatasetFolder(self)  # Object for performing all operations on dirs
        self.lastdir = self.dirs.homedir  # set the starting open directory to HOME
        self.lastdir_config = self.lastdir  # set the starting open directory for config-files
        self.changeSubmissionTarget('x02da')  # set the submission target standardly to x02da
        
        ## GUI settings
        self.setAcceptDrops(True)  # accept Drag'n drop files
        
        ## GUI fields connections
        QObject.connect(self.setinputdirectory,
            SIGNAL("clicked()"),lambda param='inputdirectory': self.getDirectory(param))  # data input directory
        QObject.connect(self.setsinogramdirectory,
            SIGNAL("clicked()"),lambda param='sindirectory': self.getDirectory(param))  # sinogram output
        QObject.connect(self.setcprdirectory,
            SIGNAL("clicked()"),lambda param='cprdirectory': self.getDirectory(param))  # cpr output
        QObject.connect(self.setfltpdirectory,
            SIGNAL("clicked()"),lambda param='fltpdirectory': self.getDirectory(param))  # fltp output
        QObject.connect(self.setrecodirectory,
            SIGNAL("clicked()"),lambda param='recodirectory': self.getDirectory(param))  # reconstructions output
        QObject.connect(self.inputdirectory,
            SIGNAL("returnPressed()"),self.dirs.initInputDirectory)  # data input through keyboard
        QObject.connect(self.sindirectory,
            SIGNAL("returnPressed()"),self.dirs.initSinDirectory)  # sinogram dir input through keyboard
        QObject.connect(self.addpostfix,
            SIGNAL("clicked()"),self.appendPostfix)  # open textfield for defining postfix
        QObject.connect(self.sinon,
            SIGNAL("clicked()"),lambda param='sinon': self.setUnsetActionCheckBox(param))  # sinogram checkbox ("toggled" not working)
        QObject.connect(self.paganinon,
            SIGNAL("clicked()"),lambda param='paganinon': self.setUnsetActionCheckBox(param))  # Paganin checkbox ("toggled" not working)
        QObject.connect(self.reconstructon,
            SIGNAL("clicked()"),lambda param='reconstructon': self.setUnsetActionCheckBox(param))  # Reco checkbox ("toggled" not working)
        QObject.connect(self.openinfiji,
            SIGNAL("clicked()"),self.setUnsetFijiOn)  # Fiji preview image checkbox ("toggled" not working)
        QObject.connect(self.sinograms,
            SIGNAL("currentIndexChanged(const QString&)"),self.moveSliderBySinochange)  # change output-dir name according to output type
        QObject.connect(self.outputtype,
            SIGNAL("currentIndexChanged(const QString&)"),self.changeOutputType)  # change output-dir name according to output type
        self.afsaccount.toggled.connect(self.setUnsetComputingLocation)  # Computing location radio box
        self.cons2.toggled.connect(self.setUnsetComputingLocation)  # Computing location radio box
        self.sinoslider.valueChanged.connect(self.setSinoWithSlider)  # Sinograms slider event
        self.sinoslider.setInvertedControls(1)  # invert the slider scrolling direction
        
        ## GUI buttons connections
        QObject.connect(self.submit,
            SIGNAL("released()"),self.submitToCluster)  # BUTTON submit button
        QObject.connect(self.clearfields,
            SIGNAL("released()"),ParameterWrap.clearAllFields)  # BUTTON clear all fields method
        QObject.connect(self.singleslice,
            SIGNAL("released()"),self.calcSingleSlice)  # BUTTON Single Slice calculation
        
        ## MENU connections
        QObject.connect(self.menuloadsettings,
            SIGNAL("triggered()"),self.loadConfigFile)  # MENU load settings
        QShortcut(QKeySequence("Ctrl+O"), self, self.loadConfigFile, context=Qt.WindowShortcut)  # comes from Qt.ShortcutContext
        QObject.connect(self.menusavesettings,
            SIGNAL("triggered()"),self.saveConfigFile)  # MENU save settings
        QShortcut(QKeySequence("Ctrl+S"), self, self.saveConfigFile, context=Qt.WindowShortcut)  # comes from Qt.ShortcutContext
        QObject.connect(self.menuLoadOnlyPaganin,
            SIGNAL("triggered()"),lambda param=ParameterWrap.CLA_dict['paganinon'].child_list[:-1]: \
            self.loadSpecificFromConfigFile(param))  # MENU load specific settings -> Paganin
        QObject.connect(self.menuLoadOnlyRingRemoval,
            SIGNAL("triggered()"),lambda param=['waveletdecompositionlevel','sigmaingaussfilter','wavelettype','waveletpaddingmode']: \
            self.loadSpecificFromConfigFile(param))  # MENU load specific settings -> Paganin
        QObject.connect(self.menuCreateCpr,
            SIGNAL("triggered()"),lambda param='createCpr': self.loadTemplate(param))  # MENU create CPR
        QObject.connect(self.menuCreateCprLog,
            SIGNAL("triggered()"),lambda param='createCprLog': self.loadTemplate(param))  # MENU create CPR with log correction
        QObject.connect(self.menuCreateFltp,
            SIGNAL("triggered()"),lambda param='createFltp': self.loadTemplate(param))  # MENU create Fltp
        QObject.connect(self.menuCreateFltpCpr,
            SIGNAL("triggered()"),lambda param='createFltpCpr': self.loadTemplate(param))  # MENU create Fltp+CPR
        QObject.connect(self.menuCreateSinosQuick,
            SIGNAL("triggered()"),lambda param='createSinosQuick': self.loadTemplate(param))  # MENU create Sinos quick
        QObject.connect(self.menuCreateSinosFromTif,
            SIGNAL("triggered()"),lambda param='createSinosFromTif': self.loadTemplate(param))  # MENU create Sinos from TIF
        QObject.connect(self.menuCreateSinosFromFltp,
            SIGNAL("triggered()"),lambda param='createSinosFromFltp': self.loadTemplate(param))  # MENU create Sinos from FLTP
        QObject.connect(self.menuCreateRecoStandard,
            SIGNAL("triggered()"),lambda param='createRecoStandard': self.loadTemplate(param))  # MENU create Recos from TIF
        QObject.connect(self.menuCreateRecoPaganin,
            SIGNAL("triggered()"),lambda param='createRecoPaganin': self.loadTemplate(param))  # MENU create Recos from FLTP
        QObject.connect(self.menuRingRemoval1,
            SIGNAL("triggered()"),lambda param='ringRemoval1': self.loadTemplate(param))  # MENU run ringremoval setting 1
        QObject.connect(self.menuRingRemoval2,
            SIGNAL("triggered()"),lambda param='ringRemoval2': self.loadTemplate(param))  # MENU run ringremoval setting 2
        QObject.connect(self.menuChangeMerlinMountPoint,
            SIGNAL("triggered()"),lambda param='merlin_mount_dir': self.getDirectory(param))  # MENU change Merlin mount point
        QObject.connect(self.menuChangeTargetoX02da,
            SIGNAL("triggered()"),lambda param='x02da': self.changeSubmissionTarget(param))  # MENU change submission target (x02da)
        QObject.connect(self.menuChangeTargetoMerlin,
            SIGNAL("triggered()"),lambda param='Merlin': self.changeSubmissionTarget(param))  # MENU change submission target (Merlin)

        
        ## Context menus
        self.submit.setContextMenuPolicy(Qt.CustomContextMenu);  # Submit button
        self.singleslice.setContextMenuPolicy(Qt.CustomContextMenu);  # Single slice button
        QObject.connect(self.submit,SIGNAL("customContextMenuRequested(const QPoint)"),
                    self.submitAndSingleSliceContextMenu)  # Submit button
        QObject.connect(self.singleslice,SIGNAL("customContextMenuRequested(const QPoint)"),
                    self.submitAndSingleSliceContextMenu)  # Single slice button
        
        ## Set tab order for all fields in GUI
        field_order = ['afsaccount','cons2','inputdirectory','setinputdirectory','inputtype',\
                       'prefix','stitchingtype','raws','darks','flats','interflats','flatfreq',\
                       'preflatsonly','roion','roi_left','roi_right','roi_upper','roi_lower',\
                       'binsize','scaleimagefactor','addpostfix','cprdirectory','setcprdirectory',\
                       'fltpdirectory','setfltpdirectory','sindirectory','setsinogramdirectory',\
                       'sinograms','sinoslider','recodirectory','setrecodirectory','jobname',\
                       'pag_energy','pag_pxsize','pag_delta','pag_beta','pag_distance',
                       'runringremoval','waveletfilterdest','wavelettype','waveletpaddingmode',\
                       'waveletdecompositionlevel','sigmaingaussfilter','runringremovalstd',\
                       'ring_std_mode','ring_std_diff','ring_std_ringwidth','filter',\
                       'cutofffrequency','edgepadding','centerofrotation','outputtype','tifmin',\
                       'tifmax','shiftcorrection','rotationangle','geometry','zingeron',\
                       'zinger_thresh','zinger_width','cpron','withlog','paganinon','fltp_fromtif',\
                       'fltp_fromcpr','sinon','sin_fromtif','sin_fromcpr','sin_fromfltp','steplines'\
                       ,'reconstructon','rec_fromtif','rec_fromsino','openinfiji','submit',\
                       'jobpriority','clearfields','singleslice','print_cmd','develbranchon']
        for key in range(len(field_order)-1):
            self.setTabOrder(getattr(self,field_order[key]), getattr(self,field_order[key+1]))

 
    def submitToCluster(self):
        '''
        This method is launched when pressing the "Submit" button in
        the GUI. First, it performs several checks, creates the command
        line string (CLS) and finally runs the "submitJob" method from
        the job object (see "connector.py").
        '''
        if not self.checkComputingLocation():  # self-explaining
            return
        
        if not ParameterWrap.checkAllParamters():  # missing GUI-fields etc.
            return
        
        if not str(self.jobname.text()):  # we need a job-name and it cannot
            self.jobname_str = 'GRecoM'   # start with a digit
        else:
            if str(self.jobname.text())[0].isdigit():
                self.jobname_str = 'z'+str(self.jobname.text())
            else:
                self.jobname_str = str(self.jobname.text())
            
        if not Prj2sinWrap.createCommand(self):  # returns True if cmd was created
            return 
        
        if self.print_cmd.isChecked():  # prints full CLS if checked 
            if not self.debugTextField():
                 return
        
        if self.job.submitJob(Prj2sinWrap.cmd):
            self.statusBar().showMessage('Job successfully submitted: '+ \
                                         strftime('%H:%M:%S - %x'))
            
            
    def calcSingleSlice(self):
        '''
        This method is launched when pressing "Single Slice" button
        from the GUI. It's similar to "submitToCluster", however, it
        doesn't utilize the "createCommand" method. Instead, it creates
        the command line string (CLS) by calling
        "createSingleSliceCommand" and in the end displays the image.
        '''
        Prj2sinWrap.createSingleSliceCommand(self)

        if self.print_cmd.isChecked():
            if not self.debugTextField():
                 return

        # Create path for reconstructed single slice image
        self.dirs.createSingleSliceImagePath()
        
        if self.openinfiji.isChecked():
            self.job.submitJobLocallyAndWait('fiji -eval \"close(\\"'+ \
                                    str(self.prefix.text())+'*\\");\"')
        
        if self.dirs.checkIfFileExist(self.dirs.img_reco):
            self.job.submitJobLocallyAndWait('rm '+self.dirs.img_reco)
        
        # after all checks completed, singleSliceFunc is called and we wait until image is done
        self.job.submitJob(Prj2sinWrap.cmd)
        
        for kk in range(30):
            if self.dirs.checkIfFileExist(self.dirs.img_reco):
                break
            else:
                sleep(0.5)
        else:
            self.displayErrorMessage('No reconstructed slice found', \
                'After waiting 15 sec the reconstructed slice was not found')
            return
                                    
        # we display the image
        if self.openinfiji.isChecked():
            self.job.submitJobLocally('fiji -eval \"open(\\"'+self.dirs.img_reco+'\\")\"')
        else:
            self.displayImageBig(self.dirs.img_reco)
        
        
    def checkComputingLocation(self):
        '''
        This method makes sure that the radiobox from where GRecoMan is
        run, is checked because it is needed for creating the correct
        directory paths.
        '''
        if not self.afsaccount.isChecked() and not self.cons2.isChecked():
            self.displayErrorMessage('Missing radio box', \
                                     'From where are you running the application?')
            return False
        return True
    
    
    def setUnsetActionCheckBox(self,mode):
        '''
        When unchecking "action" checkboxes, this method makes sure
        that the depended radio-boxes are unset as well. Since we have
        3 different types of radio-boxes we treat 3 modes.
        '''
        if mode == 'sinon':
            dependencies = ['sin_fromcpr','sin_fromfltp','sin_fromtif']
        elif mode == 'paganinon':
            dependencies = ['fltp_fromcpr','fltp_fromtif']
        elif mode == 'reconstructon':
            dependencies = ['rec_fromtif','rec_fromsino','rec_fromfltp']
            
        if not getattr(self,mode).isChecked():
            for param in dependencies:
                ParameterWrap.CLA_dict[param].resetField()
            
            
    def setUnsetFijiOn(self):
        '''
        This method is called when setting to have the preview image in
        Fiji. In that case we check whether the fiji command is
        available in the path and if not we display an error message
        and unset the checkbox again.
        '''
        if self.openinfiji.isChecked():
            if not self.job.isInstalled('fiji'):
                self.openinfiji.setCheckState(0)
                self.displayErrorMessage('Fiji not found', \
                    'fiji must be in PATH, e.g. installed in /urs/bin')
                return
            
            
    def setUnsetComputingLocation(self):
        '''
        This method checks the computing location and directory paths
        and changes the directories if necessary. It should be run when
        toggling the computing location and after loading config files. 
        '''
        paths = ['inputdirectory','cprdirectory','fltpdirectory',
                 'sindirectory','recodirectory']
        
        if not self.target == 'x02da':
            return
        
        for path_item in paths:
            path = str(getattr(self,path_item).text()) 
            if self.afsaccount.isChecked():
                if path[0:16] == '/sls/X02DA/data/' and \
                        self.dirs.homedir[0:16] == '/afs/psi.ch/user':
                    newpath = self.dirs.cons2Path2afs(path)
                    getattr(self,path_item).setText(newpath)
            
            if self.cons2.isChecked():
                if path[0:16] == '/afs/psi.ch/user':
                    newpath = self.dirs.afsPath2Cons2(path)
                    getattr(self,path_item).setText(newpath)


    def setSinoWithSlider(self):
        ''' Changes the sinogram in combobox by moving slider '''
        if not self.sinograms.count() == 0:
            ind = self.sinoslider.value()
            self.sinograms.setCurrentIndex(int(ind))
        
            
    def saveConfigFile(self):
        '''
        This method is run when pressing Menu->Save settings.
        '''
        savefile = QFileDialog.getSaveFileName(self,
                        'Select where the config file should be saved',self.lastdir_config)
        if not savefile:
            return
        if not str(savefile).lower().endswith('.txt'):
            savefile = str(savefile)+'.txt'
        file_obj = ConfigFile(self,savefile)
        file_obj.writeFile(ParameterWrap)
        self.lastdir_config = self.dirs.getParentDir(str(savefile))
        
        
    def loadConfigFile(self, loadfile = '', returnvalue = False, overwrite = True):
        '''
        This method is used for loading both, config-files (from Menu)
        and pre-set templates by stating the explicit filename. If
        returnvalue is set True then the method returns the config-file
        object, which is used by "loadSpecificFromConfigFile" to load
        only specific GUI-fields. If overwrite is False then empty
        fields from config-file are not overwriting GUI-fields
        '''
        if not loadfile:
            loadfile = QFileDialog.getOpenFileName(self,
                        'Select where the config file is located',self.lastdir_config)
        if not loadfile:
            return
        file_obj = ConfigFile(self,loadfile)
        
        if returnvalue:
            return file_obj
        
        self.lastdir_config = self.dirs.getParentDir(str(loadfile))
        file_obj.loadFile(overwrite)
        self.setUnsetComputingLocation()
        self.dirs.inputdir = self.inputdirectory.text()
        if not str(self.sindirectory.text()) == '':
            self.dirs.initSinDirectory()
        
        
    def loadSpecificFromConfigFile(self,param_list):
        '''
        Loads specific parameters (GUI-fields) written in a list
        ("param_list").
        '''
        file_obj = self.loadConfigFile([], True, False)  # We open the configfile
        file_obj.config.read(file_obj.cfgfile)  # We load here the parameters from configfile
        for param in param_list:
            file_obj.loadSingleParamter(param,True)
        
        
    def loadTemplate(self, templatename):
        '''
        This method loads a given template for performing one or more
        cluster calculations. It is basically the same as loading a
        config file (with "loadConfigFile" method), only with
        additional color-highlighting.
        '''
        template_file = self.dirs.glueOsPath([self.dirs.runningdir, \
                                              'templates' ,templatename+'.txt'])
        template_obj = self.loadConfigFile(template_file, True)
        template_obj.loadFile(False)
        
        ParameterWrap.resetAllStyleSheets()
        for param in template_obj.config.options(template_obj.heading):
            name_handle = getattr(self,param)
            name_handle.setStyleSheet("QLineEdit { border : 2px solid green;}")
    
    
    def getDirectory(self,mode,infostring = ''):
        '''
        Dialog for setting a directory source with QFileDialog. First,
        we update "lastdir" property. After that, depending on the
        directory, the textfields are updated and initialized.
        '''
        if not infostring:
            infostring = 'Select direcory'
        
        dir_temp = QFileDialog.getExistingDirectory(self,
                            infostring,self.lastdir)
        if not dir_temp:
            return

        self.lastdir = self.dirs.getParentDir(str(dir_temp))
        
        if mode == 'merlin_mount_dir':
            self.dirs.merlin_mount_dir = dir_temp
            return
        else:
            getattr(self,mode).setText(dir_temp)
        
        if mode == 'inputdirectory':
            self.dirs.initInputDirectory()
            return
        elif mode =='sindirectory':
            self.dirs.initSinDirectory()
            return

        
    def displayErrorMessage(self,head,msg):
        ''' Displays random error messages with QMessageBox '''
        QMessageBox.warning(self, head, msg)        

        
    def displayYesNoMessage(self,head,txt):
        ''' Displays dialog with "yes"/"no" and defined heading/text '''
        question = QMessageBox.warning(self, head, txt, QMessageBox.Yes, QMessageBox.No)
        
        if question == QMessageBox.Yes:
            return True
        else:
            return False 
        
        
    def displayImageBig(self,img_file):
        ''' Displays the DMP image "img_file" in the preview window '''
        self.img_obj = Image(img_file)
        
        img = QImage(self.img_obj.img_disp, self.img_obj.img_width,
                     self.img_obj.img_height, QImage.Format_RGB32)
        img = QPixmap.fromImage(img)
            
        myScaledPixmap = img.scaled(self.ImgViewer.size(), Qt.KeepAspectRatio)
        self.ImgViewer.setPixmap(myScaledPixmap)
        
        
    def debugTextField(self):
        '''
        Textfield that prints the command line string (CLS) for further
        editing (derived from "DebugCommand" class from ui_dialogs.py).
        It saves the (un-)/edited text string into the class property
        "cmd" to which is then submitted to the cluster.
        '''
        debugwin = DebugCommand(self.parent)
        QTextEdit.insertPlainText(debugwin.textfield, Prj2sinWrap.cmd)
        if debugwin.exec_() == QDialog.Accepted:
            tmp_string = str(QTextEdit.toPlainText(debugwin.textfield)).strip()
            self.Prj2sinWrap = ' '.join(tmp_string.split())
            return True
        else:
            return False
        
        
    def moveSliderBySinochange(self):
        '''
        This method moves the slider when selecting a sinogram from the
        Dropdown menu. 
        '''
        ind = self.sinograms.currentIndex()
        self.sinoslider.setSliderPosition(ind)
        
        
    def changeOutputType(self):
        '''
        This method is called whenever the combobox for output type is
        changed. It appends the correct reco-output directory.
        '''
        types = ['rec_8bit','rec_DMP','rec_DMP_HF5','rec_16bit','rec_8bit','unknown_output']
        ind = self.outputtype.currentIndex()
        self.dirs.setOutputDirectory(types[ind])
        
        
    def submitAndSingleSliceContextMenu(self,point):
        '''
        Context menu for "Submit" and "SingleSlice" buttons. When right-
        clicking on one of these and "setting a target" the
        "changeSubmissionTarget" method gets executed.
        '''
        menu     = QMenu()
        button_handle = self.sender()
        
        submit1 = menu.addAction("Set to x02da")
        submit2 = menu.addAction("Set to Merlin")
    
        self.connect(submit1,SIGNAL("triggered()"),
                    lambda param='x02da': self.changeSubmissionTarget(param))
        self.connect(submit2,SIGNAL("triggered()"),
                    lambda param='Merlin': self.changeSubmissionTarget(param))
        menu.exec_(button_handle.mapToGlobal(point))
        
        
    def changeSubmissionTarget(self,target):
        '''
        Sets the "target" property accordingly and additionally labels
        the GUI buttons. If Merlin is the target, then the Merlin
        username is asked (by running "performInitalCheck" from the job
        object) in order to create correct directory paths on Merlin.
        '''
        self.target = target
        self.submit.setText("Submit "+"("+target+")")
        self.singleslice.setText("Single slice "+"("+target+")")
        if target == 'Merlin':
            self.afsaccount.setChecked(1)
            self.job.performInitalCheck()
            if not self.dirs.merlin_mount_dir:
                self.getDirectory('merlin_mount_dir','Select where the Merlin directory is mounted')
        
                
    def dragEnterEvent(self, event):
        '''
        This method accepts dragging files from outside into the
        application
        '''
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event):
        '''
        This method tries to load a config file after being dropped
        into the application. When multiple files are dropped, only the
        last one is loaded.
        '''
        for path in event.mimeData().urls():
            self.loadConfigFile( path.toLocalFile().toLocal8Bit().data() )
            
            
    def appendPostfix(self):
        '''
        This method opens a textfield and appends a postfix to all
        directories: cpr, fltp, sin, rec_Xbit
        '''
        logwin = Postfix(self.parent)
        if not logwin.exec_() == Postfix.Accepted:  # if ESC is hit
            return

        if not logwin.postfix.text():  # if postfix text is empty
            added_string = '/'
        else:
            added_string = '__'+str(logwin.postfix.text())+'/'
            
        fields = ['cprdirectory','fltpdirectory','sindirectory','recodirectory']
        
        for item in fields:
            handle = getattr(self,item)
            item_txt = str(handle.text())
            if not item_txt:
                continue
            else:
                if item_txt[-1] == '/':
                    newstring = item_txt[:-1]
                else:
                    newstring = item_txt
            try:
                ind = newstring.index('__')
            except ValueError:
                ind = len(newstring)
            handle.setText(newstring[0:ind]+added_string)
        

if __name__ == "__main__":
    sysargs = sys.argv+['-style', 'mac']
    mainapp = QApplication(sysargs,True)  # create Qt application
    win = MainWindow()  # create main window
    win.show()
 
    # Connect signals for mainapp
    mainapp.connect(mainapp, SIGNAL("lastWindowClosed()"), mainapp, SLOT("quit()"))
    mainapp.connect(win.exitapp, SIGNAL("triggered()"), mainapp, SLOT("quit()"))
 
    # Start up mainapp
    sys.exit(mainapp.exec_())