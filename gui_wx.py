"""
MasterChess wxPython GUI
Copyright (C) 2012 Jake Hartz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Requires Python 2.5 or later (well... not including Python 3)
Also, although this uses wx and is therefore cross-platform, it looks downright ugly on Windows.
"""

from __future__ import with_statement
import os, sys, datetime, tempfile, webbrowser, weakref
import wx, wx.grid, wx.lib.buttons
try:
    import cPickle as pickle
except ImportError:
    import pickle

from MasterChess import open_database
from MasterChess.mc import Struct

__author__ = "Jake Hartz"
__description__ = "A simple chess team management system"
__copyright__ = "Copyright (C) 2012 Jake Hartz"
__license__ = "GPL"
__version__ = "1.0"


def get_local_file(relative_path):
    if wx.Platform == "__WXMSW__":
        return os.path.join(os.getcwd(), "resources", relative_path)
    else:
        return os.path.join("resources", relative_path)


def get_recent_databases():
    sp = wx.StandardPaths.Get()
    config_dir = sp.GetUserDataDir()
    try:
        # Make sure directory exists
        os.makedirs(config_dir)
    except OSError:
        # It may have already existed; if so, we can ignore the exception
        if not os.path.isdir(config_dir):
            # There was a different error on creation
            raise
    recentDB = os.path.join(config_dir, "MasterChess_cache")
    
    recentDBs = []
    if os.path.exists(recentDB):
        data = ""
        with open(recentDB, "r") as f:
            while True:
                newdata = f.read()
                if newdata == "":
                    break
                data += newdata
        if data:
            for d in data.splitlines():
                if os.path.exists(d):
                    recentDBs.append(d)
    return recentDBs

def add_recent_database(path):
    sp = wx.StandardPaths.Get()
    config_dir = sp.GetUserDataDir()
    try:
        # Make sure directory exists
        os.makedirs(config_dir)
    except OSError:
        # It may have already existed; if so, we can ignore the exception
        if not os.path.isdir(config_dir):
            # There was a different error on creation
            raise
    recentDB = os.path.join(config_dir, "MasterChess_cache")
    
    recentDBs = []
    if os.path.exists(recentDB):
        data = ""
        with open(recentDB, "r") as f:
            while True:
                newdata = f.read()
                if newdata == "":
                    break
                data += newdata
        if data:
            for d in data.splitlines():
                if os.path.exists(d):
                    recentDBs.append(d)
    
    if path in recentDBs:
        recentDBs.remove(path)
    recentDBs.insert(0, path)
    with open(recentDB, "w") as f:
        for r in recentDBs:
            f.write(r + "\n")

def remove_recent_database(path):
    sp = wx.StandardPaths.Get()
    config_dir = sp.GetUserDataDir()
    try:
        # Make sure directory exists
        os.makedirs(config_dir)
    except OSError:
        # It may have already existed; if so, we can ignore the exception
        if not os.path.isdir(config_dir):
            # There was a different error on creation
            raise
    recentDB = os.path.join(config_dir, "MasterChess_cache")
    if os.path.exists(recentDB):
        data = ""
        with open(recentDB, "r") as f:
            while True:
                newdata = f.read()
                if newdata == "":
                    break
                data += newdata
        if data:
            recentDBs = []
            for d in data.splitlines():
                if os.path.exists(d):
                    recentDBs.append(d)
            if path in recentDBs:
                recentDBs.remove(path)
                with open(recentDB, "w") as f:
                    for r in recentDBs:
                        f.write(r + "\n")


# Menu item functions - specified here since menu is specified in 2 places
def menu_about():
    info = wx.AboutDialogInfo()
    info.SetName("MasterChess")
    info.SetVersion(__version__)
    info.SetCopyright(__copyright__)
    license = "Licensed under the GNU General Public License version 3.\nFor details, see LICENSE or <http://www.gnu.org/licenses/gpl-3.0.html>"
    if wx.Platform == "__WXGTK__":
        newlicense = ""
        with open("LICENSE") as f:
            while True:
                buffer = f.read()
                if buffer == "":
                    break
                newlicense += buffer
        if newlicense:
            license = newlicense
    if wx.Platform != "__WXMAC__":
        info.SetLicense(license)
        info.SetWebSite("http://jake33.github.com/MasterChess/")
        info.SetIcon(wx.Icon(get_local_file("Chess-48.png"), wx.BITMAP_TYPE_PNG))
        info.SetDescription(__description__)
    else:
        info.SetDescription("A simple GPL-licensed chess team management system")
    wx.AboutBox(info)

