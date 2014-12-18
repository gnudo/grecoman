GRecoMan 1.2.0
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

* start by loading a data directory and check the location from where GRecoMan is running (AFS or cons-2)
* if you want to have preview in Fiji, make sure to also activate the single instance listener in Fiji (Edit -> Options -> Misc. -> Run single..)
* when reconstructing with the angles.txt file, place it into your tif-directory
* on computers with newer OpenSSH versions (above 5.6), you cannot run the program from the terminal - just by double-clicking the Desktop-icon
* for using Merlin, you need you set up Public key (password-less) authentication and the Merlin home directory needs to be mounted somewhere (e.g. with *sshfs merlinc01:/gpfs/home/$MERLINUSER ~/Desktop/merlin/*). Then, when changing the submission target in GRecoMan, you'll be asked the Merlin user name and mount point.

## Problems

Bugs, problems, questions, "new feature"-wishes and remarks please indicate through [GitHub issues](https://github.com/gnudo/grecoman/issues).
