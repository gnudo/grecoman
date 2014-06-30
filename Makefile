src/gui.py : ui_files/gui.ui
	pyuic4 ui_files/gui.ui -o src/gui.py
	externals/versionIncluder.py