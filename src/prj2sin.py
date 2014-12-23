from arguments import ParameterWrap


class Prj2sinWrap(object):
    '''
    The "Prj2sinWrap" class is used for creating the full command line
    string (CLS) given that all necessary GUI-fields were provided.
    Thus it should potentially be considered as a kind of API for the
    TOMCAT processing and reconstruction pipeline and is supposed to
    be the only place where eventual future changes in the TOMCAT
    pipeline should be propagated.
    '''
    sgepath = 'prj2sinSGE '
    sgepathdevel = '/afs/psi/project/TOMCAT_pipeline/Devel/tomcat_pipeline/bin/prj2sinSGE.sh '
    singleSlice = '/usr/bin/python /afs/psi.ch/project/tomcatsvn/' \
        'executeables/grecoman/externals/singleSliceFunc.py '

    @classmethod
    def createCommand(cls, parent):
        '''
        This is the main method for creating the command line string
        (CLS) which dependent on the checked "actions" in the GUI calls
        and other methods like "createCprAndFltpCmd", "createSinCmd"
        etc. We have three different properties in use: (i) cls.cmd is
        the full CLS to be submitted to the cluster (ii) cls.cmds is a
        list of separate cluster commands and (ii) cls.cmd0 is the
        cluster command for executing a single action.
        '''
        cls.cmd = ''
        cls.cmds = []

        if parent.develbranchon.isChecked():
            cls.cmd0 = cls.sgepathdevel
        else:
            cls.cmd0 = cls.sgepath

        # (1) We check whether we need to create CPR-s.
        if parent.cpron.isChecked():
            cls.createCprAndFltpCmd('cpr', parent)

        # (2) Then we check whether we need FLTP-s.
        if parent.paganinon.isChecked():
            if (
               not parent.fltp_fromtif.isChecked()
               and not parent.fltp_fromcpr.isChecked()
               ):
                parent.displayErrorMessage('Missing fltp source',
                    'Please select whether fltp-s should be created from tif or cpr-s!')
                return False
            cls.createCprAndFltpCmd('fltp', parent)

        # (3) After that we check whether we need sinograms.
        if parent.sinon.isChecked():
            if (
               not parent.sin_fromtif.isChecked()
               and not parent.sin_fromfltp.isChecked()
               and not parent.sin_fromtif.isChecked()
               ):
                parent.displayErrorMessage('No sinogram source defined',
                    'Check the radio box, from where to create sinograms!')
                return False
            cls.createSinCmd(parent)

        # # (4) Finally we check whether reconstructions will be created.
        if parent.reconstructon.isChecked():
            if (
               not parent.rec_fromtif.isChecked()
               and not parent.rec_fromsino.isChecked()
               and not parent.rec_fromfltp.isChecked()
               ):
                parent.displayErrorMessage('No reconstruction source defined',
                    'Check the radio box, from where to create reconstructions')
                return False
            if ParameterWrap.getComboBoxContent('geometry') == '0':
                angfile = parent.dirs.glueOsPath([parent.dirs.inputdir, 'angles.txt'])
                if not parent.dirs.checkIfFileExist(angfile):
                    parent.displayErrorMessage('Missing angles file',
                    'The file "angles.txt" is missing in the tif directory.')
                return False
            cls.createRecoCmd(parent)

        for cmd_tmp in cls.cmds:  # compose the full CLS
            cls.cmd = cls.cmd + cmd_tmp + ';'

        return True

    @classmethod
    def createCprAndFltpCmd(cls, mode, parent):
        '''
        This method is used to compose both, the command line string
        (CLS) for creating cprs and/or for creating fltps (since they
        are both very similar). Understanding the following code is not
        expected, as it requires also the understanding of the
        reconstruction pipeline.
        '''
        # # Compose all mandatory
        standard = '-d -C '
        cmd1 = cls.cmd0 + standard

        if parent.cpron.isChecked() and not parent.paganinon.isChecked():
            if parent.withlog.isChecked():
                g_param = 7
            else:
                g_param = 3
        elif parent.fltp_fromcpr.isChecked() and mode == 'fltp':
            g_param = 0
        elif parent.fltp_fromtif.isChecked() and mode == 'fltp':
            g_param = 3
        else:  # case for mode == 'cpr'
            g_param = 3

        # only if CPR if set, else only in FLTP
        if mode == 'cpr' or parent.fltp_fromtif.isChecked():
            optional = ['binsize', 'scaleimagefactor']
            cmd1 += '-f ' + parent.raws.text()
            cmd1 += ',' + parent.darks.text()
            cmd1 += ',' + parent.flats.text()
            cmd1 += ',' + parent.interflats.text()
            cmd1 += ',' + parent.flatfreq.text() + ' '
            cmd1 += ParameterWrap.CLA_dict['inputtype'].flag + ' ' + \
                ParameterWrap.getComboBoxContent('inputtype') + ' '
            for param in optional:
                if not getattr(parent, param).text() == '':
                    cmd1 += ParameterWrap.CLA_dict[param].flag + ' ' + \
                        getattr(parent, param).text() + ' '

            # Region of interest optional
            if getattr(parent, 'roion').isChecked():
                cmd1 += ParameterWrap.CLA_dict['roion'].flag + ' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    cmd1 += getattr(parent, child).text() + ','
                cmd1 = cmd1[:-1] + ' '
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.tif '
        else:
            cmd1 += '-f ' + parent.raws.text()
            cmd1 += ',0,0,0,0 '
            cmd1 += '-I 0 '
            if parent.cpron.isChecked():
                cmd1 += '--hold=' + parent.jobname_str + '_cpr '
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.cpr.DMP '

        cmd1 += '--jobname=' + parent.jobname_str + '_' + mode + ' '

        # optional job priority
        if not getattr(parent, 'jobpriority').currentIndex() == 0:
            cmd1 += ParameterWrap.CLA_dict['jobpriority'].flag + '='
            cmd1 += ParameterWrap.getComboBoxContent('jobpriority') + ' '

        # probably increases job priority on Merlin (?!)
        if parent.target == 'Merlin':
            cmd1 += '--queue=prime_ti.q --ncores=16 '
        else:
            cmd1 += ParameterWrap.CLA_dict['queue'].flag + '=' + \
                ParameterWrap.getComboBoxContent('queue') + ' '

        # only for Paganin phase retrieval
        if mode == 'fltp':
            cmd1 += ParameterWrap.CLA_dict['paganinon'].flag + ' '
            for child in ParameterWrap.CLA_dict['paganinon'].child_list[:-1]:
                cmd1 += getattr(parent, child).text() + ','
            cmd1 = cmd1[:-1] + ' '

        # only in CPR if cpr is set , else only in FLTP
        if mode == 'cpr' or not parent.cpron.isChecked():
            if getattr(parent, 'preflatsonly').isChecked():
                cmd1 += ParameterWrap.CLA_dict['preflatsonly'].flag + ' '

        cmd1 += '-g ' + str(g_param) + ' '

        # # define input and output dirs
        if mode == 'cpr':
            inputdir = parent.inputdirectory.text()
            outputdir = parent.cprdirectory.text()
        elif mode == 'fltp':
            if parent.fltp_fromcpr.isChecked():
                inputdir = parent.cprdirectory.text()
            else:
                inputdir = parent.inputdirectory.text()
            outputdir = parent.fltpdirectory.text()
        else:
            inputdir = parent.cprdirectory.text()
            outputdir = parent.fltpdirectory.text()

        cmd1 += '-o ' + parent.dirs.rewriteDirectoryPath(outputdir, 'forward') + ' '
        cmd1 += parent.dirs.rewriteDirectoryPath(inputdir, 'forward')

        cls.cmds.append(cmd1)

    @classmethod
    def createSinCmd(cls, parent):
        '''
        This method is used to compose the command line string (CLS)
        for creating sinograms. Again, understanding the following code
        is not expected, as it requires also the understanding of the
        reconstruction pipeline.
        '''
        if parent.sin_fromtif.isChecked():
            standard = '-d -g 7 -I 1 '
            cmd1 = cls.cmd0 + standard
            cmd1 += '-f ' + parent.raws.text()
            cmd1 += ',' + parent.darks.text()
            cmd1 += ',' + parent.flats.text()
            cmd1 += ',' + parent.interflats.text()
            cmd1 += ',' + parent.flatfreq.text() + ' '
            if getattr(parent, 'roion').isChecked():
                cmd1 += ParameterWrap.CLA_dict['roion'].flag + ' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    cmd1 += getattr(parent, child).text() + ','
                cmd1 = cmd1[:-1] + ' '
        else:
            standard = '-d -g 0 -I 0 '
            cmd1 = cls.cmd0 + standard
            cmd1 += '-f ' + parent.raws.text()
            cmd1 += ',0,0,0,0 '

        for param in ['preflatsonly', 'shiftcorrection']:
            if getattr(parent, param).isChecked():
                    cmd1 += ParameterWrap.CLA_dict[param].flag + ' '

        if (
           parent.runringremoval.isChecked()
           and ParameterWrap.getComboBoxContent('waveletfilterdest') is 'filter_sin'
           ):  # wavelet parameters
            cmd1 += '-k 2 '
            cmd1 += cls.setWavletParameters(parent)
        else:
            cmd1 += '-k 1 '

        # set correct jobname in order to wait for other jobs to finish
        if parent.cpron.isChecked() and not parent.paganinon.isChecked():
            cmd1 += '--hold=' + parent.jobname_str + '_cpr '
        elif parent.paganinon.isChecked():
            cmd1 += '--hold=' + parent.jobname_str + '_fltp '

        cmd1 += '--jobname=' + parent.jobname_str + '_sin '

        # optional job priority
        if not getattr(parent, 'jobpriority').currentIndex() == 0:
            cmd1 += ParameterWrap.CLA_dict['jobpriority'].flag + '='
            cmd1 += ParameterWrap.getComboBoxContent('jobpriority') + ' '

        # probably increases job priority on Merlin (?!)
        if parent.target == 'Merlin':
            cmd1 += '--queue=prime_ti.q --ncores=16 '
        else:
            cmd1 += ParameterWrap.CLA_dict['queue'].flag + '=' + \
                ParameterWrap.getComboBoxContent('queue') + ' '

        if ParameterWrap.CLA_dict['steplines'].performCheck():
            cmd1 += ParameterWrap.CLA_dict['steplines'].flag + ' ' + \
                getattr(parent, 'steplines').text() + ' '

        if ParameterWrap.CLA_dict['stitchingtype'].performCheck():
            cmd1 += ParameterWrap.CLA_dict['stitchingtype'].flag + ' ' + \
                ParameterWrap.getComboBoxContent('stitchingtype') + ' '

        if parent.sin_fromcpr.isChecked():
            inputdir = parent.cprdirectory.text()
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.cpr.DMP '
        elif parent.sin_fromfltp.isChecked():
            inputdir = parent.fltpdirectory.text()
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.fltp.DMP '
        elif parent.sin_fromtif.isChecked():
            inputdir = parent.inputdirectory.text()
            cmd1 += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.tif '

        cmd1 += '-o ' + parent.dirs.rewriteDirectoryPath(parent.sindirectory.text(), 'forward') + ' '
        cmd1 += parent.dirs.rewriteDirectoryPath(inputdir, 'forward')

        cls.cmds.append(cmd1)

    @classmethod
    def createRecoCmd(cls, parent):
        '''
        This method is used to compose the command line string (CLS)
        for creating tomographic reconstructions. Again, understanding
        the following code is not expected, as it requires also the
        understanding of the reconstruction pipeline.
        '''
        # # Compose all mandatory
        if parent.rec_fromtif.isChecked():
            inputdir = parent.inputdirectory.text()
            standard = '-d -R 0 -k 0 -I 1 -g 7 '
            standard += '-f ' + parent.raws.text()
            standard += ',' + parent.darks.text()
            standard += ',' + parent.flats.text()
            standard += ',' + parent.interflats.text()
            standard += ',' + parent.flatfreq.text() + ' '
            if ParameterWrap.CLA_dict['stitchingtype'].performCheck():
                standard += ParameterWrap.CLA_dict['stitchingtype'].flag + \
                    ' ' + ParameterWrap.getComboBoxContent('stitchingtype') + ' '
            if getattr(parent, 'roion').isChecked():
                standard += ParameterWrap.CLA_dict['roion'].flag + ' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    standard += getattr(parent, child).text() + ','
                standard = standard[:-1] + ' '
            standard += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.tif '
        elif parent.rec_fromsino.isChecked():
            inputdir = parent.sindirectory.text()
            standard = '-d -I 3 -R 0 -g 0 '
            if (
               parent.runringremoval.isChecked()
               and ParameterWrap.getComboBoxContent('waveletfilterdest') is 'filter_reco'
               ):
                standard += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                    getattr(parent, 'prefix').text() + ' '
                standard += '-k 0 '
            else:
                standard += '-k 1 '
        elif parent.rec_fromfltp.isChecked():
            inputdir = parent.fltpdirectory.text()
            standard = '-d -k 0 -I 0 -R 0 -g 0 '
            standard += '-f ' + parent.raws.text()
            standard += ',0,0,0,0 '
            if getattr(parent, 'roion').isChecked():
                standard += ParameterWrap.CLA_dict['roion'].flag + ' '
                for child in ParameterWrap.CLA_dict['roion'].child_list:
                    standard += getattr(parent, child).text() + ','
                standard = standard[:-1] + ' '
            standard += ParameterWrap.CLA_dict['prefix'].flag + ' ' + \
                getattr(parent, 'prefix').text() + '####.fltp.DMP '

        if (
           parent.runringremoval.isChecked()
           and ParameterWrap.getComboBoxContent('waveletfilterdest') is 'filter_reco'
           ):  # wavelet parameters
            standard += cls.setWavletParameters(parent)

        cmd1 = cls.cmd0 + standard

        optional = ['cutofffrequency', 'edgepadding', 'centerofrotation',
                    'rotationangle', 'tifmin', 'tifmax']
        for param in optional:
            if not getattr(parent, param).text() == '':
                cmd1 += ParameterWrap.CLA_dict[param].flag + ' ' + getattr(parent, param).text() + ' '

        # # (4) Comboboxes with respective dictionaries (except wavelet)
        comboboxes = ['filter', 'outputtype', 'geometry']
        for combo in comboboxes:
            if ParameterWrap.CLA_dict[combo].performCheck():
                cmd1 += ParameterWrap.CLA_dict[combo].flag + ' ' + \
                    ParameterWrap.getComboBoxContent(combo) + ' '

        # # (5) Standard ring removal parameters
        if parent.runringremovalstd.isChecked():
            cmd1 += cls.setStandardRingRemoval(parent)

        # # (6) Zinger removal
        if parent.zingeron.isChecked() and parent.zingermode.currentIndex() == 0:
            cmd1 += cls.setZingerParameters(parent)

        # set correct jobname in order to wait for other jobs to finish
        if parent.sinon.isChecked() and parent.rec_fromsino.isChecked():
            cmd1 += '--hold=' + parent.jobname_str + '_sin '
        elif parent.paganinon.isChecked() and parent.rec_fromfltp.isChecked():
            cmd1 += '--hold=' + parent.jobname_str + '_fltp '

        cmd1 += '--jobname=' + parent.jobname_str + '_reco '

        # optional job priority
        if not getattr(parent, 'jobpriority').currentIndex() == 0:
            cmd1 += ParameterWrap.CLA_dict['jobpriority'].flag + '='
            cmd1 += ParameterWrap.getComboBoxContent('jobpriority') + ' '

        # probably increases job priority on Merlin (?!)
        if parent.target == 'Merlin':
            cmd1 += '--queue=prime_ti.q --ncores=16 '
        else:
            cmd1 += ParameterWrap.CLA_dict['queue'].flag + '=' + \
                ParameterWrap.getComboBoxContent('queue') + ' '

        outputdir = parent.recodirectory.text()
        sinodir_tmp = parent.dirs.getParentDir(inputdir)
        sinodir_tmp = parent.dirs.glueOsPath([sinodir_tmp, 'sino_tmp'])

        if (
           parent.runringremoval.isChecked()
           and ParameterWrap.getComboBoxContent('waveletfilterdest') is 'filter_reco'
           or parent.rec_fromtif.isChecked()
           or parent.rec_fromfltp.isChecked()
           ):
            cmd1 += '-o ' + parent.dirs.rewriteDirectoryPath(sinodir_tmp, 'forward') + ' '
        cmd1 += '-O ' + parent.dirs.rewriteDirectoryPath(outputdir, 'forward') + ' '
        cmd1 += parent.dirs.rewriteDirectoryPath(inputdir, 'forward')

        cls.cmds.append(cmd1)

    @classmethod
    def createSingleSliceCommand(cls, parent):
        '''
        This method is launched when pressing "Single Slice" button
        from the GUI. It's similar to "submitToCluster", however, it
        doesn't utilize the "createCommand" method. Instead, it creates
        the command line string (CLS) itself and in the end displays
        the image.
        '''
        if not str(parent.sinograms.currentText()):
            parent.displayErrorMessage('No sinogram selected',
                'Select the Sinogram directory and press Enter. '
                'Then select one to be reconstructed.')
            return

        if ParameterWrap.getComboBoxContent('geometry') == '0':
            angfile = parent.dirs.glueOsPath([parent.sindirectory.text(), 'angles.txt'])
            if not parent.dirs.checkIfFileExist(angfile):
                parent.displayErrorMessage('Missing angles file',
                    'The file "angles.txt" is missing in the sin directory.')
                return

        if not parent.checkComputingLocation():  # self-explaining
            return

        # create the command line string for single slice reconstruction
        cls.cmd = cls.singleSlice

        combos_single = ['filter', 'geometry']
        for combo in combos_single:
            if ParameterWrap.CLA_dict[combo].performCheck():
                cls.cmd += ParameterWrap.CLA_dict[combo].flag + ' ' + \
                    ParameterWrap.getComboBoxContent(combo) + ' '

        if parent.zingeron.isChecked():
            cls.cmd += cls.setZingerParameters(parent)

        optional_single = ['cutofffrequency', 'edgepadding', 'centerofrotation', 'rotationangle']

        for param in optional_single:
            if not getattr(parent, param).text() == '':
                cls.cmd += ParameterWrap.CLA_dict[param].flag + ' ' + \
                    getattr(parent, param).text() + ' '

        if parent.runringremoval.isChecked():  # the wavelet parameters are composed separately
            cls.cmd += cls.setWavletParameters(parent)

        if parent.runringremovalstd.isChecked():
            cls.cmd += cls.setStandardRingRemoval()

        # rewrite the sinogram-directory for use at the appropriate machine
        single_sino = parent.dirs.rewriteDirectoryPath(parent.sindirectory.text(), 'forward')

        cls.cmd += '-x ' + parent.target + ' '
        cls.cmd += '--Di ' + single_sino + ' -i ' + parent.sinograms.currentText()

    @classmethod
    def setWavletParameters(cls, parent):
        '''
        Method for adding the wavelet correction to the command line
        string.
        '''
        combos = ['wavelettype', 'waveletpaddingmode']
        textedit = ['waveletdecompositionlevel', 'sigmaingaussfilter']
        cmd = ParameterWrap.CLA_dict[combos[0]].flag + ' ' + \
            str(getattr(parent, combos[0]).currentText()) + ' '
        cmd += ParameterWrap.CLA_dict[textedit[0]].flag + ' ' + \
            getattr(parent, textedit[0]).text() + ' '
        cmd += ParameterWrap.CLA_dict[textedit[1]].flag + ' ' + \
            getattr(parent, textedit[1]).text() + ' '
        cmd += ParameterWrap.CLA_dict[combos[1]].flag + ' ' + \
            ParameterWrap.getComboBoxContent(combos[1]) + ' '
        return cmd

    @classmethod
    def setStandardRingRemoval(cls, parent):
        ''' Method for setting the standard ring removal parameters '''
        cmd = ParameterWrap.CLA_dict['ring_std_mode'].flag + ' ' + \
            ParameterWrap.getComboBoxContent('ring_std_mode') + ' '
        cmd += ParameterWrap.CLA_dict['ring_std_diff'].flag + ' ' + \
            getattr(parent, 'ring_std_diff').text() + ' '
        cmd += ParameterWrap.CLA_dict['ring_std_ringwidth'].flag + ' ' + \
            getattr(parent, 'ring_std_ringwidth').text() + ' '
        return cmd

    @classmethod
    def setZingerParameters(cls, parent):
        ''' Method for adding zinger removal parameters '''
        cmd = '-z s '  # # TODO: has to be fixed after 2D version is implemented
        cmd += ParameterWrap.CLA_dict['zinger_thresh'].flag + ' ' + \
            str(getattr(parent, 'zinger_thresh').text()) + ' '
        cmd += ParameterWrap.CLA_dict['zinger_width'].flag + ' ' + \
            str(getattr(parent, 'zinger_width').text()) + ' '
        return cmd
