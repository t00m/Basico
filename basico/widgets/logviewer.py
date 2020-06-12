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
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from basico.core.log import event_log
from basico.core.wdg import BasicoWidget
from basico.core.env import ROOT, USER_DIR, APP, LPATH, GPATH, FILE

class COLUMN(IntEnum):
    LEVELNO = 0
    LEVELNAME = 1
    MODULE = 2
    TS_SECONDS = 3
    TS_HUMAN = 4
    MESSAGE = 5


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
        self.add(visor)


        # Setup model
        model = Gtk.ListStore(
            int,        # level number
            str,        # level name
            str,        # module
            int,        # timestamp seconds
            str,        # timestamp human
            str,        # message
        )
        self.srvgui.add_widget('gtk_model_logviewer', model)

        # Setup columns
        def get_column_header_widget(title, icon_name=None, width=28, height=28):
            hbox = Gtk.HBox()
            label = Gtk.Label()
            label.set_markup("<b>%s</b>" % title)
            hbox.pack_start(label, True, True, 3)
            hbox.show_all()
            return hbox

        # Level No.
        renderer = self.srvgui.add_widget('logviewer_renderer_levelno', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_levelno', Gtk.TreeViewColumn('Level No.', renderer, text=COLUMN.LEVELNO))
        renderer.set_property('height', 32)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        treeview.append_column(column)

        # Level Name
        renderer = self.srvgui.add_widget('logviewer_renderer_levelname', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_levelname', Gtk.TreeViewColumn('Level', renderer, text=COLUMN.LEVELNAME))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        column.set_cell_data_func(renderer, self.change_color)
        treeview.append_column(column)

        # Module
        renderer = self.srvgui.add_widget('logviewer_renderer_module', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_module', Gtk.TreeViewColumn('Module', renderer, text=COLUMN.MODULE))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        column.set_cell_data_func(renderer, self.change_color)
        treeview.append_column(column)

        # Timestamp seconds
        renderer = self.srvgui.add_widget('logviewer_renderer_ts_seconds', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_ts_seconds', Gtk.TreeViewColumn('Timestamp', renderer, text=COLUMN.TS_SECONDS))
        renderer.set_property('height', 32)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        treeview.append_column(column)

        # Timestamp human
        renderer = self.srvgui.add_widget('logviewer_renderer_ts_human', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_ts_human', Gtk.TreeViewColumn('Timestamp', renderer, text=COLUMN.TS_HUMAN))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        column.set_cell_data_func(renderer, self.change_color)
        treeview.append_column(column)

        # Message
        renderer = self.srvgui.add_widget('logviewer_renderer_message', Gtk.CellRendererText())
        column = self.srvgui.add_widget('logviewer_column_message', Gtk.TreeViewColumn('Message', renderer, markup=COLUMN.MESSAGE))
        renderer.set_property('height', 32)
        column.set_visible(True)
        column.set_expand(True)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        column.set_cell_data_func(renderer, self.change_color)
        treeview.append_column(column)
        self.column_message = column

        selection = treeview.get_selection()
        self.srvgui.add_widget('logviewer_selection', selection)
        selection.set_mode(Gtk.SelectionMode.SINGLE)

        treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        treeview.set_enable_tree_lines(True)
        treeview.modify_font(Pango.FontDescription('Monospace 10'))
        treeview.set_model(model)
        self.show_all()

    def change_color(self, column, renderer, model, riter, data):
        levelno = model.get(riter, 0)[0]
        if levelno == 10:
            renderer.set_property('background', 'lightgray')
        elif levelno == 20:
            renderer.set_property('background', 'lightgreen')
        elif levelno == 30:
            renderer.set_property('background', 'orange')
        elif levelno == 40:
            renderer.set_property('background', 'red')
        elif levelno == 40:
            renderer.set_property('background', 'purple')


    def update(self, *args):
        treeview = self.srvgui.get_widget('logviewer_treeview')
        model = self.srvgui.get_widget('gtk_model_logviewer')
        selection = self.srvgui.get_widget('logviewer_selection')
        record = args[1]

        def insert(record):
            levelno = record.levelno
            levelname = record.levelname
            module = record.module
            tss = record.created
            tsh = record.asctime
            message = record.getMessage()
            riter = model.insert(0, (levelno, levelname, module, tss, tsh, message))
            selection.select_iter(riter)
            treeview.scroll_to_cell(0, self.column_message)

        GLib.idle_add(insert, record)
