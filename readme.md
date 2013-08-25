MasterChess
===========

A simple, cross-platform chess team management system

Contents
--------

* `MasterChess` - a Python module (package) for basic chess team management
* `MasterChessGUI` - a graphical interface (written using wxPython) for the MasterChess module
* `Mac components`
    * `MC-QuickLook` - a QuickLook plugin for `*.mcdb` files
    * `MC-Spotlight` - a Spotlight plugin for `*.mcdb` files

Building the MasterChess GUI
----------------------------

Windows: `python.exe setup.py py2exe`

Mac: `python2.5 setup.py py2app` (If MC-QuickLook or MC-Spotify are already built (in `Mac components/MC-{QuickLook,Spotlight}/build/{Debug,Release}`), setup.py will automatically add them to the bundle.)