def menu_new(parent):
    dlg = wx.FileDialog(None, "New Database", "", "Chess " + str(datetime.date.today().year) + ".mcdb", "MasterChess Database (*.mcdb)|*.mcdb", wx.SAVE | wx.OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK:
        dirname = dlg.GetDirectory()
        path = os.path.join(dirname, dlg.GetFilename())
        if parent.load_database(path) == False:
            msgdlg = wx.MessageDialog(None, "There was an error creating " + path, "Database Error", wx.OK | wx.ICON_ERROR)
            msgdlg.ShowModal()
            msgdlg.Destroy()
    dlg.Destroy()

def menu_open(parent):
    dlg = wx.FileDialog(None, "Open Database", "", "", "MasterChess Database (*.mcdb)|*.mcdb|All Files|*.*", wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
        dirname = dlg.GetDirectory()
        filename = dlg.GetFilename()
        path = os.path.join(dirname, dlg.GetFilename())
        if parent.load_database(path) == False:
            msgdlg = wx.MessageDialog(None, "There was an error opening " + path, "Database Error", wx.OK | wx.ICON_ERROR)
            msgdlg.ShowModal()
            msgdlg.Destroy()
    dlg.Destroy()

def menu_email():
    webbrowser.open("mailto:jake3311@gmail.com?subject=MasterChess")

def menu_prefs():
    PrefFrame()


def get_pref_file():
    sp = wx.StandardPaths.Get()
    config_dir = sp.GetUserDataDir()
    try:
        # Make sure directory exists
        os.makedirs(config_dir)
    except OSError:
        # It may have already existed; if so, we can ignore the exception
        if not os.path.isdir(config_dir):
            # There was a different error on creation
            raise
    pref_file = os.path.join(config_dir, "MasterChess_config")
    return pref_file

def get_pref(prefname):
    pref_file = get_pref_file()
    if os.path.exists(pref_file):
        with open(pref_file, "rb") as f:
            data = pickle.load(f)
        if data and prefname in data:
            return data[prefname]
    # If we're still here...
    return None

def set_pref(prefname, prefvalue):
    pref_file = get_pref_file()
    data = {}
    if os.path.exists(pref_file):
        with open(pref_file, "rb") as f:
            data = pickle.load(f)
    data[prefname] = prefvalue
    with open(pref_file, "wb") as f:
        pickle.dump(data, f, -1)


class PrefFrame(wx.Frame):
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, title="MasterChess Preferences", style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX)
        
        if wx.Platform != "__WXMAC__":
            self.SetIcon(wx.Icon(get_local_file("Chess.ico"), wx.BITMAP_TYPE_ICO))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.names_check = wx.CheckBox(panel, label="Show only last names for players")
        val = get_pref("last_names")
        if val:
            self.names_check.SetValue(True)
        sizer.Add(self.names_check, 0, wx.ALL, 10)
        
        ok_button = wx.Button(panel, wx.ID_OK)
        ok_button.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnOK, ok_button)
        sizer.Add(ok_button, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        
        panel.SetSizer(sizer)
        
        bigsizer = wx.BoxSizer(wx.HORIZONTAL)
        bigsizer.Add(panel)
        self.SetSizer(bigsizer)
        
        self.Fit()
        self.Center()
        self.Show()
    
    def OnOK(self, event):
        set_pref("last_names", self.names_check.GetValue())
        self.Destroy()


class MainFrame(wx.Frame):
    def __init__(self, parent=None, mc_instance=None, auto_load_database=None):
        wx.Frame.__init__(self, parent, title="MasterChess", size=(800, 600))
        
        self.db_loaded = False
        if wx.Platform != "__WXMAC__":
            self.SetIcon(wx.Icon(get_local_file("Chess.ico"), wx.BITMAP_TYPE_ICO))
        
        # NOTE: Same menubar spec exists at bottom!
        menubar = wx.MenuBar()
        
        file_menu = wx.Menu()
        file_new = file_menu.Append(wx.ID_NEW, "&New Database\tCtrl+N", "Create a new chess team database")
        self.Bind(wx.EVT_MENU, self.OnNew, file_new)
        file_open = file_menu.Append(wx.ID_OPEN, "&Open Database\tCtrl+O", "Open an already-created chess team database")
        self.Bind(wx.EVT_MENU, self.OnOpen, file_open)
        file_options = file_menu.Append(wx.ID_PREFERENCES, "&Options", "Set MasterChess options")
        self.Bind(wx.EVT_MENU, self.OnPrefs, file_options)
        file_quit = file_menu.Append(wx.ID_EXIT, "&Exit All\tCtrl+Q", "Close all open MasterChess windows")
        self.Bind(wx.EVT_MENU, self.OnQuit, file_quit)
        menubar.Append(file_menu, "&File")
        
        help_menu = wx.Menu()
        help_email = help_menu.Append(wx.ID_ANY, "&Email Jake Hartz", "Email Jake Hartz with any questions or problems")
        self.Bind(wx.EVT_MENU, self.OnEmail, help_email)
        help_about = help_menu.Append(wx.ID_ABOUT, "&About MasterChess", "Information about MasterChess")
        self.Bind(wx.EVT_MENU, self.OnAbout, help_about)
        menubar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        if auto_load_database:
            if self.load_database(auto_load_database):
                return
            else:
                msgdlg = wx.MessageDialog(self, "There was an error opening " + auto_load_database, "Database Error", wx.OK | wx.ICON_ERROR)
                msgdlg.ShowModal()
                msgdlg.Destroy()
        
        self.mc = None
        if mc_instance:
            self.mc = mc_instance
            self.db_loaded = True
            if wx.Platform == '__WXMAC__':
                self.SetTitle(os.path.basename(self.mc.db_path))
            else:
                self.SetTitle("MasterChess - " + os.path.basename(self.mc.db_path))
            
            self.tabIndex = 0
            self.toolbar = self.CreateToolBar(style=wx.TB_HORIZONTAL|wx.TB_TEXT)
            self.toolbar.AddCheckLabelTool(0, "Results", wx.Bitmap(get_local_file("pie.png")))
            self.toolbar.AddCheckLabelTool(1, "Matches", wx.Bitmap(get_local_file("match-new.png")))
            self.toolbar.AddCheckLabelTool(2, "Players", wx.Bitmap(get_local_file("players.png")))
            self.toolbar.Realize()
            
            # Determine whether to invoke the special toolbar handling
            macNative = False
            if wx.Platform == '__WXMAC__':
                if hasattr(self, 'MacGetTopLevelWindowRef'):
                    try:
                        import ctypes
                        macNative = True
                    except ImportError:
                        pass
            if macNative:
                self.PrepareMacNativeToolBar()
                self.Bind(wx.EVT_TOOL, self.OnToolBarMacNative)
            else:
                self.toolbar.ToggleTool(0, True)
                self.Bind(wx.EVT_TOOL, self.OnToolBarDefault)
            
            self.panelA = ResultsPanel(self)
            self.panelB = MatchesPanel(self)
            self.panelB.Hide()
            self.panelC = PlayersPanel(self)
            self.panelC.Hide()
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.panelA, 1, wx.ALL | wx.EXPAND)
            sizer.Add(self.panelB, 1, wx.ALL | wx.EXPAND)
            sizer.Add(self.panelC, 1, wx.ALL | wx.EXPAND)
            self.SetSizer(sizer)
            
            self.Layout()
            self.Maximize()
        else:
            # Init start screen
            panel = StartPanel(self)
            self.Bind(wx.EVT_BUTTON, self.OnNew, panel.ButtonA)
            self.Bind(wx.EVT_BUTTON, self.OnOpen, panel.ButtonB)
            if len(panel.recentDB_buttons) > 0:
                def addHandler(path, button):
                    self.Bind(wx.EVT_BUTTON, lambda event: self.OnRecentDB(event, path), button)
                for path, button in panel.recentDB_buttons:
                    addHandler(path, button)
            # BG image dimensions
            self.SetMaxSize((900, 609))
        
        self.Center()
        self.Show()
    
    def OnTabChange(self, tabIndex):
        # Respond to the user switching tabs
        if tabIndex == 0:
            # Reports
            self.panelA.Show()
            self.panelB.Hide()
            self.panelC.Hide()
            
            self.panelA.reinit()
        elif tabIndex == 1:
            # Matches
            self.panelA.Hide()
            self.panelB.Show()
            self.panelC.Hide()
            
            self.panelB.reinit()
        elif tabIndex == 2:
            # Players
            self.panelA.Hide()
            self.panelB.Hide()
            self.panelC.Show()
            
            self.panelC.reinit()
        self.Layout()
    
    def PrepareMacNativeToolBar(self):
        # Load native Mac OS X toolbar
        import ctypes
        carbonLoc = '/System/Library/Carbon.framework/Carbon'
        coreLoc = '/System/Library/CoreFoundation.framework/CoreFoundation'
        self.carbon = ctypes.CDLL(carbonLoc)  # Also used in OnToolBarMacNative
        core = ctypes.CDLL(coreLoc)
        # Get a reference to the main window
        frame = self.MacGetTopLevelWindowRef()
        # Allocate a pointer to pass around
        p = ctypes.c_voidp()
        # Get a reference to the toolbar
        self.carbon.GetWindowToolbar(frame, ctypes.byref(p))
        toolbar = p.value
        # Get a reference to the array of toolbar items
        self.carbon.HIToolbarCopyItems(toolbar, ctypes.byref(p))
        # Get references to the toolbar items (note: separators count)
        self.macToolbarItems = [core.CFArrayGetValueAtIndex(p, i) for i in xrange(self.toolbar.GetToolsCount())]
        # Set the native "selected" state on the first tab
        # 128 corresponds to kHIToolbarItemSelected (1 << 7)
        item = self.macToolbarItems[self.tabIndex]
        self.carbon.HIToolbarItemChangeAttributes(item, 128, 0)
    
    def OnToolBarDefault(self, event):
        # Ensure that there is always one tab selected
        i = event.GetId()
        if i in xrange(self.toolbar.GetToolsCount()):
            self.toolbar.ToggleTool(i, True)
            if i != self.tabIndex:
                self.toolbar.ToggleTool(self.tabIndex, False)
                self.OnTabChange(i)
                self.tabIndex = i
        else:
            event.Skip()
    
    def OnToolBarMacNative(self, event):
        # Manage the toggled state of the tabs manually
        i = event.GetId()
        if i in xrange(self.toolbar.GetToolsCount()):
            self.toolbar.ToggleTool(i, False)  # Suppress default selection
            if i != self.tabIndex:
                # Set the native selection look via the Carbon APIs
                # 128 corresponds to kHIToolbarItemSelected (1 << 7)
                item = self.macToolbarItems[i]
                self.carbon.HIToolbarItemChangeAttributes(item, 128, 0)
                self.OnTabChange(i)
                self.tabIndex = i
        else:
            event.Skip()
    
    def OnAbout(self, event):
        menu_about()
    
    def OnEmail(self, event):
        menu_email()
    
    def OnPrefs(self, event):
        menu_prefs()
    
    def OnClose(self, event):
        if self.mc:
            self.mc.uninit()
        
        self.Destroy()
    
    def OnQuit(self, event):
        wx.Exit()
    
    def OnRecentDB(self, event, path):
        if self.load_database(path) == False:
            remove_recent_database(path)
            msgdlg = wx.MessageDialog(self, "There was an error opening " + path, "Database Error", wx.OK | wx.ICON_ERROR)
            msgdlg.ShowModal()
            msgdlg.Destroy()
    
    def OnNew(self, event):
        menu_new(self)
    
    def OnOpen(self, event):
        menu_open(self)
    
    def load_database(self, path):
        mc_instance = open_database(path)
        if mc_instance:
            p = get_pref("last_names")
            if p != None:
                mc_instance.set_pref("last_names", p and "yes" or "no")
            add_recent_database(path)
            bob = MainFrame(None, mc_instance)
            if self.db_loaded == False:
                self.Close(True)
            return True
        else:
            return False


