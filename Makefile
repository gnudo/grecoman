src/ui_main.py : ui_files/main.ui
	pyuic4 ui_files/main.ui -o src/ui_main.py
	externals/versionIncluder.py