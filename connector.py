import subprocess
from multiprocessing import Process, Queue
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os.path


class Connector(object):
    '''
    connector class used to establish SSH connection either to cons-2 or MERLIN form an AFS
    account or from home. in such cases directory paths have to be modified depending on from
    which machine one is accessing
    '''
    def __init__(self,parent):
        self.parent = parent
        self.afsuser = []
        self.eaccountuser = []
        self.afspw = []
        self.eaccountpw = []
        
    
    def performInitalCheck(self):
        '''
        method for checking both AFS and EACCOUNT credentials
        '''
        # (0) if we are on cons-2 we don't need any credentials (at least for now)
        if self.parent.cons2.isChecked():
            return True 
        
        # (1) first we check whether we have AFS-credentials AND whether we actually get them
        if not self.afsuser or not self.afspw:
            if not self.inputCredentials('AFS'):
                return False
            
        # (2) ... whether we have eaccount number and password
        if not self.eaccountuser or not self.eaccountpw:
            if not self.inputCredentials('E-ACCOUNT'):
                return False
        return True
    
    
    def submitJobLocally(self,cmd):
        '''
        method to run a job locally on cons-2
        TODO: probably this one will be united with a more generic submitJob() method (to be
        compatible also with Merlin)
        '''
        proc = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,shell=True)
        proc.stdin.write(cmd+'\n')
        #subprocess.check_call(cmd,shell=True,executable='/bin/bash')
        
        
    def submitJobViaGateway(self,cmd_str,gw,target):
        '''
        method to submit the job with via a gateway. we assume AFS credentials for the gateway
        and eaccount credentials for the target when running this method, we must already be sure
        the the AFS and eaccount credentials are orrect - otherwise it will hang forever...
        
        GORAN-EXPLANATION: confronted with the problem that we cannot have public-key auth on 
        AFS machines and the impossibility to establish direct connections to beamline computers,
        another solution had to be found...
        apparently it is quite tricky to set up SSH not to ask for a PW or
        to read it from STDIN because it always calls "gnome-ssh-askpass" to provide a password
        which is a GUI-dialog that we want to avoid!!! there are several SSH libraries, apparently
        all of them with pros and cons and bugs. so what we only use subprocess with the following:
        first we create temporary files with PW for x02da-gw and cons-2 and reset SSH_ASKPASS
        variable to get the password out of this file. this is necessary because every python
        subprocess runs in a pseudo-terminal and SSH requires a full terminal, otherwise it calls
        "gnome-ssh-askpass" >> for this reason SSH is "tricked" ...!!!
        '''
        
        ## (1) first we create files with passwords
        kk = 1
        afshome = '/afs/psi.ch/user/'+self.afsuser[0]+'/'+self.afsuser
        for ii in [self.afspw,self.eaccountpw]:
            pw = 'echo \\\"'+ii+'\\\"'
            p1 = subprocess.call(['echo "#!/bin/bash\n" > '+afshome+'/pw'+str(kk)+'.sh'],shell=True)
            p2 = subprocess.call(['echo '+pw+' >> '+afshome+'/pw'+str(kk)+'.sh'],shell=True)
            p3 = subprocess.call(['chmod a+x '+afshome+'/pw'+str(kk)+'.sh'],shell=True)
            kk = kk+1
                
        ## (2) establish the connection to gateway
        sshProcess = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,shell=True)
        
        # TODO: substitute below lines so that we don't save cleartext pw-files >> didn't work for eaccount
        #sshProcess.stdin.write('export SSH_ASKPASS=~/returnpass.sh\n')
        #sshProcess.stdin.write('echo \\\"'+self.afspw+'\\\"|ssh '+self.afsuser+'@'+x02dagw+'\n')
        sshProcess.stdin.write('export SSH_ASKPASS='+afshome+'/pw1.sh\n')
        sshProcess.stdin.write('export DISPLAY=dummydisplay:0\n')
        sshProcess.stdin.write('ssh -o \"GSSAPIAuthentication no\" '+self.afsuser+'@'+gw+'\n')
        sshProcess.stdin.write('echo $SSH_ASKPASS\n')
        sshProcess.stdout.readline()
        
        # (3) from gateway connect to target
        sshProcess.stdin.write('export SSH_ASKPASS='+afshome+'/pw2.sh\n')
        sshProcess.stdin.write('export DISPLAY=dummydisplay:0\n')
        sshProcess.stdin.write('echo $SSH_ASKPASS\n')
        sshProcess.stdout.readline()
        sshProcess.stdin.write('ssh -o \"GSSAPIAuthentication no\" '+self.eaccountuser+'@'+target+'\n')
        sshProcess.stdin.write('echo $SSH_ASKPASS\n')
        sshProcess.stdout.readline()
        
        # (4) now we first delete the password files (before continuing)
        p = subprocess.call(['rm '+afshome+'/pw1.sh'],shell=True)
        p = subprocess.call(['rm '+afshome+'/pw2.sh'],shell=True)
        
        # (5) submit the command line string from the GUI on target
        sshProcess.stdin.write(cmd_str)
        sshProcess.stdout.readline()  # will hang here if "cmd_str" doesn't return a value !!!!!
        
        
    def inputCredentials(self,mode):
        '''
        method for getting eaccount number and password, which should then be stored
        in memory. if the passwords are incorrect they are deleted again
        '''
        logwin = Login(self.parent,mode)
        if logwin.exec_() == QDialog.Accepted:
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
            return True
        return False
        
        
    def blMountEaccount(self):
        '''
        method to be called from performInitalCheck() to mount the eaccount in AFS and check
        whether it was mounted successfully. also when run, it needs to ask for eaccount
        credentials
        '''
        mountdir = self.parent.dirs.homedir+'/slsbl/x02da/'+self.eaccountuser
        p1 = subprocess.check_call(['blumount -d '+mountdir],shell=True)
        p1 = subprocess.check_call(['blmount -a '+self.eaccountuser+' -s x02da -p '+self.eaccountpw],shell=True)
        
        if not os.listdir(mountdir):
            return False
        else:
            return True
        
    
    def checkAfsCredentials(self):
        '''
        we do an ssh connection to an AFS computer and return true if we manage
        to "land" on that computer
        TODO: very pseudo-method >>> find a better way
        '''
        if not self.afsuser or not self.afspw:
            self.parent.displayErrorMessage('Missing','No blank fields for AFS-credentials allowed')
            return
        
        comp = 'llc1'
        pw = 'echo \\\"'+self.afspw+'\\\"'
        p1 = subprocess.Popen(['echo "#!/bin/bash\n" > ~/pw.sh'],shell=True)
        p2 = subprocess.Popen(['echo '+pw+' >> ~/pw.sh'],shell=True)
        p3 = subprocess.Popen(['chmod a+x ~/pw.sh'],shell=True)        
        
        queue1 = Queue()
        p = Process(target=self.checkAfsCredentialsHelper,args=(comp,queue1))
        p.start()
        p.join(2)
        try:
            if queue1.get():  # we try to get the queue >> will throw an error after timeout
                subprocess.call(['rm ~/pw.sh'],shell=True)
                return True
        except IOError as e:
            subprocess.call(['rm ~/pw.sh'],shell=True)
            p.terminate()
            self.parent.displayErrorMessage('Error','Wrong AFS Password/Username!')
            return False
        except ValueError:
            print "value error"
            return False


    def checkAfsCredentialsHelper(self,comp,queue1):#,comp):
        '''
        helper method for checkAfsCredentials in order to enable timeout of operation
        '''        
        p = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, shell=True)
        p.stdin.write('export SSH_ASKPASS=~/pw.sh\n')
        p.stdin.write('ssh -o \"GSSAPIAuthentication no\" '+self.afsuser+'@'+comp+'\n')
        p.stdin.write('echo $HOSTNAME\n')
        host = p.stdout.readline() ### this method hangs if password is wrong!!!
        if str(host[:len(comp)]) == str(comp):
            queue1.put(True)
            

