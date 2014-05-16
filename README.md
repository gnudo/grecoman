Graphical RECOnstruction MANager 1.0beta
========

## Installation
Run the following command from x02da-cons-2 *or* on your AFS account 

```
wget -O ~/Desktop/GRecoMan https://raw.githubusercontent.com/gnudo/grecoman/master/GRecoMan;chmod a+x ~/Desktop/GRecoMan;
```

After that you'll find a Desktop-icon for GRecoMan that you simply need to double-click for running the application.

## Usage

Since it's still a beta version, there are missing warnings in the GUI when mistyping some things. Therefore note the following:

* everything starts by loading a tif directory and selecting the location from where GRecoMan is running
* after that correct the prefix to be the same as in the logfile (since logfile-parsing is not yet implemented)
* make sure to check an "action" on the right to indicate what you want the pipeline to compute
* note that for running a full reconstruction, sinograms already need to be created 

## Problems

Bugs, problems, questions, wishes and remarks please indicate through [github issues](https://github.com/gnudo/source-size-calculator/issues).
