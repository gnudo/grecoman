gui.py : gui.ui
	pyuic4 gui.ui -o gui.py
	externals/versionIncluder.py