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
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from basico.core.srv import Service
from basico.core.log import event_log, queue_log
from basico.core.env import FILE, LPATH, ATYPES, APP
from basico.widgets.cols import CollectionsMgtView
from basico.widgets.settingsview import SettingsView
from basico.services.uif import UIFuncs
from basico.services.kb4it import KBStatus

class Callback(Service):
    def initialize(self):
        GObject.signal_new('gui-started', Callback, GObject.SignalFlags.RUN_LAST, None, () )
        self.connect('gui-started', self.gui_started)
        self.get_services()
        self.th = threading.Thread(name='startup', target=self.on_startup)
        self.th.setDaemon(True)
        self.th.start()

    def on_startup(self, *args):
        """
        Awesome way :( to know when all widgets are ready to work...
        It waits until statusbar widget is loaded and then emit
        the signal 'gui-started'...
        """
        GUI_READY = False
        while not GUI_READY:
            try:
                statusbar = self.srvgui.get_widget('widget_statusbar')
                if statusbar is not None:
                    GUI_READY = True
                    break
            except Exception as error:
                self.log.debug(error)
                GUI_READY = False
            time.sleep(0.5)

        if GUI_READY:
            self.emit('gui-started')


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
        self.srvbkb = self.get_service('KB4IT')
        self.srvbkb.connect('kb-updated', self.kb_updated)

    def gui_started(self, *args):
        # Update statusbar and logviewer
        statusbar = self.srvgui.get_widget('widget_statusbar')
        statusbar.alive()
        self.th = threading.Thread(name='statusbar', target=self.gui_statusbar_update)
        self.th.setDaemon(True)
        self.th.start()
        self.log.debug("Logging activated")

        # Connect signals
        self.connect_signals()
        self.log.debug("Signals connected")

        self.log.debug("Basico ready!")

    def connect_signals(self):
        wsdict = self.srvgui.get_signals()
        for widget in wsdict:
            for signal in wsdict[widget]:
                callback, data = wsdict[widget][signal]
                self.srvuif.connect_signal(widget, signal, callback, data)

        # ~ self.srvuif.connect_signal('gtk_button_logviewer', 'clicked', self.display_log)

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

    def gui_statusbar_update(self, *args):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        alive = statusbar is not None
        while alive:
            record = queue_log.get()
            time.sleep(0.25)
            statusbar.message(record)
            queue_log.task_done()
        time.sleep(0.1)

    def kb_updated(self, *args):
        self.log.info("Basico KB updated")
