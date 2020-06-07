#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_logviewer.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Logviewer Widget
"""

from os.path import sep as SEP
from html import escape
import logging
from enum import IntEnum

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from basico.core.mod_log import event_log
from basico.core.mod_wdg import BasicoWidget
from basico.core.mod_env import ROOT, USER_DIR, APP, LPATH, GPATH, FILE

class COLUMN(IntEnum):
    KEY = 0
    ICON = 1
    CHECKBOX = 2


class LogViewer(BasicoWidget, Gtk.Box):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.Box.__init__(self, app)
        self.get_services()
        self.setup()


    def get_services(self):
        """Load services to be used in this class
        """
        self.srvgui = self.get_service("GUI")

    def connect_signals(self, *args):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        statusbar.connect('statusbar-updated', self.update)

    def setup(self):
        visor = Gtk.VBox()
        scr = Gtk.ScrolledWindow()
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        treeview = self.srvgui.add_widget('logviewer_treeview', Gtk.TreeView())
        scr.add(treeview)
        visor.pack_start(scr, True, True, 0)
        visor.show_all()

        # Setup model
        model = Gtk.ListStore(
            str,        # key
            str,        # Icon
            str,        # checkbox
        )
        self.srvgui.add_widget('gtk_model_logviewer', model)

        # Setup columns
        def get_column_header_widget(title, icon_name=None, width=28, height=28):
            hbox = Gtk.HBox()
            # ~ icon = self.srvicm.get_new_image_icon(icon_name, width, height)
            label = Gtk.Label()
            label.set_markup("<b>%s</b>" % title)
            # ~ label.modify_font(Pango.FontDescription('Monospace 10'))
            # ~ hbox.pack_start(icon, False, False, 3)
            hbox.pack_start(label, True, True, 3)
            hbox.show_all()
            return hbox

        # SAP Note key
        renderer = self.srvgui.add_widget('logviewer_renderer_key', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_key', Gtk.TreeViewColumn('Key', renderer, text=COLUMN.KEY))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        treeview.append_column(column)

        # SAP Note key
        renderer = self.srvgui.add_widget('logviewer_renderer_icon', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_key', Gtk.TreeViewColumn('Icon', renderer, text=COLUMN.ICON))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        treeview.append_column(column)

        # SAP Note key
        renderer = self.srvgui.add_widget('logviewer_renderer_checkbox', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_checkbox', Gtk.TreeViewColumn('Checkbox', renderer, text=COLUMN.CHECKBOX))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(True)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        treeview.append_column(column)


    def update(self, *args):
        record = args[1]
        print ("LOGVIEWER: %s" % record.getMessage())

