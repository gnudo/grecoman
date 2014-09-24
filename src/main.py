from ui_main import Ui_reco_mainwin
from ui_dialogs import DebugCommand
from dmp_reader import DMPreader
from arguments import ParameterWrap
from connector import Connector
from datasets import DatasetFolder
from fileIO import ConfigFile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep,strftime # TODO: preliminary
import os.path  # TODO: preliminary
import sys


class MainWindow(QMainWindow, Ui_reco_mainwin):
    '''
    main class containing methods for ideally all window actions in the main app. other specific
    methods should be contained in other classes
    '''
 
    def __init__(self):        
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
        QObject.connect(self.sinon,
            SIGNAL("clicked()"),lambda param='sinon': self.setUnsetActionCheckBox(param))  # sinogram checkbox ("toggled" not working)
        QObject.connect(self.paganinon,
            SIGNAL("clicked()"),lambda param='paganinon': self.setUnsetActionCheckBox(param))  # Paganin checkbox ("toggled" not working)
        QObject.connect(self.reconstructon,
            SIGNAL("clicked()"),lambda param='reconstructon': self.setUnsetActionCheckBox(param))  # Reco checkbox ("toggled" not working)
        QObject.connect(self.openinfiji,
            SIGNAL("clicked()"),self.setUnsetFijiOn)  # Fiji preview image checkbox ("toggled" not working)
        QObject.connect(self.outputtype,
            SIGNAL("currentIndexChanged(const QString&)"),self.changeOutputType)  # change output-dir name according to output type
        self.afsaccount.toggled.connect(self.setUnsetComputingLocation)  # Computing location radio box
        self.cons2.toggled.connect(self.setUnsetComputingLocation)  # Computing location radio box
        self.sinoslider.valueChanged.connect(self.setSinoWithSlider)  # Sinograms slider event
        
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
        QObject.connect(self.menusavesettings,
            SIGNAL("triggered()"),self.saveConfigFile)  # MENU save settings
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
                       'binsize','scaleimagefactor','cprdirectory','setcprdirectory',\
                       'fltpdirectory','setfltpdirectory','sindirectory','setsinogramdirectory',\
                       'sinograms','recodirectory','setrecodirectory','jobname','pag_energy',\
                       'pag_pxsize','pag_delta','pag_beta','pag_distance','runringremoval',\
                       'wavelettype','waveletpaddingmode','waveletdecompositionlevel',
                       'sigmaingaussfilter','filter','cutofffrequency','edgepadding',\
                       'centerofrotation','outputtype','tifmin','tifmax','shiftcorrection',\
                       'rotationangle','geometry','zingeron','zinger_thresh','zinger_width','cpron',\
                       'withlog','paganinon','fltp_fromtif','fltp_fromcpr','sinon','sin_fromtif',\
                       'sin_fromcpr','sin_fromfltp','steplines','reconstructon','rec_fromtif',\
                       'rec_fromsino','openinfiji','submit','clearfields','singleslice','print_cmd',\
                       'develbranchon']
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
            
        if not self.createCommand():  # returns True if further checks succeed
            return
        
        if self.print_cmd.isChecked():  # prints full CLS if checked 
            if not self.debugTextField():
                 return
        
        if not self.job.performInitalCheck():  # check account credentials
            return
        
        if self.job.checkIdenticalJobs(self.cmd):
            if not self.displayYesNoMessage('Identical Job','You have' \
                    ' submitted an identical job just before. Are you' \
                    ' sure you want to submit it again?'):
                self.statusBar().clearMessage()
                return
        
        self.job.submitJob(self.cmd)
        self.statusBar().showMessage('Job successfully submitted: '+strftime('%H:%M:%S - %x'))
            
            
    def calcSingleSlice(self):
        '''
        This method is launched when pressing "Single Slice" button
        from the GUI. It's similar to "submitToCluster", however, it
        doesn't utilize the "createCommand" method. Instead, it creates
        the command line string (CLS) itself and in the end displays
        the image.
        '''
        if not str(self.sinograms.currentText()):
            self.displayErrorMessage('No sinogram selected', 'Select the Sinogram directory and press Enter. Then select one to be reconstructed.')
            return
        
        if not self.checkComputingLocation():  # self-explaining
            return

        # create the command line string for single slice reconstruction
        self.cmd = '/usr/bin/python /afs/psi.ch/project/tomcatsvn/executeables/grecoman/externals/singleSliceFunc.py '
        
        combos_single = ['filter','geometry']
        for combo in combos_single:
            if ParameterWrap.CLA_dict[combo].performCheck():
                self.cmd += ParameterWrap.CLA_dict[combo].flag+' '+ParameterWrap.getComboBoxContent(combo)+' ' 
        
        if self.zingeron.isChecked():
            self.cmd += self.setZingerParameters()
        
        optional_single = ['cutofffrequency','edgepadding','centerofrotation','rotationangle']
        for param in optional_single:
            if not getattr(self,param).text() == '':
                self.cmd += ParameterWrap.CLA_dict[param].flag+' '+getattr(self,param).text()+' '
        
        if self.runringremoval.isChecked():  # the wavelet parameters are composed separately
            self.cmd += self.setWavletParameters()
            
        if self.runringremovalstd.isChecked():
            self.cmd += self.setStandardRingRemoval()
        
        # rewrite the sinogram-directory for use at the appropriate machine
        single_sino = self.dirs.rewriteDirectoryPath(self.sindirectory.text(),'forward')
        
        self.cmd += '-x '+self.target+' '
        self.cmd += '--Di '+single_sino+' -i '+self.sinograms.currentText()
        
        if self.print_cmd.isChecked():
            if not self.debugTextField():
                 return

        if not self.job.performInitalCheck():  # check account credentials
            return
        
        # TODO: probably whole part below should be rewritten and
        # outsourced to "imageOpen class" or similar...
        # we look for the image and delete it if it exists
        basedir = self.dirs.rewriteDirectoryPath(self.dirs.getParentDir(single_sino),'backward')
        
        new_filename = self.sinograms.currentText()[:-7]+'rec.'
        img = basedir+'viewrec/'+str(new_filename+self.sinograms.currentText()[-3:])
        
        if self.openinfiji.isChecked():
            self.job.submitJobLocallyAndWait('fiji -eval \"close(\\"'+str(self.prefix.text())+'*\\");\"')
        
        if os.path.isfile(img):
            self.job.submitJobLocallyAndWait('rm '+img)  
        
        # after all checks completed, singleSliceFunc is called and we wait until image is done
        self.job.submitJob(self.cmd)
        
        for kk in range(30):
            if os.path.isfile(img):
                break
            else:
                sleep(0.5)
        else:
            self.displayErrorMessage('No reconstructed slice found', 'After waiting 15 sec the reconstructed slice was not found')
            return
                                    
        # we display the image
        if self.openinfiji.isChecked():
            self.job.submitJobLocally('fiji -eval \"open(\\"'+img+'\\")\"')
        else:
            self.displayImageBig(img)
 

    def createCommand(self):
        '''
        This is the main method for creating the command line stirng
        (CLS) which dependent on the checked "actions" in the GUI calls
        other methods like "createCprAndFltpCmd", "createSinCmd" etc.
        We have three different properties in use: (i) self.cmd is full
        CLS to be submitted to the cluster (ii) self.cmds is a list of
        separate cluster commands and (ii) self.cmd0 is the cluster
        command for executing a single action.
        '''
        self.cmd = ''
        self.cmds = []
        
        if self.develbranchon.isChecked():
            self.cmd0 = "/afs/psi/project/TOMCAT_pipeline/Devel/tomcat_pipeline/src/prj2sinSGE.sh "
        else:
            self.cmd0 = "prj2sinSGE "
        
        # (1) We check whether we need to create CPR-s.
        if self.cpron.isChecked():
            if not self.createCprAndFltpCmd('cpr',self.jobname_str):
                return False
        
        # (2) Then we check whether we need FLTP-s.
        if self.paganinon.isChecked():
            if not self.fltp_fromtif.isChecked() and not self.fltp_fromcpr.isChecked():
                self.displayErrorMessage('Missing fltp source', 'Please select whether fltp-s should be created from tif or cpr-s!')
                return False
            if not self.createCprAndFltpCmd('fltp',self.jobname_str):
                return False
            
        # (3) After that we check whether we need sinograms.
        if self.sinon.isChecked():
            if not self.createSinCmd(self.jobname_str):
                return False
            
        ## (4) Finally we check whether reconstructions will be created.
        if self.reconstructon.isChecked():
            if not self.createRecoCmd(self.jobname_str):
                return False
        
        for cmd_tmp in self.cmds:  # compose the full CLS
            self.cmd = self.cmd+cmd_tmp+';' 
        
        return True
            
    
    def createCprAndFltpCmd(self,mode,jobname):
        '''
        This method is used to compose both, the command line string
        (CLS) for creating cprs and/or for creating fltps (since they
        are both very similar). Understanding the following code is not
        expected, as it requires also the understanding of the
        reconstruction pipeline.
        '''
        ## Compose all mandatory
        standard = '-d -C '
        cmd1 = self.cmd0+standard
        
        if self.cpron.isChecked() and not self.paganinon.isChecked():
            if self.withlog.isChecked():
                g_param = 7
            else:
                g_param = 3
        elif self.fltp_fromcpr.isChecked() and mode == 'fltp':
            g_param = 0
        elif self.fltp_fromtif.isChecked() and mode == 'fltp':
            g_param = 3
        else: # case for mode == 'cpr'
            g_param = 3
        
        # only if CPR if set, else only in FLTP
        if mode == 'cpr' or self.fltp_fromtif.isChecked():
            optional = ['binsize', 'scaleimagefactor']
            cmd1 += '-f '+self.raws.text()
            cmd1 += ','+self.darks.text()
            cmd1 += ','+self.flats.text()
            cmd1 += ','+self.interflats.text()
            cmd1 += ','+self.flatfreq.text()+' '
            cmd1 += ParameterWrap.CLA_dict['inputtype'].flag+' '+ParameterWrap.getComboBoxContent('inputtype')+' '
            for param in optional:
                if not getattr(self,param).text() == '':
                    cmd1 += ParameterWrap.CLA_dict[param].flag+' '+getattr(self,param).text()+' '
            
            # Region of interest optional
            if getattr(self,'roion').isChecked():
                cmd1 += ParameterWrap.CLA_dict['roion'].flag+' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    cmd1 += getattr(self,child).text()+','
                cmd1 = cmd1[:-1]+' '
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.tif '
        else:
            cmd1 += '-f '+self.raws.text()
            cmd1 += ',0,0,0,0 '
            cmd1 += '-I 0 '
            if self.cpron.isChecked():
                cmd1 += '--hold='+jobname+'_cpr '
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.cpr.DMP '
        
        cmd1 += '--jobname='+jobname+'_'+mode+' '
        
        # optional job priority
        if not getattr(self,'jobpriority').currentIndex() == 0:
            cmd1 += ParameterWrap.CLA_dict['jobpriority'].flag+'='
            cmd1 += ParameterWrap.getComboBoxContent('jobpriority')+' '
  
        # probably increases job priority on Merlin (?!)
        if self.target == 'Merlin':
            cmd1 += '--queue=prime_ti.q --ncores=16 ' 
  
        # only for Paganin phase retrieval
        if mode == 'fltp':
            cmd1 += ParameterWrap.CLA_dict['paganinon'].flag+' '
            for child in ParameterWrap.CLA_dict['paganinon'].child_list[:-1]:
                cmd1 += getattr(self,child).text()+','
            cmd1 = cmd1[:-1]+' '
                
        # only in CPR if cpr is set , else only in FLTP
        if mode == 'cpr' or not self.cpron.isChecked():
            if getattr(self,'preflatsonly').isChecked():
                cmd1 += ParameterWrap.CLA_dict['preflatsonly'].flag+' '
        
        cmd1 += '-g '+str(g_param)+' '
        
        ## define input and output dirs
        if mode == 'cpr':
            inputdir = self.inputdirectory.text()
            outputdir = self.cprdirectory.text()
        elif mode == 'fltp':
            if self.fltp_fromcpr.isChecked():
                inputdir = self.cprdirectory.text()
            else:
                inputdir = self.inputdirectory.text()
            outputdir = self.fltpdirectory.text()
        else:
            inputdir = self.cprdirectory.text()
            outputdir = self.fltpdirectory.text()

        cmd1 += '-o '+self.dirs.rewriteDirectoryPath(outputdir,'forward')+' '
        cmd1 += self.dirs.rewriteDirectoryPath(inputdir,'forward')

        self.cmds.append(cmd1)
        return True
    
    
    def createSinCmd(self,jobname):
        '''
        This method is used to compose the command line string (CLS)
        for creating sinograms. Again, understanding the following code
        is not expected, as it requires also the understanding of the
        reconstruction pipeline.
        '''
        if self.sin_fromtif.isChecked():
            standard = '-d -g 7 -I 1 '
            cmd1 = self.cmd0+standard
            cmd1 += '-f '+self.raws.text()
            cmd1 += ','+self.darks.text()
            cmd1 += ','+self.flats.text()
            cmd1 += ','+self.interflats.text()
            cmd1 += ','+self.flatfreq.text()+' '
            if getattr(self,'roion').isChecked():
                cmd1 += ParameterWrap.CLA_dict['roion'].flag+' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    cmd1 += getattr(self,child).text()+','
                cmd1 = cmd1[:-1]+' '
        else:
            standard = '-d -k 2 -g 0 -I 0 '
            cmd1 = self.cmd0+standard
            cmd1 += '-f '+self.raws.text()
            cmd1 += ',0,0,0,0 '
        
        for param in ['preflatsonly','shiftcorrection']:
            if getattr(self,param).isChecked():
                    cmd1 += ParameterWrap.CLA_dict[param].flag+' '
        
        if self.runringremoval.isChecked():  # wavelet parameters
            cmd1 += '-k 2 '
            cmd1 += self.setWavletParameters()
        else:
            cmd1 += '-k 1 '
        
        # set correct jobname in order to wait for other jobs to finish
        if self.cpron.isChecked() and not self.paganinon.isChecked():
            cmd1 += '--hold='+jobname+'_cpr '
        elif self.paganinon.isChecked():
            cmd1 += '--hold='+jobname+'_fltp '
            
        cmd1 += '--jobname='+jobname+'_sin '
        
        # optional job priority
        if not getattr(self,'jobpriority').currentIndex() == 0:
            cmd1 += ParameterWrap.CLA_dict['jobpriority'].flag+'='
            cmd1 += ParameterWrap.getComboBoxContent('jobpriority')+' '
        
        # probably increases job priority on Merlin (?!)
        if self.target == 'Merlin':
            cmd1 += '--queue=prime_ti.q --ncores=16 '
        
        if ParameterWrap.CLA_dict['steplines'].performCheck():
            cmd1 += ParameterWrap.CLA_dict['steplines'].flag+' '+getattr(self,'steplines').text()+' '
            
        if ParameterWrap.CLA_dict['stitchingtype'].performCheck():
            cmd1 += ParameterWrap.CLA_dict['stitchingtype'].flag+' '+ParameterWrap.getComboBoxContent('stitchingtype')+' '
        
        if self.sin_fromcpr.isChecked():
            inputdir = self.cprdirectory.text()
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.cpr.DMP '
        elif self.sin_fromfltp.isChecked():
            inputdir = self.fltpdirectory.text()
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.fltp.DMP '
        elif self.sin_fromtif.isChecked():
            inputdir = self.inputdirectory.text()
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.tif '
        else:
            self.displayErrorMessage('No sinogram source defined', 'Check the radio box, from where to create sinograms')
            return
        
        cmd1 += '-o '+self.dirs.rewriteDirectoryPath(self.sindirectory.text(),'forward')+' '
        cmd1 += self.dirs.rewriteDirectoryPath(inputdir,'forward')
            
        self.cmds.append(cmd1)
        return True
    
    
    def createRecoCmd(self,jobname):
        '''
        This method is used to compose the command line string (CLS)
        for creating tomographic reconstructions. Again, understanding
        the following code is not expected, as it requires also the
        understanding of the reconstruction pipeline.
        '''
        ## Compose all mandatory
        if self.rec_fromtif.isChecked():
            inputdir = self.inputdirectory.text()
            standard = '-d -R 0 -k 0 -I 1 -g 7 '
            standard += '-f '+self.raws.text()
            standard += ','+self.darks.text()
            standard += ','+self.flats.text()
            standard += ','+self.interflats.text()
            standard += ','+self.flatfreq.text()+' '
            if ParameterWrap.CLA_dict['stitchingtype'].performCheck():
                standard += ParameterWrap.CLA_dict['stitchingtype'].flag + \
                        ' '+ParameterWrap.getComboBoxContent('stitchingtype')+' '
            if self.runringremoval.isChecked():  # wavelet parameters
                standard += self.setWavletParameters()
            if getattr(self,'roion').isChecked():
                standard += ParameterWrap.CLA_dict['roion'].flag+' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    standard += getattr(self,child).text()+','
                standard = standard[:-1]+' '
            standard += ParameterWrap.CLA_dict['prefix'].flag+' '+ \
                        getattr(self,'prefix').text()+'####.tif '
        elif self.rec_fromsino.isChecked():
            inputdir = self.sindirectory.text()
            standard = '-d -k 1 -I 3 -R 0 -g 0 '
        else:
            self.displayErrorMessage('No reconstruction source defined', 'Check the radio box, from where to create reconstructions')
            return
            
        cmd1 = self.cmd0+standard

        optional = ['cutofffrequency','edgepadding','centerofrotation','rotationangle','tifmin','tifmax']
        for param in optional:
            if not getattr(self,param).text() == '':
                cmd1 += ParameterWrap.CLA_dict[param].flag+' '+getattr(self,param).text()+' '
        
        ## (4) Comboboxes with respective dictionaries (except wavelet)
        comboboxes = ['filter', 'outputtype', 'geometry']
        for combo in comboboxes:
            if ParameterWrap.CLA_dict[combo].performCheck():
                cmd1 += ParameterWrap.CLA_dict[combo].flag+' '+ParameterWrap.getComboBoxContent(combo)+' '
                
        ## (5) Standard ring removal parameters
        if self.runringremovalstd.isChecked():
            cmd1 += self.setStandardRingRemoval()
            
        ## (6) Zinger removal
        if self.zingeron.isChecked() and self.zingermode.currentIndex() == 0:
            cmd1 += self.setZingerParameters()
                
        # set correct jobname in order to wait for other jobs to finish
        if self.sinon.isChecked() and self.rec_fromsino.isChecked():
            cmd1 += '--hold='+jobname+'_sin '
            
        cmd1 += '--jobname='+jobname+'_reco '
        
        # optional job priority
        if not getattr(self,'jobpriority').currentIndex() == 0:
            cmd1 += ParameterWrap.CLA_dict['jobpriority'].flag+'='
            cmd1 += ParameterWrap.getComboBoxContent('jobpriority')+' '
        
        # probably increases job priority on Merlin (?!)
        if self.target == 'Merlin':
            cmd1 += '--queue=prime_ti.q --ncores=16 '
        
        outputdir = self.recodirectory.text()
        sinodir_tmp = self.dirs.getParentDir(inputdir)
        sinodir_tmp = self.dirs.glueOsPath([sinodir_tmp,'sino_tmp'])
        
        if self.rec_fromtif.isChecked():
            cmd1 += '-o '+self.dirs.rewriteDirectoryPath(sinodir_tmp,'forward')+' '
        cmd1 += '-O '+self.dirs.rewriteDirectoryPath(outputdir,'forward')+' '
        cmd1 += self.dirs.rewriteDirectoryPath(inputdir,'forward')
        
        self.cmds.append(cmd1)
        return True
        
        
    def checkComputingLocation(self):
        '''
        This method makes sure that the radiobox from where GRecoMan is
        run, is checked and will also determine this in future releases
        automatically.
        '''
        if not self.afsaccount.isChecked() and not self.cons2.isChecked():
            self.displayErrorMessage('Missing radio box', 'From where are you running the application?')
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
            dependencies = ['rec_fromtif','rec_fromsino']
            
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
        paths = ['inputdirectory','cprdirectory','fltpdirectory','sindirectory','recodirectory']
        
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
        ''' Changes the sinogram in combo by moving slider '''
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
        template_file = self.dirs.glueOsPath([self.dirs.runningdir, 'templates' ,templatename+'.txt'])
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
            
        
    def setWavletParameters(self):
        '''
        Method for adding the wavelet correction to the command line
        string.
        '''
        combos = ['wavelettype','waveletpaddingmode']
        textedit = ['waveletdecompositionlevel','sigmaingaussfilter']
        cmd = ParameterWrap.CLA_dict[combos[0]].flag+' '+str(getattr(self,combos[0]).currentText())+' '
        cmd += ParameterWrap.CLA_dict[textedit[0]].flag+' '+getattr(self,textedit[0]).text()+' '
        cmd += ParameterWrap.CLA_dict[textedit[1]].flag+' '+getattr(self,textedit[1]).text()+' '
        cmd += ParameterWrap.CLA_dict[combos[1]].flag+' '+ParameterWrap.getComboBoxContent(combos[1])+' '
        return cmd
    
    
    def setStandardRingRemoval(self):
        ''' Method for setting the standard ring removal parameters '''
        cmd = ParameterWrap.CLA_dict['ring_std_mode'].flag+' '+ParameterWrap.getComboBoxContent('ring_std_mode')+' '
        cmd += ParameterWrap.CLA_dict['ring_std_diff'].flag+' '+getattr(self,'ring_std_diff').text()+' '
        cmd += ParameterWrap.CLA_dict['ring_std_ringwidth'].flag+' '+getattr(self,'ring_std_ringwidth').text()+' '
        return cmd
        
        
    def setZingerParameters(self):
        '''
        method for adding zinger removal parameters
        '''
        cmd = '-z s ' ## TODO: has to be fixed after 2D version is implemented
        cmd += ParameterWrap.CLA_dict['zinger_thresh'].flag+' '+str(getattr(self,'zinger_thresh').text())+' '
        cmd += ParameterWrap.CLA_dict['zinger_width'].flag+' '+str(getattr(self,'zinger_width').text())+' '
        return cmd

        
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
        '''
        method for displaying a single image in the big frame
        TODO: to be outsourced
        '''
        if img_file[-3:].lower() == 'tif':
            myPixmap = QPixmap(img_file)
        elif img_file[-3:].lower() == 'dmp':
            myPixmap = DMPreader(img_file)
            
        myScaledPixmap = myPixmap.scaled(self.ImgViewer.size(), Qt.KeepAspectRatio)
        self.ImgViewer.setPixmap(myScaledPixmap)
        
        
    def debugTextField(self):
        '''
        Textfield that prints the command line string (CLS) for further
        editing (derived from "DebugCommand" class from ui_dialogs.py).
        It saves the (un-)/edited text string into the class property
        "cmd" to which is then submitted to the cluster.
        '''
        debugwin = DebugCommand(self.parent)
        QTextEdit.insertPlainText(debugwin.textfield, self.cmd)
        if debugwin.exec_() == QDialog.Accepted:
            tmp_string = str(QTextEdit.toPlainText(debugwin.textfield)).strip()
            self.cmd = ' '.join(tmp_string.split())
            return True
        else:
            return False
        
        
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
        Sets the "target" property accordingly and addiotionally labels
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