from ui_main import Ui_reco_mainwin
from dmp_reader import DMPreader
from arguments import ParameterWrap
from connector import Connector
from advanced_checks import AdvancedChecks
from fileIO import FileIO
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep # TODO: preliminary
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
        self.dirs = AdvancedChecks(self)  # Object for performing all operations on dirs
        self.lastdir = self.dirs.homedir  # set the starting open directory to HOME
        self.changeSubmissionTarget('x02da')  # set the submission target standardly to x02da
        
        ## GUI fields connections
        QObject.connect(self.setinputdirectory,
            SIGNAL("clicked()"),lambda param='input_dir': self.getDirectory(param))  # data input directory
        QObject.connect(self.inputdirectory,
            SIGNAL("returnPressed()"),self.dirs.initInputDirectory)  # data input through keyboard
        QObject.connect(self.sinogramdirectory,
            SIGNAL("returnPressed()"),self.dirs.initSinDirectory)  # sinogram dir input through keyboard
        QObject.connect(self.setsinogramdirectory,
            SIGNAL("clicked()"),lambda param='sinodir': self.getDirectory(param))  # sinogram output
        QObject.connect(self.setcprdirectory,
            SIGNAL("clicked()"),lambda param='cprdirectory': self.getDirectory(param))  # cpr output
        QObject.connect(self.setfltpdirectory,
            SIGNAL("clicked()"),lambda param='fltpdir': self.getDirectory(param))  # fltp output
        QObject.connect(self.setrecodirectory,
            SIGNAL("clicked()"),lambda param='recodir': self.getDirectory(param))  # reconstructions output
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
        
        ## Context menus
        self.submit.setContextMenuPolicy(Qt.CustomContextMenu);  # Submit button
        self.singleslice.setContextMenuPolicy(Qt.CustomContextMenu);  # Single slice button
        QObject.connect(self.submit,SIGNAL("customContextMenuRequested(const QPoint)"),
                    self.submitAndSingleSliceContextMenu)  # Submit button
        QObject.connect(self.singleslice,SIGNAL("customContextMenuRequested(const QPoint)"),
                    self.submitAndSingleSliceContextMenu)  # Single slice button
        
 
    def submitToCluster(self):
        '''
        method that launches all the checks and if successful submits the
        command to cons-2 for starting the job
        '''
        if not self.checkComputingLocation():
            return
        
        if not ParameterWrap.checkAllParamters():
            return
        
        # (1) Create command line string
        if not str(self.jobname.text()):
            self.jobname_str = 'GRecoM'
        else:
            self.jobname_str = str(self.jobname.text())
            
        self.cmd = ''
        if not self.createCommand():
            return
        
        if self.print_cmd.isChecked():
            if not self.debugTextField():
                 return
        
        # (2) run SSH-connector and check all account credentials
        if not self.job.performInitalCheck():
            return
        
        # (3) run SSh-connector to launch the job
        if self.afsaccount.isChecked():
            self.job.submitJobViaGateway(self.cmd+'\n','x02da-gw','x02da-cons-2')
        elif self.cons2.isChecked():
            self.job.submitJobLocally(self.cmd)
            
            
    def calcSingleSlice(self):
        '''
        method for renconstructing a single slice for a given sinogram.
        '''
        if not str(self.sinograms.currentText()):
            self.displayErrorMessage('No sinogram selected', 'Select the Sinogram directory and press Enter. Then select one to be reconstructed.')
            return
        
        ## (1) check whether we have defined the location from where we run the reconstruction
        if not self.checkComputingLocation():
            return
        
        ## (2) before calculating on x02da-cons-2, we need to rewrite the path of the sino dir
        if self.afsaccount.isChecked():
            single_sino = self.dirs.afsPath2Cons2(self.sinogramdirectory.text())
        elif self.cons2.isChecked():
            single_sino = str(self.sinogramdirectory.text())

        ## (3) create the command line string for single slice reconstruction
        self.cmd = '/usr/bin/python /afs/psi.ch/project/tomcatsvn/executeables/grecoman/externals/singleSliceFunc.py '
        
        combos_single = ['filter','geometry']  # removed: 'outputtype' (let's always have DMP!)
        for combo in combos_single:
            if ParameterWrap.CLA_dict[combo].performCheck():
                self.cmd += ParameterWrap.CLA_dict[combo].flag+' '+ParameterWrap.getComboBoxContent(combo)+' ' 
        
        if self.zingeron.isChecked():
            self.setZingerParameters()
        
        optional_single = ['cutofffrequency','edgepadding','centerofrotation','rotationangle']
        for param in optional_single:
            if not getattr(self,param).text() == '':
                self.cmd += ParameterWrap.CLA_dict[param].flag+' '+getattr(self,param).text()+' '
        
        if self.runringremoval.isChecked():  # the wavelet parameters are composed separately
            self.cmd += self.setWavletParameters()
        
        self.cmd += '--Di '+single_sino+' -i '+self.sinograms.currentText()
        
        if self.print_cmd.isChecked():
            if not self.debugTextField():
                 return
        
        ## (4) now we check credentials
        if not self.job.performInitalCheck():
            return
        
        ## (5) we look for the image and delete it if it exists
        # TODO: just preliminary as the whole PATH-modification things should be
        #       outsourced (we want to avoid spaghetti-code!)
        if self.afsaccount.isChecked():
            basedir = self.dirs.cons2Path2afs(self.dirs.getParentDir(single_sino))
        elif self.cons2.isChecked():
            basedir = self.dirs.getParentDir(single_sino)
            
        new_filename = self.sinograms.currentText()[:-7]+'rec.'
        img = basedir+'/viewrec/'+str(new_filename+self.sinograms.currentText()[-3:])
        
        if self.openinfiji.isChecked():
            self.job.submitJobLocallyAndWait('fiji -eval \"close(\\"'+str(self.prefix.text())+'*\\");\"')
        
        if os.path.isfile(img):
            self.job.submitJobLocallyAndWait('rm '+img)  
        
        ## (6) after all checks completed, singleSliceFunc is called and we wait until image is done
        if self.afsaccount.isChecked():
            self.job.submitJobViaGateway(self.cmd+'\n','x02da-gw','x02da-cons-2')
        elif self.cons2.isChecked():
            self.job.submitJobLocally(self.cmd)
            
        for kk in range(10):
            if os.path.isfile(img):
                break
            else:
                sleep(0.5)
        else:
            self.displayErrorMessage('No reconstructed slice found', 'After waiting 5 sec the reconstructed slice was not found')
            return
                                    
        ## (7) we display the image
        if self.openinfiji.isChecked():
            self.job.submitJobLocally('fiji -eval \"open(\\"'+img+'\\")\"')
        else:
            self.displayImageBig(img)
 

    def createCommand(self):
        '''
        main method for creating the command line string. for consistency reasons the flags are
        defined in the registerAllParameters() method only (and only there!)
        '''
        if self.develbranchon.isChecked():
            self.cmd0 = "/afs/psi/project/TOMCAT_pipeline/Devel/tomcat_pipeline/src/prj2sinSGE.sh "
        else:
            self.cmd0 = "prj2sinSGE "
        self.cmds = []
        
        ## (1) First check whether we need to create CPR-s
        if self.cpron.isChecked():
            if not self.createCprAndFltpCmd('cpr',self.jobname_str):
                return False
        
        ## (2) Then we check whether we need FLTP-s
        if self.paganinon.isChecked():
            if not self.fltp_fromtif.isChecked() and not self.fltp_fromcpr.isChecked():
                self.displayErrorMessage('Missing fltp source', 'Please select whether fltp-s should be created from tif or cpr-s!')
                return False
            if not self.createCprAndFltpCmd('fltp',self.jobname_str):
                return False
            
        ## (3) Whether we need sinograms
        if self.sinon.isChecked():
            if not self.createSinCmd(self.jobname_str):
                return False
            
        ## (4) Whether we want reconstructions
        if self.reconstructon.isChecked():
            if not self.createRecoCmd(self.jobname_str):
                return False
        
        for cmd_tmp in self.cmds:
