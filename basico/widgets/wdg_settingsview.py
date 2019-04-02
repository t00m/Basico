#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_settingsview.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Settings Widget
"""

import os
from os.path import sep as SEP
import glob
from html import escape
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from basico.core.mod_wdg import BasicoWidget
from basico.core.mod_env import ROOT, USER_DIR, APP, LPATH, GPATH, FILE

logger = logging.getLogger(__name__)

class SettingsView(BasicoWidget, Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.ScrolledWindow.__init__(self)
        self.get_services()
        self.setup()

    def get_services(self):
        """Load services to be used in this class
        """
        self.srvgui = self.get_service("GUI")
        self.srvbnr = self.get_service('BNR')
        self.srvutl = self.get_service('Utils')
        self.srvant = self.get_service('Annotation')
        self.srvdtb = self.get_service('DB')
        self.srvbnr = self.get_service('BNR')


    def setup(self):
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.IN)
        self.set_hexpand(True)
        self.set_vexpand(True)
        viewport = Gtk.Viewport()
        self.treeview = Gtk.TreeView()
        self.treeview.grab_focus()
        viewport.add(self.treeview)
        self.add(viewport)

        # Setup model
        self.model = Gtk.TreeStore(
            str,        # Primary key: SECTION-KEY-VALUE
            str,        # Key
            str,        # Value
        )

        # Setup columns
        # Primary key: SECTION-KEY-VALUE
        self.renderer_pkey = Gtk.CellRendererText()
        self.column_pkey = Gtk.TreeViewColumn('Primary Key', self.renderer_pkey, text=0)
        self.column_pkey.set_visible(False)
        self.column_pkey.set_expand(False)
        self.column_pkey.set_clickable(False)
        self.column_pkey.set_sort_indicator(False)
        self.treeview.append_column(self.column_pkey)

        # Key
        self.renderer_key = Gtk.CellRendererText()
        self.column_key = Gtk.TreeViewColumn('Key', self.renderer_key, markup=1)
        self.column_key.set_visible(True)
        self.column_key.set_expand(False)
        self.column_key.set_clickable(False)
        self.column_key.set_sort_indicator(False)
        self.treeview.append_column(self.column_key)

        # Value
        self.renderer_value = Gtk.CellRendererText()
        self.column_value = Gtk.TreeViewColumn('Value', self.renderer_value, markup=2)
        self.column_value.set_visible(True)
        self.column_value.set_expand(True)
        self.column_value.set_clickable(False)
        self.column_value.set_sort_indicator(False)
        self.treeview.append_column(self.column_value)

        # TreeView common
        self.sorted_model = Gtk.TreeModelSort(model=self.model)
        self.sorted_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.treeview.set_model(self.sorted_model)
        self.treeview.modify_font(Pango.FontDescription('Monospace 10'))

        self.treeview.set_can_focus(False)
        self.treeview.set_headers_visible(False)
        self.treeview.set_enable_search(True)
        self.treeview.set_hover_selection(False)
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)

        # Selection
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        self.show_all()


    def update(self):
        self.model.clear()
        self.srvstg = self.get_service('Settings')
        config = self.srvstg.load()
        sdict = {}

        # ENVIRONMENT NODE
        root = self.model.append(None, ['root', '<big><b>Environment</b></big>', ''])
        pid = self.model.append(root, ['', '<b>APP</b>', ''])
        for key in APP:
            value = APP[key]
            if isinstance(value, list):
                value = ('\n'.join(value))
            value = escape(value)
            self.model.append(pid, ['APP-%s' % key, '<span color="blue">%s</span>' % key, value])

        pid = self.model.append(root, ['', '<b>LPATH</b>', ''])
        for key in LPATH:
            self.model.append(pid, ['LPATH-%s' % key, '<span color="blue">%s</span>' % key, LPATH[key]])

        pid = self.model.append(root, ['', '<b>GPATH</b>', ''])
        for key in GPATH:
            self.model.append(pid, ['GPATH-%s' % key, '<span color="blue">%s</span>' % key, GPATH[key]])

        pid = self.model.append(root, ['', '<b>FILE</b>', ''])
        for key in FILE:
            self.model.append(pid, ['FILE-%s' % key, '<span color="blue">%s</span>' % key, FILE[key]])

        # SETTINGS NODE
        root = self.model.append(None, ['root', '<big><b>Settings</b></big>', ''])

        def get_pid(key):
            try:
                pid = sdict[key]
            except:
                pid = self.model.append(root, [key, '<b>%s</b>' % key, ''])
                sdict[key] = pid
            return pid

        for skey in config.keys():
            pid = get_pid(skey)
            for key in config[skey]:
                value = str(config[skey][key])
                pkey = '%s-%s-%s' % (skey, key, value)
                self.model.append(pid, [pkey, '<span color="blue">%s</span>' % key, value])


        # WIDGETS NODE
        root = self.model.append(None, ['root', '<big><b>Runtime Objects</b></big>', ''])

        wdgdict = {}
        widgets = self.srvgui.get_widgets()
        for name in widgets:
            objname = escape(str(widgets[name]))
            pobj = gobject = objname[4:objname.find(' ')]
            gobj_left = gobject[:gobject.find('.')]
            gobj_right = gobject[gobject.find('.')+1:]
            pobj = gobject[:gobject.find('.')]
            try:
                ppid_left = wdgdict[gobj_left]
            except:
                ppid_left = self.model.append(root, [gobj_left, '<b>%s</b>' % gobj_left, ''])
                wdgdict[gobj_left] = ppid_left


            try:
                ppid_right = wdgdict[gobj_right]
            except:
                ppid_right = self.model.append(ppid_left, [gobj_right, '<b>%s</b>' % gobj_right, ''])
                wdgdict[gobj_right] = ppid_right

            self.model.append(ppid_right, [gobject, name, objname[4:-4]])


        # STATS NODE
        root = self.model.append(None, ['root', '<big><b>Stats Overview</b></big>', ''])
        s_count = self.srvdtb.get_total()
        a_count = self.srvant.get_total()
        stats = self.srvdtb.get_stats()
        sapnotes_node = self.model.append(root, ['', 'SAP Notes', "%6d" % s_count])
        components_node = self.model.append(sapnotes_node, ['', 'Components', ''])
        for component in stats['maincomp']:
            self.model.append(components_node, [component, component, "%6d" % stats['maincomp'][component]])
        self.model.append(root, ['', 'Annotations', "%6d" % a_count])

