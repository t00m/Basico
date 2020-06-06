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
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from basico.core.mod_log import event_log
from basico.core.mod_wdg import BasicoWidget
from basico.core.mod_env import ROOT, USER_DIR, APP, LPATH, GPATH, FILE


class LogViewer(BasicoWidget, Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.ScrolledWindow.__init__(self)
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
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.IN)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.logviewer = self.srvgui.add_widget('gtk_textview_logviewer', Gtk.TextView())
        self.logviewer.set_wrap_mode(Gtk.WrapMode.NONE)
        self.logviewer.modify_font(Pango.FontDescription('Monospace 10'))
        buffer_logviewer = self.logviewer.get_buffer()
        self.add(self.logviewer)
        self.show_all()


    def update(self, *args):
        record = args[1]
        print ("LOGVIEWER: %s" % record.getMessage())

