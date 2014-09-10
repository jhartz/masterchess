"""
Setup/build script for MasterChess

For usage info, see readme.md
"""

import os, sys, subprocess
from distutils.dir_util import copy_tree

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

from MasterChessGUI import __description__, __copyright__, __version__

def get_folder(path):
    if isinstance(path, list):
        return [get_folder(i) for i in path]
    else:
        return (path, [os.path.join(path, i) for i in os.listdir(path) if i[:1] != "." and os.path.isfile(os.path.join(path, i))])


DATA_FILES = [get_folder("resources")]
DATA_FILES_MAC = ["QuickLook.py"]
DATA_MODULE_PACKAGES = ["MasterChess"]
PY2EXE_BUNDLE = False

options = {
    "name": "MasterChess",
    "version": __version__,
    "description": __description__,
    "author": "Jake Hartz",
    "author_email": "jhartz@outlook.com",
    "license": "GPL",
    "url": "http://jhartz.github.io/masterchess/"
}

if sys.platform == "darwin" and "py2app" in sys.argv:
    options.update({
        "setup_requires": ["py2app"],
        "app": ["MasterChessGUI.py"],
        "data_files": DATA_FILES + DATA_FILES_MAC,
        "options": {
            "py2app": {
                "argv_emulation": True,
                "iconfile": "resources/Chess.icns",
                "plist": {
                    "CFBundleIdentifier": "com.github.jhartz.masterchess",
                    "CFBundleGetInfoString": __description__,
                    "NSHumanReadableCopyright": __copyright__,
                    "UTExportedTypeDeclarations": [
                        {
                            "UTTypeIdentifier": "com.github.jhartz.masterchess.mcdb",
                            "UTTypeDescription": "MasterChess database",
                            #"UTTypeIconFile": "Chess.icns",
                            "UTTypeConformsTo": [
                                "public.data"
                            ],
                            "UTTypeTagSpecification": {
                                "public.filename-extension": "mcdb"
                            }
                        }
                    ],
                    "CFBundleDocumentTypes": [
                        {
                            #"CFBundleTypeExtensions": [
                            #    "mcdb"
                            #],
                            "CFBundleTypeIconFile": "Chess.icns",
                            #"CFBundleTypeName": "MasterChess database",
                            "CFBundleTypeName": "MasterChess database",
                            "LSItemContentTypes": [
                                "com.github.jhartz.masterchess.mcdb"
                            ],
                            "CFBundleTypeRole": "Editor",
                            "LSHandlerRank": "Owner"
                        }
                    ]
                }
            }
        }
    })
elif sys.platform == "win32" and "py2exe" in sys.argv:
    import py2exe
    options.update({
        "setup_requires": ["py2exe"],
        "data_files": DATA_FILES,
        "windows": [
            {
                "script": "MasterChessGUI.py",
                "icon_resources": [(1, "resources/Chess.ico")],
                "other_resources": [(u"VERSIONTAG", 1, "MasterChess " + __version__)]  # TODO: Test this!!
            }
        ]
    })
    if PY2EXE_BUNDLE:
        # TODO: Why does this cause the old-style (ie. pre-Windows XP) win32 widgets to be used?
        options.update({
            "options": {
                "py2exe": {
                    "bundle_files": 1
                }
            },
            "zipfile": None
        })
else:
    options.update({
        "scripts": ["MasterChessGUI.py"],
        "packages": DATA_MODULE_PACKAGES,
        "data_files": DATA_FILES,
        "install_requires": ["wx"]
    })


setup(**options)


if sys.platform == "darwin" and "py2app" in sys.argv:
    # If we have a compiled MC-QuickLook or MC-Spotlight, include that
    if os.path.isdir(os.path.join("dist", "MasterChess.app", "Contents")):
        # QuickLook
        loc = os.path.join("Mac components", "MC-QuickLook", "Build", "Release", "MC-QuickLook.qlgenerator")
        if not os.path.exists(loc):
            # Try debug version
            loc = os.path.join("Mac components", "MC-QuickLook", "Build", "Debug", "MC-QuickLook.qlgenerator")
        if os.path.exists(loc):
            print ""
            print "Copying MC-QuickLook to app bundle"
            copy_tree(loc, os.path.join("dist", "MasterChess.app", "Contents", "Library", "QuickLook", os.path.basename(loc)))
            print "Reloading quicklookd"
            try:
                subprocess.call(["qlmanage", "-r"])
                subprocess.call(["qlmanage", "-r", "cache"])
            except OSError:
                print "Error calling qlmanage (manually call `qlmanage -r` and `qlmanage -r cache` to reload quicklookd)"
        
        # Spotlight
        loc = os.path.join("Mac components", "MC-Spotlight", "Build", "Release", "MC-Spotlight.mdimporter")
        if not os.path.exists(loc):
            # Try debug version
            loc = os.path.join("Mac components", "MC-Spotlight", "Build", "Debug", "MC-Spotlight.mdimporter")
        if os.path.exists(loc):
            print ""
            print "Copying MC-Spotlight to app bundle"
            copy_tree(loc, os.path.join("dist", "MasterChess.app", "Contents", "Library", "Spotlight", os.path.basename(loc)))