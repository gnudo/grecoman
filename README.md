GRecoMan 1.0.1
========

Public repository of the Graphical Reconstruction Manager for use at the [TOMCAT beamline](http://www.psi.ch/sls/tomcat/). For using it, please follow the steps below. In addition, the repository can also be cloned/downloaded to any PSI/AFS and/or beamline computer and run locally. There are two branches: *master* for the last stable release and *development* including the most recent (eventually untested) features.

## Installation
Run the following command from x02da-cons-2 *or* on your AFS account:

```
curl -o ~/Desktop/GRecoMan https://raw.githubusercontent.com/gnudo/grecoman/master/GRecoMan;chmod a+x ~/Desktop/GRecoMan;
```

For running the application, you'll find a Desktop-icon for GRecoMan that you simply need to double-click.

## Usage

For the most part the basic functionality has been debugged and usage should be straight-forward. The following knowledge should be enough for successfully running the application:

* everything starts by loading a tif directory and selecting the location from where GRecoMan is running (AFS or cons-2)
* if you want to have preview in Fiji, make sure to also activate the single instance listener in Fiji (Edit -> Options -> Misc. -> Run single..)
* when reconstructing with the angles.txt file, place it into your sinogram-directory
* on computers with newer OpenSSH versions (above 5.6), you cannot run the program from the terminal - just by double-clicking the Desktop-icon
* zinger removal is not yet implemented

## Problems

Bugs, problems, questions, "new feature"-wishes and remarks please indicate through [github issues](https://github.com/gnudo/grecoman/issues).
