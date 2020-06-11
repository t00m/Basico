#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_cb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: UI and related callbacks service
"""

import os
import json
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from basico.core.mod_srv import Service
from basico.core.mod_log import event_log, queue_log
from basico.core.mod_env import FILE, LPATH, ATYPES, APP
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_settingsview import SettingsView
from basico.services.srv_uif import UIFuncs

MAX_WORKERS = 1 # Number of simultaneous connections

# def naming rule: <service>_<widget>_<action>

class Callback(Service):
    def initialize(self):
        self.get_services()
        self.connect_signals()

    def get_services(self):
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvgui = self.get_service('GUI')
        self.srvuif = self.get_service("UIF")
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvutl = self.get_service('Utils')
        self.srvclt = self.get_service('Collections')
        self.srvweb = self.get_service('Driver')
        # ~ self.srvant = self.get_service('Annotation')
        # ~ self.srvbnr = self.get_service('BNR')
        # ~ self.srvatc = self.get_service('Attachment')

    def connect_signals(self, *args):
        # ~ uiapp = self.srvgui.get_uiapp()
        # ~ uiapp.connect('gui-started', self.gui_started)
        # ~ self.srvgui.connect('gui-update', self.gui_update)
        # ~ logviewer = self.srvgui.get_widget('logviewer')
        # ~ statusbar = self.srvgui.get_widget('widget_statusbar')
        # ~ statusbar.connect('statusbar-updated', logviewer.update)
        pass

    def gui_started(self, *args):
        self.log.debug("GUI started")

    @UIFuncs.hide_popovers
    def display_dashboard(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack('dashboard')

    @UIFuncs.hide_popovers
    def display_about(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack('about')

    @UIFuncs.hide_popovers
    def display_log(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack('log')

    @UIFuncs.hide_popovers
    def display_settings(self, *args):
        view_settings = self.srvgui.get_widget('widget_settings')
        view_settings.update()
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack('settings')

    @UIFuncs.hide_popovers
    def display_help(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack('help')

    def gui_menuview_update(self, *args):
        view = args[1]
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        menuview = self.srvgui.get_widget('menuview')
        if view is None:
            view = menuview.get_view()

        if view is not None:
            viewlabel = self.srvgui.get_widget('gtk_label_current_view')
            name = "<b>%-10s</b>" % view.capitalize()
            viewlabel.set_markup(name)

        popover = self.srvgui.get_widget('gtk_popover_button_menu_views')
        popover.hide()
        menuview.set_view(view)
        visor_sapnotes.display()

    def gui_update(self, *args):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        # ~ menuview = self.srvgui.get_widget('menuview')
        # ~ view = menuview.get_view()
        # ~ menuview.set_view(view)
        # ~ menuview.select_first_entry()
        visor_sapnotes.update()
        self.gui_statusbar_update()

    def gui_statusbar_update(self, *args):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        alive = statusbar is not None
        while alive:
            record = queue_log.get()
            time.sleep(0.25)
            statusbar.message(record)
            queue_log.task_done()
        time.sleep(0.25)
