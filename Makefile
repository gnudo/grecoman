src/ui_main.py : ui_files/main.ui
	pyuic4 ui_files/main.ui -o src/ui_main.py
	pyrcc4 -o src/ui_icons_rc.py ui_files/ui_icons.qrc
	externals/versionIncluder.py