class PropertiesDialog(wx.Dialog):
    """Dialog used to create/edit a new match/player."""
    
    def __init__(self, parent, title, data, returnref):
        wx.Dialog.__init__(self, parent=parent, title=title) # size=(250, 200)
        self.returnref = returnref
        self.returnref["returned_data"] = None
        self.data_elems = []
        self.titler = title
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        sb = wx.StaticBox(panel)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
        
        self.control_sizer = None
        def yes_control_sizer():
            if self.control_sizer == None:
                self.control_sizer = wx.FlexGridSizer(wx.VERTICAL)
                self.control_sizer.SetCols(2)
        def no_control_sizer():
            if self.control_sizer:
                sbs.Add(self.control_sizer)
                self.control_sizer = None
        
        for name, type, stuff in data:
            if type == "list":
                # List box
                yes_control_sizer()
                self.control_sizer.Add(wx.StaticText(panel, label=name + ":"), 0, wx.ALL, 5)
                choicebox = wx.Choice(panel)
                for thing in stuff[0]:
                    index = choicebox.Append(thing[1], thing[0])
                    if stuff[1] == thing[0]:
                        choicebox.Select(index)
                self.control_sizer.Add(choicebox, 0, wx.ALL, 5)
                self.data_elems.append((name, type, choicebox))
            elif type == "expanded_list":
                # Radio buttons
                no_control_sizer()
                lilsizer = wx.BoxSizer(wx.VERTICAL)
                lilsizer.Add(wx.StaticText(panel, label=name + ":"))
                elems = []
                for index, thing in enumerate(stuff[0]):
                    if index == 0:
                        btn = wx.RadioButton(panel, label=thing[1], style=wx.RB_GROUP)
                    else:
                        btn = wx.RadioButton(panel, label=thing[1])
                    if stuff[1] == thing[0]:
                        btn.SetValue(True)
                    lilsizer.Add(btn)
                    elems.append((btn, thing[0]))
                self.data_elems.append((name, type, elems))
                sbs.Add(lilsizer, 0, wx.ALL, 5)
            elif type == "check":
                # Checkbox
                no_control_sizer()
                checkbox = wx.CheckBox(panel, label=name)
                checkbox.SetValue(stuff)
                self.data_elems.append((name, type, checkbox))
                sbs.Add(checkbox)
            elif type in ["string", "number", "date"]:
                # Text box, spin button, or date picker
                yes_control_sizer()
                self.control_sizer.Add(wx.StaticText(panel, label=name + ":"), 0, wx.ALL, 5)
                if type == "string":
                    ctrl = wx.TextCtrl(panel)
                elif type == "number":
                    ctrl = wx.SpinCtrl(panel)
                elif type == "date":
                    ctrl = wx.DatePickerCtrl(panel, size=(120, -1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
                ctrl.SetValue(stuff)
                self.control_sizer.Add(ctrl, 0, wx.ALL, 5)
                self.data_elems.append((name, type, ctrl))
        no_control_sizer()
        panel.SetSizer(sbs)
        
        buttonbox = wx.StdDialogButtonSizer()
        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        cancel_button = wx.Button(self, wx.ID_CANCEL)
        buttonbox.AddButton(ok_button)
        buttonbox.SetAffirmativeButton(ok_button)
        buttonbox.AddButton(cancel_button)
        buttonbox.SetCancelButton(cancel_button)
        buttonbox.Realize()
        
        vbox.Add(panel, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(buttonbox, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        
        self.SetSizer(vbox)
        
        ok_button.Bind(wx.EVT_BUTTON, self.OnOK)
        cancel_button.Bind(wx.EVT_BUTTON, self.OnCancel)
        
        self.Fit()
        self.Center()
    
    def OnCancel(self, event):
        self.Destroy()
    
    def OnOK(self, event):
        data = {}
        nogood = False
        for item in self.data_elems:
            name = item[0]
            type = item[1]
            elem = item[2]
            
            if type == "list":
                sel = elem.GetSelection()
                if sel == wx.NOT_FOUND:
                    dlg = wx.MessageDialog(self, "Please make a selection for \"%s\"." % name, self.titler, wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    elem.SetFocus()
                    nogood = True
                    break
                else:
                    data[name] = elem.GetClientData(sel)
            elif type == "expanded_list":
                sel = None
                for btn, val in elem:
                    if btn.GetValue():
                        sel = val
                if sel == None:
                    dlg = wx.MessageDialog(self, "Please make a selection for \"%s\"." % name, self.titler, wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    nogood = True
                    break
                else:
                    data[name] = sel
            elif type in ["check", "string", "number", "date"]:
                val = elem.GetValue()
                if val or type == "check":
                    data[name] = val
                else:
                    dlg = wx.MessageDialog(self, "Please enter a value for \"%s\"." % name, self.titler, wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    elem.SetFocus()
                    nogood = True
                    break
        
        if nogood == False:
            self.returnref["returned_data"] = data
            self.Destroy()

class MatchesPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mc = parent.mc
        self.exclude_disabled = True
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_HRULES)
        self.list.InsertColumn(0, "White Player")
        self.list.InsertColumn(1, "Black Player")
        self.list.InsertColumn(2, "Outcome")
        self.list.InsertColumn(3, "Date")
        sizer.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)
        
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.OnListKeyDown, self.list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListActivate, self.list)
        
        new_button = wx.Button(self, label="New match", style=wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.OnNew, new_button)
        # TODO: Listen to onchange or whatever on this so when someone starts typing we can filter out matches that don't have players with these names (and, please, make this text box look nicer - maybe make it into a combo box where the drop-down list can have all the players in it - just last names if the last name pref is on (and we just filter on last names if it's on), otherwise full names)
        self.filter_box = wx.TextCtrl(self)
        self.disable_checkbox = wx.CheckBox(self, label="Show disabled matches")
        self.disable_checkbox.SetToolTip(wx.ToolTip("Disabled matches are not used to help calculate any rankings, scores, or statistics."))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.disable_checkbox)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(new_button)
        hbox.Add((15, 1), 1)
        hbox.Add(wx.StaticText(self, label="Filter: "))
        hbox.Add(self.filter_box)
        hbox.Add((15, 1), 1)
        hbox.Add(self.disable_checkbox)
        
        sizer.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
        self.reinit()
    
    def get_name(self, id=None, player=None):
        if player == None:
            player = self.mc.get_players(id)[0]
        if get_pref("last_names"):
            return player.last_name
        else:
            return player.first_name + " " + player.last_name
    
    def reinit(self):
        if self.list.GetColumnCount() == 5 and self.exclude_disabled:
            self.list.DeleteColumn(4)
        if self.list.GetColumnCount() == 4 and not self.exclude_disabled:
            self.list.InsertColumn(4, "Enabled")
        
        self.itemindexes = {}
        self.list.DeleteAllItems()
        
        matches = self.mc.get_matches(exclude_disabled=self.exclude_disabled)
        for match in matches:
            white_player = self.mc.get_players(match.white_player)[0]
            black_player = self.mc.get_players(match.black_player)[0]
            outcome = "Draw"
            if match.outcome == 0:
                outcome = "White victory"
            elif match.outcome == 1:
                outcome = "Black victory"
            elif match.outcome == 2:
                outcome = "Stalemate"
            
            # TODO: Put winning player in bold!
            index = self.list.InsertStringItem(sys.maxint, self.get_name(player=white_player))
            self.itemindexes[index] = match.id
            self.list.SetStringItem(index, 1, self.get_name(player=black_player))
            self.list.SetStringItem(index, 2, outcome)
            self.list.SetStringItem(index, 3, datetime.date.fromtimestamp(match.timestamp).strftime("%m/%d/%y"))
            if not self.exclude_disabled:
                self.list.SetStringItem(index, 4, match.enabled and "Yes" or "No")
        
        for column in xrange(4):
            self.list.SetColumnWidth(column, wx.LIST_AUTOSIZE)
            oldwidth = self.list.GetColumnWidth(column)
            self.list.SetColumnWidth(column, wx.LIST_AUTOSIZE_USEHEADER)
            if oldwidth > self.list.GetColumnWidth(column): self.list.SetColumnWidth(column, wx.LIST_AUTOSIZE)
        
        self.Layout()
    
    def OnCheck(self, event):
        self.exclude_disabled = not self.disable_checkbox.GetValue()
        self.Freeze()
        self.reinit()
        self.Thaw()
    
    def OnListKeyDown(self, event):
        keycode = event.GetKeyCode()
        item = self.list.GetFocusedItem()
        if keycode in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE, wx.WXK_BACK] and item != -1:
            self.mc.remove_match(self.itemindexes[item])
            self.list.DeleteItem(item)
    
    def OnListActivate(self, event):
        match = self.mc.get_matches(self.itemindexes[event.GetIndex()])[0]
        all_players = [(p.id, self.get_name(player=p)) for p in self.mc.get_players()]
        returned_data = Struct()  # Since we can't weakref on a plain dict
        dlg = PropertiesDialog(self, "Edit Match", [
            ("White Player", "list", (all_players, match.white_player)),
            ("Black Player", "list", (all_players, match.black_player)),
            ("Outcome", "expanded_list", ([(0, "White victory"), (1, "Black victory"), (2, "Stalemate"), (3, "Draw")], match.outcome)),
            ("Date", "date", wx.DateTimeFromTimeT(match.timestamp)),
            ("Enabled", "check", match.enabled)
        ], weakref.proxy(returned_data))
        dlg.ShowModal()
        data = returned_data.returned_data
        if data:
            old_date = datetime.date.fromtimestamp(match.timestamp)
            new_date = datetime.date.fromtimestamp(data["Date"].GetTicks())
            returning = {
                "white_player": data["White Player"],
                "black_player": data["Black Player"],
                "outcome": data["Outcome"],
                "enabled": data["Enabled"]
            }
            if new_date != old_date:
                returning["timestamp"] = data["Date"].GetTicks()
            self.mc.update_match(match.id, returning)
            self.Freeze()
            self.reinit()
            self.Thaw()
    
    def OnNew(self, event):
        all_players = [(p.id, self.get_name(player=p)) for p in self.mc.get_players()]
        if len(all_players) == 0:
            dlg = wx.MessageDialog(self, "You must add at least one player in the \"Players\" panel before adding a match.", "New Match", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            returned_data = Struct()  # Since we can't weakref on a plain dict
            today = datetime.date.today()
            mydate = wx.DateTime()
            mydate.Set(today.day, today.month, today.year)
            dlg = PropertiesDialog(self, "New Match", [
                ("White Player", "list", (all_players, None)),
                ("Black Player", "list", (all_players, None)),
                ("Outcome", "expanded_list", ([(0, "White victory"), (1, "Black victory"), (2, "Stalemate"), (3, "Draw")], None)),
                ("Date", "date", mydate)
            ], weakref.proxy(returned_data))
            dlg.ShowModal()
            data = returned_data.returned_data
            if data:
                returning = {
                    "white_player": data["White Player"],
                    "black_player": data["Black Player"],
                    "outcome": data["Outcome"]
                }
                if data["Date"] != mydate:
                    returning["timestamp"] = data["Date"].GetTicks()
                self.mc.add_match(**returning)
                self.Freeze()
                self.reinit()
                self.Thaw()

class PlayersPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mc = parent.mc
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_HRULES)
        self.list.InsertColumn(0, "Name")
        self.list.InsertColumn(1, "Grade")
        self.list.InsertColumn(2, "Wins")
        self.list.InsertColumn(3, "Losses")
        self.list.InsertColumn(4, "Total")
        sizer.Add(self.list, 1, wx.ALL | wx.EXPAND, 5)
        
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.OnListKeyDown, self.list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListActivate, self.list)
        
        new_button = wx.Button(self, label="New player", style=wx.ALIGN_LEFT)
        self.Bind(wx.EVT_BUTTON, self.OnNew, new_button)
        sizer.Add(new_button, 0, wx.ALL, 5)
        
        self.SetSizer(sizer)
        
        self.reinit()
    
    def reinit(self):
        self.list.DeleteAllItems()
        self.itemindexes = {}
        
        players = self.mc.get_players()
        for player in players:
            win_stats = ""
            loss_stats = ""
            if player.stats.total > 0:
                win_stats = "  (" + str(int(round((float(player.stats.wins) / float(player.stats.total)) * 100))) + "%)  "
                loss_stats = "  (" + str(int(round((float(player.stats.losses) / float(player.stats.total)) * 100))) + "%)  "
            
            namer = ""
            if get_pref("last_names"):
                namer = player.last_name + ", " + player.first_name
            else:
                namer = player.first_name + " " + player.last_name
            index = self.list.InsertStringItem(sys.maxint, namer)
            self.itemindexes[index] = player.id
            self.list.SetStringItem(index, 1, str(player.grade))
            self.list.SetStringItem(index, 2, str(player.stats.wins) + win_stats)
            self.list.SetStringItem(index, 3, str(player.stats.losses) + loss_stats)
            self.list.SetStringItem(index, 4, str(player.stats.total))
        
        for column in xrange(5):
            self.list.SetColumnWidth(column, wx.LIST_AUTOSIZE)
            oldwidth = self.list.GetColumnWidth(column)
            self.list.SetColumnWidth(column, wx.LIST_AUTOSIZE_USEHEADER)
            if oldwidth > self.list.GetColumnWidth(column): self.list.SetColumnWidth(column, wx.LIST_AUTOSIZE)
        
        self.Layout()
    
    def OnListKeyDown(self, event):
        keycode = event.GetKeyCode()
        item = self.list.GetFocusedItem()
        if keycode in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE, wx.WXK_BACK] and item != -1:
            self.mc.remove_player(self.itemindexes[item])
            self.list.DeleteItem(item)
    
    def OnListActivate(self, event):
        player = self.mc.get_players(self.itemindexes[event.GetIndex()])[0]
        returned_data = Struct()  # Since we can't weakref on a plain dict
        dlg = PropertiesDialog(self, "Edit Player", [
            ("First Name", "string", player.first_name),
            ("Last Name", "string", player.last_name),
            ("Grade", "number", player.grade)
        ], weakref.proxy(returned_data))
        dlg.ShowModal()
        data = returned_data.returned_data
        if data:
            self.mc.update_player(player.id, {
                "first_name": data["First Name"],
                "last_name": data["Last Name"],
                "grade": data["Grade"]
            })
            self.Freeze()
            self.reinit()
            self.Thaw()
    
    def OnNew(self, event):
        returned_data = Struct()  # Since we can't weakref on a plain dict
        dlg = PropertiesDialog(self, "New Player", [
            ("First Name", "string", ""),
            ("Last Name", "string", ""),
            ("Grade", "number", 12)
        ], weakref.proxy(returned_data))
        dlg.ShowModal()
        data = returned_data.returned_data
        if data:
            self.mc.add_player(data["First Name"], data["Last Name"], data["Grade"])
            self.Freeze()
            self.reinit()
            self.Thaw()


class ResultsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mc = parent.mc
        
        self.notebook = ResultsNotebook(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 6)
        self.SetSizer(sizer)
        
        self.reinit()
    
    def reinit(self):
        self.notebook.GetCurrentPage().reinit()

class ResultsNotebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        self.mc = parent.mc
        
        self.ResultsTab = ResultsTab(self)
        self.AddPage(self.ResultsTab, "Results")
        
        self.StatisticsTab = StatisticsTab(self)
        self.AddPage(self.StatisticsTab, "Statistics")
        
        self.RankingsTab = RankingsTab(self)
        self.AddPage(self.RankingsTab, "Rankings")
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanging(self, event):
        new = event.GetSelection()
        if new == 0:
            self.ResultsTab.reinit()
        elif new == 1:
            self.StatisticsTab.reinit()
        elif new == 2:
            self.RankingsTab.reinit()
        event.Skip()

class MyGridTable(wx.grid.PyGridTableBase):
    def __init__(self, parent, tbl, grid, mc, *args, **kwargs):
        super(MyGridTable, self).__init__(*args, **kwargs)
        self.parent = parent
        self.tbl = tbl
        self.grid = grid
        self.mc = mc
    
    def GetNumberRows(self):
        return len(self.tbl.row_headers)
    
    def GetNumberCols(self):
        return len(self.tbl.column_headers)
    
    def GetRowLabelValue(self, row):
        if len(self.tbl.rows) > 1 and len(self.tbl.rows[0]) > 0:
            head = self.tbl.row_headers[row]
            if isinstance(head, tuple):
                return head[1]
            else:
                return head
        else:
            return ""
    
    def GetColLabelValue(self, col):
        if len(self.tbl.rows) > 1 and len(self.tbl.rows[0]) > 0:
            head = self.tbl.column_headers[col]
            if isinstance(head, tuple):
                return head[1]
            else:
                return head
        else:
            return ""
    
    def IsEmptyCell(self, row, col):
        """Return True if the cell is empty"""
        try:
            if self.tbl.rows[row][col] != None:
                return False
            else:
                return True
        except IndexError:
            return True
    
    def GetTypeName(self, row, col):
        """Return the name of the data type of the value in the cell"""
        return "floater"
    
    def GetValue(self, row, col):
        if len(self.tbl.rows) > 1 and len(self.tbl.rows[0]) > 0:
            if self.IsEmptyCell(row, col):
                return ""
            else:
                val = self.tbl.rows[row][col]
                try:
                    if val == int(val):
                        val = int(val)
                except:
                    pass
                return val
        else:
            return """To get started, go to the "Players" panel to add your players."""
    
    def GetAttr(self, row, col, param):
        attr = wx.grid.GridCellAttr()
        attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        if row == len(self.tbl.row_headers) - 1 or col == len(self.tbl.column_headers) - 1:
            attr.SetReadOnly(True)
            attr.SetFont(wx.Font(wx.SystemSettings.GetFont(0).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
        return attr
    
    def SetValue(self, row, col, value):
        try:
            val = float(value)
        except ValueError:
            return False
        
        oldval = self.tbl.rows[row][col]
        if val - oldval in [0.5, 1]:
            # New win or draw
            dlg = wx.SingleChoiceDialog(self.parent, "Please select the white player:", "New Match", [self.tbl.row_headers[row][1], self.tbl.column_headers[col][1][4:]])
            if dlg.ShowModal() == wx.ID_OK:
                outcome = None
                if val - oldval == 0.5:
                    newdlg = wx.SingleChoiceDialog(self.parent, "Please select the outcome:", "New Match", ["Stalemate", "Draw"])
                    if newdlg.ShowModal() == wx.ID_OK:
                        outcome = dlg.GetSelection() + 2
                    else:
                        outcome = -1
                if dlg.GetSelection() == 0:
                    white_player_id = self.tbl.row_headers[row][0]
                    black_player_id = self.tbl.column_headers[col][0]
                    if outcome == None:
                        outcome = 0
                else:
                    white_player_id = self.tbl.column_headers[col][0]
                    black_player_id = self.tbl.row_headers[row][0]
                    if outcome == None:
                        outcome = 1
                if outcome == None or outcome == -1:
                    return False
                else:
                    self.mc.add_match(white_player_id, black_player_id, outcome)
                    self.tbl.rows[row][col] = val
                    self.grid.ForceRefresh()
                    return True
            else:
                return False
        else:
            return False

class ResultsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mc = parent.mc
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        #self.reinit()
    
    def reinit(self):
        full_names = True
        if get_pref("last_names"):
            full_names = False
        tbl = self.mc.get_grand_table(full_names=full_names)
        self.sizer.Clear(True)
        
        self.grid = wx.grid.Grid(self)
        self.grid.RegisterDataType("floater", wx.grid.GridCellStringRenderer(), wx.grid.GridCellFloatEditor(2, 1))
        self.sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND, 5)
        self.grid.SetTable(MyGridTable(self, tbl, self.grid, self.mc))
        self.grid.AutoSize()
        
        # Autosize row/column labels
        if len(tbl.rows) > 1 and len(tbl.rows[0]) > 0:
            devContext = wx.ScreenDC()
            devContext.SetFont(self.grid.GetLabelFont())
            
            # First do row labels
            maxWidth = 0
            curRow = self.grid.GetNumberRows() - 1
            while curRow >= 0:
                curWidth = devContext.GetTextExtent("M%s" % (self.grid.GetRowLabelValue(curRow)))[0]
                if curWidth > maxWidth:
                    maxWidth = curWidth
                curRow = curRow - 1
            self.grid.SetRowLabelSize(maxWidth)
            
            # Then column labels
            maxHeight = 0
            curCol = self.grid.GetNumberCols() - 1
            while curCol >= 0:
                (w,h,d,l) = devContext.GetFullTextExtent(self.grid.GetColLabelValue(curCol))
                curHeight = h + d + l + 4
                if curHeight > maxHeight:
                    maxHeight = curHeight
                curCol = curCol - 1
            self.grid.SetColLabelSize(maxHeight)
        
        self.grid.FitInside()
        self.Layout()

class StatisticsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mc = parent.mc
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        #self.reinit()
    
    def reinit(self):
        stats = self.mc.get_stats()
        self.sizer.Clear(True)
        
        self.selector = wx.Choice(self)
        self.selector.Select(self.selector.Append("Overall Statistics"))
        use_last_names = get_pref("last_names")
        for player in self.mc.get_players():
            namer = ""
            if use_last_names:
                namer = player.last_name
            else:
                namer = player.first_name + " " + player.last_name
            self.selector.Append(namer, player.id)
        self.Bind(wx.EVT_CHOICE, self.ChoiceSelect, self.selector)
        self.sizer.Add(self.selector, 0, wx.ALL | wx.EXPAND, 25)
        
        #self.textsizer = wx.BoxSizer(wx.VERTICAL)
        self.textsizer = wx.FlexGridSizer(wx.VERTICAL)
        self.textsizer.SetCols(3)
        
        add_text = lambda text, flags=0: self.textsizer.Add(wx.StaticText(self, label=text), 0, wx.ALL | flags, 3)
        
        add_text("White victory:", wx.ALIGN_RIGHT)
        add_text(str(stats.totals.white_wins))
        add_text("(" + str(int(round(stats.outcomes.white * 100))) + "%)")
        
        add_text("Black victory:", wx.ALIGN_RIGHT)
        add_text(str(stats.totals.black_wins))
        add_text("(" + str(int(round(stats.outcomes.black * 100))) + "%)")
        
        add_text("Stalemate:", wx.ALIGN_RIGHT)
        add_text(str(stats.totals.stalemates))
        add_text("(" + str(int(round(stats.outcomes.stalemate * 100))) + "%)")
        
        add_text("Draw:", wx.ALIGN_RIGHT)
        add_text(str(stats.totals.draws))
        add_text("(" + str(int(round(stats.outcomes.draw * 100))) + "%)")
        
        add_text("Total matches:", wx.ALIGN_RIGHT)
        add_text(str(stats.totals.matches))
        
        self.sizer.Add(self.textsizer, 0, (wx.ALL ^ wx.TOP), 25)
        
        self.Layout()
    
    def ChoiceSelect(self, event):
        sel = self.selector.GetSelection()
        if sel != wx.NOT_FOUND and self.selector.GetClientData(sel):
            player = self.mc.get_players(self.selector.GetClientData(sel))[0]
            self.textsizer.Clear(True)
            if player.stats.total > 0:
                white_wins = float(player.stats.white_wins) / float(player.stats.total)
                white_losses = float(player.stats.white_losses) / float(player.stats.total)
                black_wins = float(player.stats.black_wins) / float(player.stats.total)
                black_losses = float(player.stats.black_losses) / float(player.stats.total)
                stalemates = float(player.stats.stalemates) / float(player.stats.total)
                draws = float(player.stats.draws) / float(player.stats.total)
                
                add_text = lambda text, flags=0: self.textsizer.Add(wx.StaticText(self, label=text), 0, wx.ALL | flags, 3)
                
                add_text("White wins:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.white_wins))
                add_text("(" + str(int(round(white_wins * 100))) + "%)")
                
                add_text("White losses:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.white_losses))
                add_text("(" + str(int(round(white_losses * 100))) + "%)")
                
                add_text(" ")
                add_text(" ")
                add_text(" ")
                
                add_text("Black wins:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.black_wins))
                add_text("(" + str(int(round(black_wins * 100))) + "%)")
                
                add_text("Black losses:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.black_losses))
                add_text("(" + str(int(round(black_losses * 100))) + "%)")
                
                add_text(" ")
                add_text(" ")
                add_text(" ")
                
                add_text("Stalemates:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.stalemates))
                add_text("(" + str(int(round(stalemates * 100))) + "%)")
                
                add_text("Draws:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.draws))
                add_text("(" + str(int(round(draws * 100))) + "%)")
                
                add_text(" ")
                add_text(" ")
                add_text(" ")
                
                add_text("Total matches:", wx.ALIGN_RIGHT)
                add_text(str(player.stats.total))
            else:
                self.textsizer.Add(wx.StaticText(self, label="No matches found for " + player.first_name + " " + player.last_name))
            self.Layout()
        else:
            self.Freeze()
            self.reinit()
            self.Thaw()

class RankingsTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mc = parent.mc
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        #self.reinit()
    
    def reinit(self):
        rankings = self.mc.get_rankings(True)
        self.sizer.Clear(True)
        
        bigsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        if len(rankings) > 0:
            sizer = wx.FlexGridSizer(wx.VERTICAL)
            sizer.SetCols(2)
            use_last_names = get_pref("last_names")
            for index, item in enumerate(rankings):
                player = self.mc.get_players(item[0])[0]
                namer = ""
                if use_last_names:
                    namer = player.last_name
                else:
                    namer = player.first_name + " " + player.last_name
                sizer.Add(wx.StaticText(self, label=str(index + 1) + ": "), 0, wx.ALIGN_RIGHT)
                txt = wx.StaticText(self, label=namer)
                txt.SetToolTip(wx.ToolTip(str(round(item[1], 4))))
                sizer.Add(txt)
            bigsizer.Add(sizer, 1, wx.ALL | wx.EXPAND, 25)
        else:
            bigsizer.Add(wx.StaticText(self, label="You must add at least one player in the \"Players\" panel before viewing rankings."), 1, wx.ALL | wx.EXPAND, 25)
        
        self.sizer.Add(bigsizer)
        self.Layout()


class StartPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.frame = parent
        self.recentDB_buttons = []
        
        bigsizer = wx.BoxSizer(wx.VERTICAL)
        
        if wx.Platform == "__WXMSW__":
            bigtitle = wx.StaticText(self, label="Welcome to MasterChess!", style=wx.ALIGN_CENTER)
            bigtitle.SetFont(wx.Font(36, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
            bigtitle.SetBackgroundColour(wx.Colour(red=220, blue=220, green=255, alpha=160))
            bigsizer.Add(bigtitle, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)
        else:
            bigsizer.Add(wx.StaticBitmap(self, bitmap=wx.Bitmap(get_local_file("MasterChess-small.png"))), 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)
        
        bigsizer.Add(wx.StaticText(self, label=" ", style=wx.ALIGN_CENTER), 0)
        
        if wx.Platform == "__WXMAC__":
            self.ButtonA = wx.lib.buttons.ThemedGenButton(self, label="Create a New Database", style=wx.ALIGN_CENTER)
            self.ButtonB = wx.lib.buttons.ThemedGenButton(self, label="Open an Existing Database", style=wx.ALIGN_CENTER)
        else:
            self.ButtonA = wx.Button(self, label="Create a New Database", style=wx.ALIGN_CENTER)
            self.ButtonB = wx.Button(self, label="Open an Existing Database", style=wx.ALIGN_CENTER)
        self.ButtonA.SetFont(wx.Font(17, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.ButtonB.SetFont(wx.Font(17, wx.SWISS, wx.NORMAL, wx.NORMAL))
        smallsizer = wx.BoxSizer(wx.HORIZONTAL)
        smallsizer.Add(self.ButtonA, 1, wx.ALL | wx.EXPAND, 25)
        smallsizer.Add(self.ButtonB, 1, wx.ALL | wx.EXPAND, 25)
        bigsizer.Add(smallsizer, 1, wx.ALL | wx.EXPAND, 5)
        
        recentDBs = get_recent_databases()
        if len(recentDBs) > 0:
            smallpanel = wx.Panel(self)
            smallpanel.SetBackgroundColour(wx.Colour(red=255, blue=255, green=255, alpha=190))
            smallsizer = wx.BoxSizer(wx.VERTICAL)
            smalltitle = wx.StaticText(smallpanel, label="Recent Databases:", style=wx.ALIGN_LEFT)
            smalltitle.SetFont(wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
            smallsizer.Add(smalltitle, 0, wx.ALL, 5)
            for index, recentDB in enumerate(recentDBs):
                tempbtn = wx.lib.buttons.GenButton(smallpanel, label=recentDB, style=wx.ALIGN_LEFT | wx.BORDER_NONE)
                smallsizer.Add(tempbtn, 0, wx.ALL, 3)
                if index == 0:
                    tempbtn.SetFocus()
                self.recentDB_buttons.append((recentDB, tempbtn))
            
            smallpanel.SetSizer(smallsizer)
            
            bigsizer.Add(smallpanel, 2, wx.ALL | wx.EXPAND, 11)
        
        self.SetSizer(bigsizer)
        self.Layout()
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
    
    def OnEraseBackground(self, event):
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap(get_local_file("chess.jpg"))
        dc.DrawBitmap(bmp, 0, 0)


class MyApp(wx.App):
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)
        
        # This catches events when the app is asked to activate by some other process
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
    
    def OnInit(self):
        if wx.Platform == "__WXMAC__":
            self.SetExitOnFrameDelete(False)
            
            # NOTE: Same menubar spec exists at top!
            menubar = wx.MenuBar()
            
            file_menu = wx.Menu()
            file_new = file_menu.Append(wx.ID_NEW, "&New Database\tCtrl+N", "Create a new chess team database")
            self.Bind(wx.EVT_MENU, self.OnNew, file_new)
            file_open = file_menu.Append(wx.ID_OPEN, "&Open Database\tCtrl+O", "Open an already-created chess team database")
            self.Bind(wx.EVT_MENU, self.OnOpen, file_open)
            file_options = file_menu.Append(wx.ID_PREFERENCES, "&Options", "Set MasterChess options")
            self.Bind(wx.EVT_MENU, self.OnPrefs, file_options)
            file_quit = file_menu.Append(wx.ID_EXIT, "&Exit All\tCtrl+Q", "Close all open MasterChess windows")
            self.Bind(wx.EVT_MENU, self.OnQuit, file_quit)
            menubar.Append(file_menu, "&File")
            
            help_menu = wx.Menu()
            help_email = help_menu.Append(wx.ID_ANY, "&Email Jake Hartz", "Email Jake Hartz with any questions or problems")
            self.Bind(wx.EVT_MENU, self.OnEmail, help_email)
            help_about = help_menu.Append(wx.ID_ABOUT, "&About MasterChess", "Information about MasterChess")
            self.Bind(wx.EVT_MENU, self.OnAbout, help_about)
            menubar.Append(help_menu, "&Help")
            
            wx.MenuBar.MacSetCommonMenuBar(menubar)
        
        something_loaded = False
        for f in sys.argv[1:]:
            frame = MainFrame(auto_load_database=f)
            something_loaded = True
        
        if something_loaded == False:
            MainFrame()
        
        return True
    
    def OnAbout(self, event):
        menu_about()
    
    def OnEmail(self, event):
        menu_email()
    
    def OnQuit(self, event):
        wx.Exit()
    
    def OnPrefs(self, event):
        menu_prefs()
    
    def OnNew(self, event):
        menu_new(self)
    
    def OnOpen(self, event):
        menu_open(self)
    
    def load_database(self, path):
        topwin = self.GetTopWindow()
        if topwin:
            return topwin.load_database(path)
        else:
            MainFrame(auto_load_database=path)
            return True
    
    def BringWindowToFront(self):
        topwin = self.GetTopWindow()
        if topwin:
            topwin.Raise()
        else:
            MainFrame()
    
    def OnActivate(self, event):
        # If this is an activate event, rather than something else, like iconize...
        if event.GetActive():
            self.BringWindowToFront()
        event.Skip()
    
    def OpenFileMessage(self, filename):
        self.load_database(filename)
    
    def MacOpenFile(self, filename):
        # Called for files droped on the dock icon or opened via Finder
        self.load_database(filename)
    
    def MacReopenApp(self):
        # Called when the dock icon is clicked
        self.BringWindowToFront()
    
    def MacNewFile(self):
        pass
    
    def MacPrintFile(self, file_path):
        pass


if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()