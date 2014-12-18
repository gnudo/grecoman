import subprocess
from multiprocessing import Process, Queue
from ui_dialogs import Login
import os.path
import hashlib


class Connector(object):
    '''
    The connector class covers all activities for establishing a SSH
    connection to the TOMCAT cluster (login, credentials check), as
    well as all methods associated with communicating shell commands
    with certain machines. Moreover, it should be the only place where
    certain commands are executed (by using subprocess etc.).
    '''
    def __init__(self, parent):
        self.parent = parent
        self.afsuser = []
        self.eaccountuser = []
        self.merlinuser = []
        self.afspw = []
        self.eaccountpw = []
        self.cmds_cache = [None] * 5


    def performInitalCheck(self):
        '''
        This method makes sure that the correct account credentials are
        saved in the respective properties and if not, it launches the
        "inputCredentials" method to get them via GUI-dialogs.
        '''
        # (0) if we are on cons-2 we don't need any credentials
        if self.parent.cons2.isChecked():
            return True

        # (1) if the Target is 'Merlin'
        if self.parent.target == 'Merlin':
            if not self.merlinuser:
                self.inputCredentials('Merlin')
            return True

        # (2) We check whether we have AFS-credentials and if not whether
        # we obtain them
        if not self.afsuser or not self.afspw:
            if not self.inputCredentials('AFS'):
                return False

        # (3) We check for e-account number and password
        if not self.eaccountuser or not self.eaccountpw:
            if not self.inputCredentials('E-ACCOUNT'):
                return False
        return True


    def checkIdenticalJobs(self, cmd):
        '''
        This method checks whether an identical job has been submitted
        during the last 5 job submissions and if yes, it returns True.
        '''
        md5_str = hashlib.md5(cmd).hexdigest()[0:10]
        for item in self.cmds_cache:
            if item == md5_str:
                return True

        self.cmds_cache.pop(0)
        self.cmds_cache.append(md5_str)


    def submitJob(self, cmd):
        '''
        This method determines where (on which machine) to submit the
        reconstruction job and calls the appropriate method.
        '''
        if not self.performInitalCheck():  # check account credentials
            return
       
        if self.checkIdenticalJobs(cmd):
            if not self.parent.displayYesNoMessage('Identical Job','You have' \
                    ' submitted an identical job just before. Are you' \
                    ' sure you want to submit it again?'):
                self.parent.statusBar().clearMessage()
                return

        if self.parent.afsaccount.isChecked():
            if self.parent.target == 'x02da':
                self.submitJobViaGateway(cmd + '\n', 'x02da-gw',
                                         'x02da-cons-2')
            elif self.parent.target == 'Merlin':
                self.submitJobViaSshPublicKey(cmd + '\n', 'merlinc60')
        elif self.parent.cons2.isChecked():
            self.submitJobLocally(cmd)
        
        return True


    def submitJobLocally(self, cmd):
        ''' Submits a command to the local shell (bash) '''
        proc = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, shell=True)
        proc.stdin.write(cmd + '\n')


    def submitJobLocallyAndWait(self, cmd):
        ''' Submits a command to the local shell and waits till executed '''
        proc = subprocess.Popen(cmd, shell=True)
        proc.communicate()


    def submitJobViaSshPublicKey(self, cmd_str, target):
        '''
        Submits a job via SSH when public key auth has been set up
        properly.
        '''
        sshProcess = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, shell=True)
        sshProcess.stdin.write('ssh ' + self.merlinuser + '@' + target + '\n')
        sshProcess.stdin.write('whoami\n')
        sshProcess.stdout.readline()
        sshProcess.stdin.write(cmd_str)
        sshProcess.stdout.readline()


    def submitJobViaGateway(self, cmd_str, gw, target):
        '''
        Submits the job via a gateway, assuming AFS-credentials for
        logging into the gateway and e-account credentials for the
        target computer. When running the method we must be sure, that
        all credentials are correct otherwise the whole application
        will hang forever.
        
        Background: This method represents quite a "hack" as it is
        currently impossible to have public-key authentication on
        AFS-machines as well as it is impossible to establish direct
        connections to beamline computers from within PSI.
        Furthermore, it is quite tricky to set up SSH not to ask for
        a PW or to read it from STDIN because it always calls
        "gnome-ssh-askpass" to provide a password which is a GUI-dialog
        that we wanted to avoid in this case! Likewise there are
        several SSH libraries, that could be used instead, but apparently
        all have some pros/cons and bugs and don't seem suited to the
        PSI IT infrastructure at the moment. For this reason use Python's
        subprocess with the following procedure:
        (1) we create temporary files with PW for x02da-gw and cons-2 and
        (2) reset SSH_ASKPASS variable to get the password out of this
        file.
        '''

        ## (1) first we create files with passwords
        kk = 1
        afshome = '/afs/psi.ch/user/' + self.afsuser[0] + '/' + self.afsuser
        for ii in [self.afspw, self.eaccountpw]:
            pw = 'echo \\\"' + ii + '\\\"'
            p1 = subprocess.call(['echo "#!/bin/bash\n" > ' + afshome + \
                '/pw' + str(kk) + '.sh'], shell=True)
            p2 = subprocess.call(['echo ' + pw + ' >> ' + afshome + '/pw' + \
                str(kk) + '.sh'], shell=True)
            p3 = subprocess.call(['chmod a+x ' + afshome + '/pw' + str(kk) + \
                '.sh'], shell=True)
            kk = kk + 1

        ## (2) establish the connection to gateway
        sshProcess = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, shell=True)

        # TODO: substitute below lines so that we don't save cleartext pw-files
        # >> didn't work for eaccount
        # sshProcess.stdin.write('export SSH_ASKPASS=~/returnpass.sh\n')
        # sshProcess.stdin.write('echo \\\"' + self.afspw + '\\\"|ssh ' + \
            # self.afsuser + '@' + x02dagw + '\n')
        sshProcess.stdin.write('export SSH_ASKPASS=' + afshome + '/pw1.sh\n')
        sshProcess.stdin.write('export DISPLAY=dummydisplay:0\n')
        sshProcess.stdin.write('ssh -o \"GSSAPIAuthentication no\" ' + \
            self.afsuser + '@' + gw + '\n')
        sshProcess.stdin.write('echo $SSH_ASKPASS\n')
        sshProcess.stdout.readline()

        # (3) from gateway connect to target
        sshProcess.stdin.write('export SSH_ASKPASS=' + afshome + '/pw2.sh\n')
        sshProcess.stdin.write('export DISPLAY=dummydisplay:0\n')
        sshProcess.stdin.write('echo $SSH_ASKPASS\n')
        sshProcess.stdout.readline()
        sshProcess.stdin.write('ssh -o \"GSSAPIAuthentication no\" ' + \
            self.eaccountuser + '@' + target + '\n')
        sshProcess.stdin.write('echo $SSH_ASKPASS\n')
        sshProcess.stdout.readline()

        # (4) now we first delete the password files (before continuing)
        p = subprocess.call(['rm ' + afshome + '/pw1.sh'], shell=True)
        p = subprocess.call(['rm ' + afshome + '/pw2.sh'], shell=True)

        # (5) submit the command line string from the GUI on target
        sshProcess.stdin.write(cmd_str)
        sshProcess.stdout.readline()  # hangs if "cmd_str" doesn't return value


    def inputCredentials(self, mode):
        '''
        This method is used for reading AFS and e-account credentials
        from the GUI-fields of the GUI-dialog, and running respective
        methods to check whether those are correct.
        '''
        logwin = Login(self.parent, mode)
        if logwin.exec_() == Login.Accepted:
            if mode == 'AFS':
                self.afsuser = str(logwin.username.text())
                self.afspw = str(logwin.password.text())
                if not self.checkAfsCredentials():  # Check AFS-credentials
                    self.afsuser = []
                    self.afspw = []
                    return False
            elif mode == 'E-ACCOUNT':
                self.eaccountuser = str(logwin.username.text())
                self.eaccountpw = str(logwin.password.text())
                if not self.blMountEaccount():  # Check EACCOUNT-credentials
                    self.eaccountuser = []
                    self.afspw = []
                    return False
            elif mode == 'Merlin':
                self.merlinuser = str(logwin.username.text())
            return True
        return False


    def blMountEaccount(self):
        '''
        Mounts the e-account on an AFS-machine with the "blmount"
        command and returns True if it was mounted successfully.
        '''
        mountdir = self.parent.dirs.homedir + '/slsbl/x02da/' + \
            self.eaccountuser
        p1 = subprocess.check_call(['blumount -d ' + mountdir], shell=True)
        p1 = subprocess.check_call(['blmount -a ' + self.eaccountuser + \
            ' -s x02da -p ' + self.eaccountpw], shell=True)

        if not os.listdir(mountdir):
            return False
        else:
            return True


    def checkAfsCredentials(self):
        '''
        This is again a preliminary "hack" method for checking whether
        the AFS-credentials are correct. We simply connect to an
        AFS-machine at PSI and check whether we manage to do so.
        TODO: Obviously any simpler solution is more than welcome...
        '''
        if not self.afsuser or not self.afspw:
            self.parent.displayErrorMessage('Missing',
                'No blank fields for AFS-credentials allowed')
            return

        comp = 'llc1'
        pw = 'echo \\\"' + self.afspw + '\\\"'
        p1 = subprocess.Popen(['echo "#!/bin/bash\n" > ~/pw.sh'], shell=True)
        p2 = subprocess.Popen(['echo ' + pw + ' >> ~/pw.sh'], shell=True)
        p3 = subprocess.Popen(['chmod a+x ~/pw.sh'], shell=True)

        queue1 = Queue()
        p = Process(target=self.checkAfsCredentialsHelper, args=(comp, queue1))
        p.start()
        p.join(2)
        try:
            # we try to get the queue >> will throw an error after timeout
            if queue1.get():
                subprocess.call(['rm ~/pw.sh'], shell=True)
                return True
        except IOError as e:
            subprocess.call(['rm ~/pw.sh'], shell=True)
            p.terminate()
            self.parent.displayErrorMessage('Error',
                'Wrong AFS Password/Username!')
            return False
        except ValueError:
            print "value error"
            return False


    def checkAfsCredentialsHelper(self, comp, queue1):  # ,comp):
        '''
        Helper method for checkAfsCredentials in order to enable
        timeout of operation.
        '''
        p = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, shell=True)
        p.stdin.write('export SSH_ASKPASS=~/pw.sh\n')
        p.stdin.write('ssh -o \"GSSAPIAuthentication no\" ' + self.afsuser + \
            '@' + comp + '\n')
        p.stdin.write('echo $HOSTNAME\n')
        host = p.stdout.readline()  # this method hangs if password is wrong!
        if str(host[:len(comp)]) == str(comp):
            queue1.put(True)


    def isInstalled(self, application):
        '''
        Checks whether an application is installed on the system and
        returns True or False
        '''
        p = subprocess.call('which ' + application, shell=True)
        if p == 0:
            return True
        else:
            return False
