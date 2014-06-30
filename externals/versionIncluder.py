#!/usr/bin/env python
import subprocess
import os.path
'''
DESCRIPTION: git pre-commit hook for having automatic version name
of GRecoMan in the title-window. To activate the hook, run following
command from <grecoman/.git/hooks/> directory:
--> ln -s ../../externals/versionIncluder.py pre-commit;chmod +x pre-commit;
ATTENTION: if using MAKEFILE, then git hooking is unnecessary
'''

'''
(1) get the current git description
'''
label, stderr = subprocess.Popen(["git", "describe","--tags"],stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE).communicate()

'''
(2) change the app name in the GUI
'''
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.split(currentdir)[0]

filename = os.path.join(parentdir,'ui_main.py')

f = open(filename,'r')
content = f.read()
f.close()

newcontent = content.replace('GRecoMan', 'GRecoMan '+label[:-1])

'''
(3) write a new GUI file
'''
f = open(filename,'w')
f.write(newcontent)
f.close()

'''
(4) add changed GUI file
'''
subprocess.check_call(["git","add","gui.py"])