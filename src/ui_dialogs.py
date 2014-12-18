from PyQt4.QtGui import *
from PyQt4.QtCore import *


class DebugCommand(QDialog):
    '''
    GUI window for displaying and changing the command line string
    being sent to the cluster. It is displayed when "Print command line
    string (debug)" is checked.
    '''
    def __init__(self, parent):
        QDialog.__init__(self)
        self.heading = QLabel()
        self.heading.setObjectName("head")
        self.heading.setText(QApplication.translate("Debug command",
                                                    "Command to be submitted:",
                                                    None,
                                                    QApplication.UnicodeUTF8))
        self.buttonsubmit = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.textfield = QTextEdit(self)
        self.buttonsubmit.accepted.connect(self.accept)
        self.buttonsubmit.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.textfield)
        layout.addWidget(self.buttonsubmit)
        self.resize(600, 300)
        

class Login(QDialog):
    '''
    GUI window for entering credentials for various accounts, which
    can be (depending on "mode"): AFS, eaccount or Merlin. For the
    "Merlin" account we assume to have set up public key
    authentification. Thus, only a Merlin username has to be provided. 
    '''
    def __init__(self, parent, mode):
        QDialog.__init__(self)
        self.heading = QLabel()
        self.heading.setObjectName("head")
        self.heading.setText(QApplication.translate("Dialog", "Input " + mode
                                                    + "-Credentials", None,
                                                    QApplication.UnicodeUTF8))
        self.label = QLabel()
        self.label.setObjectName("label")
        self.label.setText(QApplication.translate("Dialog", "Login:", None,
                                                  QApplication.UnicodeUTF8))
        if not mode == 'Merlin':
            self.label2 = QLabel()
            self.label2.setObjectName("label2")
            self.label2.setText(QApplication.translate("Dialog", "Password:",
                                                       None,
                                                       QApplication.UnicodeUTF8))
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        if mode == 'Merlin':  # for Merlin we don't need a PW,
            self.password.hide()
            self.password.setText('test')
        self.parent = parent
        self.buttonlogin = QPushButton('Login', self)
        self.buttonlogin.clicked.connect(self.execLoginButton)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.label)
        layout.addWidget(self.username)
        if not mode == 'Merlin':
            layout.addWidget(self.label2)
            layout.addWidget(self.password)
        layout.addWidget(self.buttonlogin)

    def execLoginButton(self):
        '''Method that is run when pressing the login button'''
        if not self.username.text() or not self.password.text():
            self.parent.displayErrorMessage('Empty fields',
                                            'The password and/or user name '
                                            'cannot be left blank')
        else:
            self.accept()


class Postfix(QDialog):
    '''
    GUI Window (simple QLineedit) for entering a postfix)
    '''
    def __init__(self, parent):
        QDialog.__init__(self)
        self.heading = QLabel()
        self.heading.setObjectName("head")
        self.heading.setText(QApplication.translate("Dialog",
                                                    "Define Postfix:", None,
                                                    QApplication.UnicodeUTF8))
        self.postfix = QLineEdit(self)
        self.parent = parent
        self.buttonok = QPushButton('Ok', self)
        self.buttonok.clicked.connect(self.accept)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.postfix)
        layout.addWidget(self.buttonok)