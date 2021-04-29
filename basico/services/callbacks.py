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
        # Be aware about when the whole gui is started
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
            time.sleep(0.5)

        if GUI_READY:
            self.emit('gui-started')


    def get_services(self):
        # ~ self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvgui = self.get_service('GUI')
        self.srvuif = self.get_service("UIF")
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvutl = self.get_service('Utils')
        self.srvclt = self.get_service('Collections')
        # ~ self.srvweb = self.get_service('Driver')
        # ~ self.srvbkb = self.get_service('KB4IT')
        self.srvclb = self # Trick
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

        # Memento
        # Working but disabled. Remember size and position.
        # ~ self.memento()

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

    @UIFuncs.hide_popovers
    def display_visor_sapnotes(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_visors('visor-sapnotes')

    @UIFuncs.hide_popovers
    def display_visor_kb(self, *args):
        window = self.srvgui.get_widget('gtk_app_window_main')
        window.show_stack_visors('visor-kb')

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

    ## SAP Notes Visor callbacks ##
    def gui_visor_sapnotes_show_bookmarks(self, *args):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        menuview = self.srvgui.get_widget('menuview')
        button = self.srvgui.get_widget('gtk_togglebutton_bookmarks')

        active = button.get_active()
        if active:
            menuview.populate_by_bookmarks()
            button.set_active(False)

    # ~ def gui_visor_sapnotes_update_sapnotes(self, bag):
        # ~ self.srvsap.download(bag)

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
            time.sleep(0.1)
            statusbar.message(record)
            queue_log.task_done()
        time.sleep(0.1)

    ## KB API
    def kb_import_from_files(self):
        visor_kb = self.srvgui.get_widget('visor_kb')
        parent = self.srvuif.get_window_parent()
        dialog = Gtk.FileChooserDialog(
            "Please choose a file",
            parent,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )
        dialog.set_default_size(800, 400)
        dialog.set_select_multiple(True)
        filter_adoc = Gtk.FileFilter()
        filter_adoc.set_name("Asciidoctor sources")
        filter_adoc.add_pattern("*.adoc")
        dialog.add_filter(filter_adoc)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_files = dialog.get_filenames()
            target = self.srvbkb.get_config_value('sources') or LPATH['DOC_SOURCE']
            for source_file in selected_files:
                shutil.copy(source_file, target)
                self.log.debug("%s copied to %s", os.path.basename(source_file), target)
            self.log.info("Copied %d documents to KB4IT sources directory", len(selected_files))
            self.srvbkb.request_update()
            visor_kb.reload_page()
        elif response == Gtk.ResponseType.CANCEL:
            self.log.warning("Action canceled by user")
        dialog.destroy()

    def kb_import_from_directory(self):
        visor_kb = self.srvgui.get_widget('visor_kb')
        parent = self.srvuif.get_window_parent()
        dialog = Gtk.FileChooserDialog(
            "Please choose a directory",
            parent,
            Gtk.FileChooserAction.CREATE_FOLDER,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )
        dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.set_default_size(800, 400)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_folder = dialog.get_filename()
            self.log.debug("Importing asciidoctor sources from: %s", selected_folder)
            selected_files = glob.glob(os.path.join(selected_folder, '*.adoc'))
            self.log.debug("Found %d asciidoctor files", len(selected_files))
            target = self.srvbkb.get_config_value('sources') or LPATH['DOC_SOURCE']
            for source_file in selected_files:
                shutil.copy(source_file, target)
                self.log.debug("%s copied to %s", os.path.basename(source_file), target)
            self.log.info("Copied %d documents to KB4IT sources directory", len(selected_files))
            self.srvbkb.request_update()
            visor_kb.reload_page()
        elif response == Gtk.ResponseType.CANCEL:
            self.log.warning("Action canceled by user")
        dialog.destroy()