class Login(QDialog):
    '''
    minimalistic class for Login dialog 
    '''
    def __init__(self,parent,mode):
        QDialog.__init__(self)
        self.heading = QLabel()
        self.heading.setObjectName("head")
        self.heading.setText(QApplication.translate("Dialog", "Input "+mode+"-Credentials", None, QApplication.UnicodeUTF8))
        self.label = QLabel()
        self.label.setObjectName("label")
        self.label.setText(QApplication.translate("Dialog", "Login:", None, QApplication.UnicodeUTF8))
        self.label2 = QLabel()
        self.label2.setObjectName("label2")
        self.label2.setText(QApplication.translate("Dialog", "Password:", None, QApplication.UnicodeUTF8))
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.parent = parent
        self.buttonlogin = QPushButton('Login', self)
        self.buttonlogin.clicked.connect(self.execLoginButton)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.label2)
        layout.addWidget(self.password)
        layout.addWidget(self.buttonlogin)
   
   
    def execLoginButton(self):
        '''
        method that is run when login button is pressed
        '''
        if not self.username.text() or not self.password.text():
            self.parent.displayErrorMessage('Empty fields','The password and/or user name cannot be left blank')
        else:
            self.accept()
            
        
if __name__ == "__main__":
    # test playground
    asdf = "echo "+'asdf'
    p1 = subprocess.call(['echo "#!/bin/bash\n" > ~/test.sh'],shell=True)
    p2 = subprocess.call(['echo '+asdf+' >> ~/test.sh'],shell=True)
    p3 = subprocess.call(['chmod a+x ~/test.sh'],shell=True)