#             print '++ '+cmd_tmp
            self.cmd = self.cmd+cmd_tmp+';' 
        
        return True
            
    
    def createCprAndFltpCmd(self,mode,jobname):
        '''
        method for creating the cmd for creating cprs and/or fltps.
        it is basically very similar. only for the fltp command the Paganin
        parameters are added and a few flags changed
        TODO: rewrite IF-statements here because now it's really a mess
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
        
        ## only in CPR if set, else only in FLTP
        if mode == 'cpr' or self.fltp_fromtif.isChecked():
            optional = ['binsize', 'scaleimagefactor']
            cmd1 += '-f '+self.raws.text()
            cmd1 += ','+self.darks.text()
            cmd1 += ','+self.flats.text()
            cmd1 += ','+self.interflats.text()
            cmd1 += ','+self.flatfreq.text()+' '
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
            if self.cpron.isChecked():
                cmd1 += '--hold='+jobname+'_cpr '
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.cpr.DMP '
        
        cmd1 += '--jobname='+jobname+'_'+mode+' '
  
        ## only for Paganin phase retrieval
        if mode == 'fltp':
            cmd1 += ParameterWrap.CLA_dict['paganinon'].flag+' '
            for child in ParameterWrap.CLA_dict['paganinon'].child_list:
                cmd1 += getattr(self,child).text()+','
            cmd1 = cmd1[:-2]
            cmd1 = cmd1[:-len(str(getattr(self,child).text()))]+' '  # hack: delete last child
                
        ## only in CPR if cpr is set , else only in FLTP
        if mode == 'cpr' or not self.cpron.isChecked():
            if getattr(self,'preflatsonly').isChecked():
                cmd1 += ParameterWrap.CLA_dict['preflatsonly'].flag+' '
        
        cmd1 += '-g '+str(g_param)+' '
        
        ## TODO: include maybe above
        if mode == 'cpr' or self.fltp_fromtif.isChecked(): # or not self.cpron.isChecked():
            cmd1 += ParameterWrap.CLA_dict['inputtype'].flag+' '+ParameterWrap.getComboBoxContent('inputtype')+' '
        else:
            cmd1 += '-I 0 '
        
        ## define input and output dirs
        if mode == 'cpr':
            inputdir = os.path.join(str(self.inputdirectory.text()),'')
            outputdir = os.path.join(str(self.cprdirectory.text()),'')
        elif mode == 'fltp':# and not self.cpron.isChecked():
            if self.fltp_fromcpr.isChecked():
                inputdir = os.path.join(str(self.cprdirectory.text()),'')
            else:
                inputdir = os.path.join(str(self.inputdirectory.text()),'')
            outputdir = os.path.join(str(self.fltpdirectory.text()),'')
        else:
            inputdir = os.path.join(str(self.cprdirectory.text()),'')
            outputdir = os.path.join(str(self.fltpdirectory.text()),'')
        
        ## TODO: probably outsource whole snippet
        if self.afsaccount.isChecked():
            inputdir_mod = self.dirs.afsPath2Cons2(inputdir)
            outputdir_mod= self.dirs.afsPath2Cons2(outputdir)
            cmd1 += '-o '+outputdir_mod+' '
            cmd1 += inputdir_mod
        elif self.cons2.isChecked():
            cmd1 += '-o '+outputdir+' '
            cmd1 += inputdir

#         return cmd1
        self.cmds.append(cmd1)
        return True
    
    
    def createSinCmd(self,jobname):
        '''
        method for creating command line for sinograms
        '''
        if self.sin_fromtif.isChecked():
            standard = '-d -g 7 -I 1 '
            cmd1 = self.cmd0+standard
            cmd1 += '-f '+self.raws.text()
            cmd1 += ','+self.darks.text()
            cmd1 += ','+self.flats.text()
            cmd1 += ','+self.interflats.text()
            cmd1 += ','+self.flatfreq.text()+' '            
        else:
            standard = '-d -k 2 -g 0 -I 0 '
            cmd1 = self.cmd0+standard
            cmd1 += '-f '+self.raws.text()
            cmd1 += ',0,0,0,0 '
            
        if getattr(self,'preflatsonly').isChecked():
                cmd1 += ParameterWrap.CLA_dict['preflatsonly'].flag+' '
        
        if self.runringremoval.isChecked():  # the wavelet parameters are composed separately
            cmd1 += '-k 2 '
            cmd1 += self.setWavletParameters()
        else:
            cmd1 += '-k 1 '
        
        # TODO: use jobname in IO so that we don't need to hardcode
        if self.cpron.isChecked() and not self.paganinon.isChecked():
            cmd1 += '--hold='+jobname+'_cpr '
        elif self.paganinon.isChecked():
            cmd1 += '--hold='+jobname+'_fltp '
            
        cmd1 += '--jobname='+jobname+'_sin '
        
        if ParameterWrap.CLA_dict['steplines'].performCheck():
            cmd1 += ParameterWrap.CLA_dict['steplines'].flag+' '+getattr(self,'steplines').text()+' '
            
        if ParameterWrap.CLA_dict['stitchingtype'].performCheck():
            cmd1 += ParameterWrap.CLA_dict['stitchingtype'].flag+' '+ParameterWrap.getComboBoxContent('stitchingtype')+' '
        
        if self.sin_fromcpr.isChecked():
            inputdir = os.path.join(str(self.cprdirectory.text()),'')
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.cpr.DMP '
        elif self.sin_fromfltp.isChecked():
            inputdir = os.path.join(str(self.fltpdirectory.text()),'')
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.fltp.DMP '
        elif self.sin_fromtif.isChecked():
            inputdir = os.path.join(str(self.inputdirectory.text()),'')
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.tif '
        else:
            self.displayErrorMessage('No sinogram source defined', 'Check the radio box, from where to create sinograms')
            return
        
        # TODO: probably outsource like before
        if self.afsaccount.isChecked():
            inputdir_mod = self.dirs.afsPath2Cons2(inputdir)
            outputdir_mod= self.dirs.afsPath2Cons2(str(self.sinogramdirectory.text()))
            cmd1 += '-o '+outputdir_mod+' '
            cmd1 += inputdir_mod
        elif self.cons2.isChecked():
            cmd1 += '-o '+os.path.join(str(self.sinogramdirectory.text()),'')+' '
            cmd1 += inputdir
            
        self.cmds.append(cmd1)
        return True
    
    
    def createRecoCmd(self,jobname):
        '''
        method for creating command line string for reconstruction job
        '''
        ## Compose all mandatory
        if self.rec_fromtif.isChecked():
            inputdir = os.path.join(str(self.inputdirectory.text()),'')
            standard = '-d -R 0 -k 0 -I 1 -g 7 '
            standard += '-f '+self.raws.text()
            standard += ','+self.darks.text()
            standard += ','+self.flats.text()
            standard += ','+self.interflats.text()
            standard += ','+self.flatfreq.text()+' '
            if ParameterWrap.CLA_dict['stitchingtype'].performCheck():
                standard += ParameterWrap.CLA_dict['stitchingtype'].flag+' '+ParameterWrap.getComboBoxContent('stitchingtype')+' '
            if self.runringremoval.isChecked():  # the wavelet parameters are composed separately
                standard += self.setWavletParameters()
            standard += ParameterWrap.CLA_dict['prefix'].flag+' '+getattr(self,'prefix').text()+'####.tif '
        elif self.rec_fromsino.isChecked():
            inputdir = os.path.join(str(self.sinogramdirectory.text()),'')
            standard = '-d -k 1 -I 3 -R 0 -g 0 '
        else:
            self.displayErrorMessage('No reconstruction source defined', 'Check the radio box, from where to create reconstructions')
            return
            
        cmd1 = self.cmd0+standard

        optional = ['cutofffrequency','edgepadding','centerofrotation','rotationangle','tifmin','tifmax']
        for param in optional:
            if not getattr(self,param).text() == '':
                cmd1 += ParameterWrap.CLA_dict[param].flag+' '+getattr(self,param).text()+' '
        
        ## (4) Comboboxes with respective dictionaries (except wavelet comboboxes)
        comboboxes = ['filter', 'outputtype', 'geometry']
        for combo in comboboxes:
            if ParameterWrap.CLA_dict[combo].performCheck():
                cmd1 += ParameterWrap.CLA_dict[combo].flag+' '+ParameterWrap.getComboBoxContent(combo)+' ' 
                
        # TODO: use jobname in IO so that we don't need to hardcode
        if self.sinon.isChecked() and self.rec_fromsino.isChecked():
            cmd1 += '--hold='+jobname+'_sin '
            
        cmd1 += '--jobname='+jobname+'_reco '
        
        outputdir = os.path.join(str(self.recodirectory.text()),'')
        sinodir_tmp = self.dirs.getParentDir(inputdir)+'sino_tmp/'
        if self.afsaccount.isChecked():
            inputdir_mod = self.dirs.afsPath2Cons2(inputdir)
            outputdir_mod= self.dirs.afsPath2Cons2(outputdir)
            if self.rec_fromtif.isChecked():
                sinodir_tmp_mod = self.dirs.afsPath2Cons2(sinodir_tmp)
                cmd1 += '-o '+sinodir_tmp_mod+' '
            cmd1 += '-O '+outputdir_mod+' '
            cmd1 += inputdir_mod
        elif self.cons2.isChecked():
            if self.rec_fromtif.isChecked():
                cmd1 += '-o '+sinodir_tmp+' '
            cmd1 += '-O '+outputdir+' '
            cmd1 += inputdir
        
        self.cmds.append(cmd1)
        return True
        
        
    def checkComputingLocation(self):
        '''
        make sure the radiobox from where the computing takes place has been set
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
                self.displayErrorMessage('Fiji not found', 'fiji must be in PATH, e.g. installed in /urs/bin')
                return
            
            
    def saveConfigFile(self):
        '''
        method when pressing Menu item for loading config file
        '''
        savefile = QFileDialog.getSaveFileName(self,
                        'Select where the config file should be saved',self.lastdir)
        if not savefile:
            return
        file_obj = FileIO(savefile)
        file_obj.writeFile(self, ParameterWrap)
        self.lastdir = self.dirs.getParentDir(str(savefile))
        
        
    def loadConfigFile(self, loadfile = '', returnvalue = False, overwrite = True):
        '''
        method for loading config-file (from Menu item) or by giving absolute config-file path name
        (loadfile). if returnvalue is set True then the method returns the config-file object. If overwrite is
        False then empty fields from config-file are not overwriting GUI-fields
        '''
        if not loadfile:
            loadfile = QFileDialog.getOpenFileName(self,
                        'Select where the config file is located',self.lastdir)
        if not loadfile:
            return
        self.lastdir = self.dirs.getParentDir(str(loadfile))
        file_obj = FileIO(loadfile)
        file_obj.loadFile(self,ParameterWrap,overwrite)
        
        if returnvalue:
            return file_obj
        
        self.dirs.inputdir = self.inputdirectory.text()
        self.dirs.initSinDirectory()
        
        
    def loadTemplate(self, templatename):
        '''
        method for loading menu template for SGE-script. it's basically the same as loading a
        config file, only with additional color-highlighting
        '''
        template_file = self.dirs.glueOsPath([self.dirs.runningdir, 'templates' ,templatename+'.txt'])
        template_obj = self.loadConfigFile(template_file, True, False)
        
        ParameterWrap.resetAllStyleSheets()
        for param in template_obj.config.options(template_obj.heading):
            name_handle = getattr(self,param)
            name_handle.setStyleSheet("QLineEdit { border : 2px solid green;}")
    
    
    def getDirectory(self,mode):
        '''
        Dialog for setting a directory source with QFileDialog. First,
        we update "lastdir" property. After that, depending on the
        directory, the textfield are updated and initialized.
        '''
        dir_temp = QFileDialog.getExistingDirectory(self,
                            'Select direcory',self.lastdir)
        if not dir_temp:
            return

        self.lastdir = self.dirs.getParentDir(str(dir_temp))
        
        if mode == 'input_dir':
            self.inputdirectory.setText(dir_temp)
            self.dirs.initInputDirectory()
            return
        elif mode =='sinodir':
            self.sinogramdirectory.setText(dir_temp)
            self.dirs.sinodir = dir_temp
            self.dirs.initSinDirectory()
            return
        elif mode =='cprdirectory':
            self.dirs.cprdir = dir_temp
            self.cprdirectory.setText(self.dirs.cprdir)
            return
        elif mode =='fltpdir':
            self.dirs.fltpdir = dir_temp
            self.fltpdirectory.setText(self.dirs.fltpdir)
            return
        elif mode =='recodir':
            self.dirs.recodir = dir_temp
            self.recodirectory.setText(self.dirs.recodir)
            return
            
        
    def setWavletParameters(self):
        '''
        method for adding the wavelet correction to the command line string
        '''
        combos = ['wavelettype','waveletpaddingmode']
        textedit = ['waveletdecompositionlevel','sigmaingaussfilter']
        cmd = ''
        cmd += ParameterWrap.CLA_dict[combos[0]].flag+' '+str(getattr(self,combos[0]).currentText())+' '
        cmd += ParameterWrap.CLA_dict[textedit[0]].flag+' '+getattr(self,textedit[0]).text()+' '
        cmd += ParameterWrap.CLA_dict[textedit[1]].flag+' '+getattr(self,textedit[1]).text()+' '
        cmd += ParameterWrap.CLA_dict[combos[1]].flag+' '+ParameterWrap.getComboBoxContent(combos[1])+' '
        return cmd
        
        
    def setZingerParameters(self):
        '''
        method for adding zinger removal parameters
        '''
        self.cmd += '-z 1 '
        self.cmd += ParameterWrap.CLA_dict['zinger_thresh'].flag+' '+str(getattr(self,'zinger_thresh').text())+' '
        self.cmd += ParameterWrap.CLA_dict['zinger_width'].flag+' '+str(getattr(self,'zinger_width').text())+' '

        
    def displayErrorMessage(self,head,msg):
        '''
        method to display random error messages with QMessageBox
        '''
        QMessageBox.warning(self, head, msg)        

        
    def displayYesNoMessage(self,head,txt):
        '''
        show dialog with yes/no answer and defined text
        '''
        question = QMessageBox.warning(self, head, txt, QMessageBox.Yes, QMessageBox.No)
        
        if question == QMessageBox.Yes:
            return True
        else:
            return False 
        
        
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
        
        
    def debugTextField(self):
        '''
        prints the command line string into a textfield that can be edited and
        saves the (un)edited text string into the class property self.cmd to
        be submitted to the cluster
        '''
        debugwin = DebugCommand(self.parent)
        QTextEdit.insertPlainText(debugwin.textfield, self.cmd)
        if debugwin.exec_() == QDialog.Accepted:
            tmp_string = str(QTextEdit.toPlainText(debugwin.textfield)).strip()
            self.cmd = ' '.join(tmp_string.split())
            print self.cmd
            return True
        else:
            return False
        
        
    def changeOutputType(self):
        '''
        method for appending correct reco-output directory name when changing
        output type
        '''
        ind = str(self.outputtype.currentIndex())
        if ind == '0':
            newname = 'rec_8bit'
        elif ind == '1':
            newname = 'rec_DMP'
        elif ind ==  '2':
            newname = 'rec_DMP_HF5'
        elif ind ==  '3':
            newname = 'rec_16bit'
        elif ind ==  '4':
            newname = 'rec_8bit'
        else:
            newname = 'unknown_output'
        
        outputpaths = self.dirs.splitOsPath(str(self.recodirectory.text()))
        newpathlist = outputpaths[:-1]+[newname]
        pathstr = self.dirs.glueOsPath(newpathlist)
        self.recodirectory.setText(pathstr)
        
        
    def submitAndSingleSliceContextMenu(self,point):
        '''
        Context menu for submit and SingleSlice buttons. When right-
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
        Sets the "target" property according "target" input and labels
        the GUI buttons accordingly.
        '''
        self.target = target
        self.submit.setText("Submit "+"("+target+")")
        self.singleslice.setText("Single slice "+"("+target+")")
            

class DebugCommand(QDialog):
    '''
    window for displaying and changing debug command
    '''
    def __init__(self,parent):
        QDialog.__init__(self)
        self.heading = QLabel()
        self.heading.setObjectName("head")
        self.heading.setText(QApplication.translate("Debug command", "Command to be submitted to", None, QApplication.UnicodeUTF8))
        self.buttonsubmit = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.textfield = QTextEdit(self)
        self.buttonsubmit.accepted.connect(self.accept)
        self.buttonsubmit.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.textfield)
        layout.addWidget(self.buttonsubmit)
        self.resize(600, 300)
        


if __name__ == "__main__":
    mainapp = QApplication(sys.argv,True)  # create Qt application
    win = MainWindow()  # create main window
    win.show()
 
    # Connect signals for mainapp
    mainapp.connect(mainapp, SIGNAL("lastWindowClosed()"), mainapp, SLOT("quit()"))
    mainapp.connect(win.exitapp, SIGNAL("triggered()"), mainapp, SLOT("quit()"))
 
    # Start up mainapp
    sys.exit(mainapp.exec_())