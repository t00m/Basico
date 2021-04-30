#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_cb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: UI and related callbacks service
"""

import os
import glob
import time
import shutil
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject

from basico.core.env import LPATH
from basico.core.srv import Service
from basico.core.log import queue_log
from basico.services.uif import UIFuncs

class Callback(Service):
    """
    Callbacks service is in charge of setup all the gui aspects once it
    has started
    """
    def initialize(self):
        # Be aware about when the whole GUI is started
        GObject.signal_new('gui-started', Callback, GObject.SignalFlags.RUN_LAST, None, () )
        self.connect('gui-started', self.gui_started)
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
            time.sleep(1)

        if GUI_READY:
            self.emit('gui-started')

    def get_services(self):
        self.srvgui = self.get_service('GUI')
        self.srvuif = self.get_service("UIF")
        self.srvgui.connect('new-signal', self.connect_signal)

    def gui_started(self, *args):
        # Update statusbar and logviewer
        statusbar = self.srvgui.get_widget('widget_statusbar')
        statusbar.alive()
        self.th = threading.Thread(name='statusbar', target=self.gui_statusbar_update)
        self.th.setDaemon(True)
        self.th.start()
        self.log.debug("UI Logging activated")

        # Connect signals
        self.connect_signals()

        # Execute GUI plugins
        plugins = self.get_service('Plugins')
        plugins.run(category='GUI')

        # Alive
        self.srvgui.set_running(True)
        self.log.debug("Signals connected")
        self.log.debug("Basico ready!")

    def connect_signals(self):
        """Auto connect all those signals registered for widgets"""
        wsdict = self.srvgui.get_signals()
        for widget in wsdict:
            for signal in wsdict[widget]:
                callback, data = wsdict[widget][signal]
                self.srvuif.connect_signal(widget, signal, callback, data)

    def connect_signal(self, *args):
        """
        Connect those signals emitted once the gui is started and after
        the auto connect signlas has been fired
        """
        widget, signal, callback, data = args[1]
        self.srvuif.connect_signal(widget, signal, callback, data)
        self.log.debug("Connected signal '%s' to widget '%s' with callback '%s'", signal, widget, callback)

    ## GTK APP WINDOW ##
    def gui_appwindow_changed(self, widget, e):
        """
        Save some gui aspects like width, height, x, y
        Currently only width and height are taken into account
        """
        cur_size_pos = widget.get_last_size_pos()
        new_size_pos = (e.width, e.height, e.x, e.y)
        if new_size_pos != cur_size_pos:
            widget.set_last_size_pos(new_size_pos)
            widget.set_config_value('size_pos', (e.width, e.height, e.x, e.y))
        return False

    # ~ @UIFuncs.hide_popovers
    # ~ def display_about(self, *args):
        # ~ window = self.srvgui.get_widget('gtk_app_window_main')
        # ~ window.show_stack_system('about')

    ## STATUSBAR ##
    def gui_statusbar_update(self, *args):
        """Update statusbar by using intercepted logging"""
        statusbar = self.srvgui.get_widget('widget_statusbar')
        alive = statusbar is not None
        while alive:
            record = queue_log.get()
            time.sleep(0.1)
            statusbar.message(record)
            queue_log.task_done()
        time.sleep(0.1)
