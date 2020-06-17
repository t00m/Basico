#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_cb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: UI and related callbacks service
"""

import time
import threading

from gi.repository import GObject

from basico.core.srv import Service
from basico.core.log import queue_log
from basico.services.uif import UIFuncs
from basico.services.kb4it import KBStatus


class Callback(Service):
    """
    Callbacks service is in charge of setup all the gui aspects once it
    has started
    """
    def initialize(self):
        # Be aware about when the whole gui is started
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
        self.srvclb = self # Trick
        self.srvbkb.connect('kb-updated', self.kb_updated)
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

        # Alive
        self.srvgui.set_running(True)
        self.log.debug("Signals connected")
        self.log.debug("Basico ready!")

        # Memento
        self.memento()

    def memento(self):
        # Remember last window size
        try:
            appwindow = self.srvgui.get_widget('gtk_app_window')
            appwindow.connect('configure-event', self.gui_appwindow_changed)
            width, height, x, y = appwindow.get_last_size_pos()
            appwindow.set_size_request(width, height)
        except:
            self.log.warning("Window couldn't be resized")


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

    ## GTK APP WINDOW ##
    def gui_appwindow_changed(self, widget, e):
        """
        Save some gui aspects like w, h, x, y
        FIXME: when the window is maximized and then back to normal, the
               window can't be resized :/
        """
        widget.set_config_value('size_pos', (e.width, e.height, e.x, e.y))
        return False

    @UIFuncs.hide_popovers
    def display_visor_sapnotes(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_visors('visor-sapnotes')

    @UIFuncs.hide_popovers
    def display_visor_annotations(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_visors('visor-annotations')

    @UIFuncs.hide_popovers
    def display_about(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_system('about')

    @UIFuncs.hide_popovers
    def display_log(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_system('log')

    @UIFuncs.hide_popovers
    def display_settings(self, *args):
        view_settings = self.srvgui.get_widget('widget_settings')
        view_settings.update()
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_system('settings')

    @UIFuncs.hide_popovers
    def display_help(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_system('help')

    ## Menuview callabacks ##
    def gui_menuview_toggled(self, *args):
        """Show/Hide menu views"""
        button = self.srvgui.get_widget('gtk_togglebutton_toolbar_menuview')
        menuview_container = self.srvgui.get_widget('gtk_vbox_container_menu_view')
        toggled = button.get_active()
        if toggled:
            menuview_container.set_no_show_all(False)
            menuview_container.show_all()
        else:
            menuview_container.hide()
            menuview_container.set_no_show_all(True)

    def gui_menuview_update(self, *args):
        """Update visor sapnotes when view changes"""
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

    def gui_menuview_row_changed(self, *args):
        """
        Update visor sapnotes when user choose a different row in the
        treeview associated to that view
        """
        menuview = self.srvgui.get_widget('menuview')
        menuview.row_changed()

    ## VISOR SAP NOTES ##
    def gui_annotation_create(self, button, sid):
        self.log.warning("Functionality not implemented yet: Creating annotation for SAP Note %s", sid)

    ## STATUSBAR ##
    def gui_statusbar_update(self, *args):
        """Update statusbar by using intercepted logging"""
        statusbar = self.srvgui.get_widget('widget_statusbar')
        alive = statusbar is not None
        while alive:
            record = queue_log.get()
            time.sleep(0.25)
            statusbar.message(record)
            queue_log.task_done()
        time.sleep(0.1)

    def kb_updated(self, *args):
        """Be aware when Basico KB is updated"""
        self.log.info("Basico KB updated")
