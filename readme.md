# MasterChess

A simple, cross-platform chess team management system

## Contents

- `MasterChess` - a Python module (package) for basic chess team management
- `MasterChessGUI` - a graphical interface (written using wxPython) for the MasterChess module
- `Mac components`
    - `MC-QuickLook` - a QuickLook plugin for `*.mcdb` files
    - `MC-Spotlight` - a Spotlight plugin for `*.mcdb` files

## Using the MasterChess module

To explore the module, open the Python interactive shell in the `masterchess` directory. Then, try:

```python
import MasterChess
help(MasterChess)
help(MasterChess.mc)
```

## Using the MasterChess GUI

This is a graphical interface for the MasterChess module written in wxPython.

Just run `python MasterChessGUI.py` to run it. (For more details, see the OS-specific info in "Building the MasterChess GUI.")

## Building the MasterChess GUI

These methods use the `setup.py` file to package the MasterChess GUI into an OS-specific executable.

### Windows

Requirements:

- [Python 2.x](https://www.python.org/download/)
- [wxPython](http://www.wxpython.org/download.php)
- [setuptools](https://pypi.python.org/pypi/setuptools)
- [py2exe](http://www.py2exe.org/) ([PyPi](https://pypi.python.org/pypi/py2exe/))

To build the .exe, run: `python.exe setup.py py2exe`

If you get an error like `error: [Errno 2] No such file or directory: 'MSVCP90.dll'`, [search for it on the Internet](https://www.google.com/search?q=error%3A+[Errno+2]+No+such+file+or+directory%3A+%27MSVCP90.dll%27) to find the best solution for you.

### Mac OS X

Requirements (usually pre-installed):

- Python 2.x (tested with Python 2.5 on Snow Leopard)
- wxPython
- setuptools
- py2app

There are two additional components for Mac: MC-QuickLook and MC-Spotlight (for QuickLook and Spotlight plugins). They exist as XCode projects in the `Mac components` folder. If MC-QuickLook or MC-Spotlight are already built (in `Mac components/MC-{QuickLook,Spotlight}/build/{Debug,Release}`), setup.py will automatically add them to the bundle.

To build the .app bundle, run: `python2.5 setup.py py2app`

After the .app bundle is built, it can sometimes be helpful to run:

`/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -f dist/MasterChess.app`

`mdimport -d2 ~/test.mcdb` (if such a file exists)

### Other OSes (Linux, etc.)

Requirements:

- Python 2.x (tested with Python 2.7)
- wxPython (tested with the GTK version)
- setuptools (if you plan to use setup.py)

To build and install as a package: `python2 setup.py build` and `python2.5 setup.py install` (You may have to delve into the `setup.py` file and tweak it for your situation.)
