"""
Setup/build script for MasterChess

 Usage (Mac OS X):
     python2.5 setup.py py2app

 Usage (Windows):
     python setup.py py2exe
"""

import os, sys, subprocess
from distutils.dir_util import copy_tree

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

from gui_wx import __description__, __copyright__, __version__

def get_folder(path):
    if isinstance(path, list):
        return [get_folder(i) for i in path]
    else:
        return (path, [os.path.join(path, i) for i in os.listdir(path) if i[:1] != "." and os.path.isfile(os.path.join(path, i))])


DATA_FILES = [get_folder("resources")]
DATA_FILES_MAC = ["QuickLook.py"]
DATA_MODULE_PACKAGES = ["MasterChess"]

options = {
    "name": "MasterChess",
    "version": __version__,
    "description": __description__,
    "author": "Jake Hartz",
    "author_email": "jake33@rocketmail.com",
    "license": "GPL"
}

if sys.platform == "darwin" and sys.argv[1] == "py2app":
    options.update({
        "setup_requires": ["py2app"],
        "app": ["gui_wx.py"],
        "data_files": DATA_FILES + DATA_FILES_MAC + get_folder(DATA_MODULE_PACKAGES),
        "options": {
            "py2app": {
                "argv_emulation": True,
                "iconfile": "resources/Chess.icns",
                "plist": {
                    "CFBundleIdentifier": "com.github.jake33.masterchess",
                    "CFBundleGetInfoString": __description__,
                    "NSHumanReadableCopyright": __copyright__,
                    "UTExportedTypeDeclarations": [
                        {
                            "UTTypeIdentifier": "com.github.jake33.masterchess.mcdb",
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
                                "com.github.jake33.masterchess.mcdb"
                            ],
                            "CFBundleTypeRole": "Editor",
                            "LSHandlerRank": "Owner"
                        }
                    ]
                }
            }
        }
    })
elif sys.platform == "win32":
    options.update({
        "setup_requires": ["py2exe"],
        "data_files": DATA_FILES + get_folder(DATA_MODULE_PACKAGES),
        "windows": [
            {
                "script": "gui_wx.py",
                "icon_resources": [(1, "resources/Chess.ico")],
                "other_resources": [(u"VERSIONTAG", 1, "MasterChess " + __version__)]  # TODO: Test this!!
            }
        ],
        #"options": {
        #    "py2exe": {
        #        "bundle_files": 1
        #    }
        #},
        #"zipfile": None
    })
else:
    options.update({
        "scripts": ["gui_wx.py"],
        "packages": DATA_MODULE_PACKAGES,
        "data_files": DATA_FILES,
        "install_requires": ["wx"]
    })


setup(**options)


if sys.platform == "darwin" and sys.argv[1] == "py2app":
    # If we have a compiled MC-QuickLook mc MC-Spotlight, include that
    if os.path.isdir(os.path.join("dist", "MasterChess.app", "Contents")):
        # QuickLook
        loc = os.path.join("Mac components", "MC-QuickLook", "Build", "Release", "MC-QuickLook.qlgenerator")
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
        loc = os.path.join("Mac components", "MC-Spotlight", "Build", "Debug", "MC-Spotlight.mdimporter")
        if os.path.exists(loc):
            print ""
            print "Copying MC-Spotlight to app bundle"
            copy_tree(loc, os.path.join("dist", "MasterChess.app", "Contents", "Library", "Spotlight", os.path.basename(loc)))