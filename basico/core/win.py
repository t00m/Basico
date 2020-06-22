#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_win.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Gtk.ApplicationWindow implementation
"""

import os
import sys
import stat
import time
import logging
import platform

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from basico.core.wdg import BasicoWidget
from basico.core.srv import Service
from basico.core.env import APP, FILE
from basico.widgets.visor_sapnotes import SAPNotesVisor
from basico.widgets.about import About
from basico.widgets.settingsview import SettingsView
from basico.widgets.logviewer import LogViewer
from basico.widgets.statusbar import Statusbar
from basico.widgets.browser import BasicoBrowser
from basico.widgets.kb import KBWidget


class GtkAppWindow(BasicoWidget, Gtk.ApplicationWindow):
    size_pos = None

    def __init__(self, uiapp):
        self.uiapp = uiapp
        self.setup_controller(uiapp)
        self.app = uiapp.get_controller()
        super().__init__(self.app, __class__.__name__)

    def _setup_widget(self):
        self.size_pos = self.get_size_pos_from_config()
        if self.size_pos is None:
            self.log.debug("No last size and position saved. First time execution?")

        self.setup_window(self.uiapp)
        self.setup_widgets()
        self.srvgui.add_widget('gtk_app_window', self)
        self.run()

    def get_size_pos_from_config(self):
        return self.get_config_value('size_pos')

    def get_last_size_pos(self):
        return self.size_pos

    def set_last_size_pos(self, size_pos):
        self.size_pos = size_pos

    def get_services(self):
        self.srvicm = self.controller.get_service('IM')
        self.srvclb = self.controller.get_service('Callbacks')

    def setup_controller(self, uiapp):
        self.controller = uiapp.get_controller()

    def get_signal(self, signal):
        return self.signals[key]


    def setup_window(self, uiapp):
        Gtk.Window.__init__(self, title=APP['name'], application=uiapp)
        icon = self.srvicm.get_icon('basico-component', 36, 36)
        self.set_icon(icon)
        """
        Change Gtk+ Style
        """
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        # ~ css_provider.load_from_path(FILE['CSS'])
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.set_default_size(1024, 728)
        self.setup_headerbar()
        self.show_all()

    def setup_headerbar(self):
        hb = self.srvgui.add_widget('gtk_headerbar_container', Gtk.HeaderBar())
        hb.set_show_close_button(True)
        hb.props.title = "Basico"
        hb.props.subtitle = "SAP Notes Manager for SAP Consultants"
        lhbox = self.setup_headerbar_left(hb)
        hb.pack_start(lhbox)
        rhbox = self.setup_headerbar_right(hb)
        hb.pack_end(rhbox)
        self.set_titlebar(hb)
        hb.show_all()

    def setup_headerbar_left(self, hb):
        lhbox = self.srvgui.add_widget('gtk_hbox_hb_left', Gtk.HBox())

        ## Visor SAP Notes
        button = Gtk.Button()
        icon = self.srvicm.get_pixbuf_icon('basico-dashboard', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_visor_sapnotes', button)
        self.srvgui.add_signal('gtk_button_visor_sapnotes', 'clicked', 'self.srvclb.display_visor_sapnotes')
        lhbox.pack_start(button, False, False, 0)

        ## Visor KB
        button = Gtk.Button()
        icon = self.srvicm.get_pixbuf_icon('basico-annotation', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_visor_kb', button)
        self.srvgui.add_signal('gtk_button_visor_kb', 'clicked', 'self.srvclb.display_visor_kb')
        lhbox.pack_start(button, False, False, 0)

        return lhbox

    def setup_headerbar_right(self, hb):
        rhbox = Gtk.HBox()

        ## System Menu
        button = Gtk.Button()
        icon = self.srvicm.get_pixbuf_icon('basico-menu-system', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NONE)
        popover = Gtk.Popover.new(button)
        self.srvgui.add_widget('gtk_popover_button_menu_system', popover)
        self.srvgui.add_widget('gtk_button_menu_system', button)
        self.srvgui.add_signal('gtk_button_menu_system', 'clicked', 'self.srvuif.popover_show', popover)
        rhbox.pack_end(button, False, False, 0)

        # Popover body
        box = Gtk.Box(spacing = 0, orientation="vertical")
        popover.add(box)

        ### About
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-about', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("About")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_about', button)
        self.srvgui.add_signal('gtk_button_about', 'clicked', 'self.srvclb.display_about')
        box.pack_end(button, False, False, 0)

        ### Help
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-help', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("Help")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_help', button)
        self.srvgui.add_signal('gtk_button_help', 'clicked', 'self.srvclb.display_help')
        box.pack_end(button, False, False, 0)

        ### Log viewer
        # ~ # Disabled temporary
        # ~ hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        # ~ icon = self.srvicm.get_pixbuf_icon('basico-logviewer', 24, 24)
        # ~ image = Gtk.Image()
        # ~ image.set_from_pixbuf(icon)
        # ~ label = Gtk.Label("Event viewer")
        # ~ hbox.pack_start(image, False, False, 3)
        # ~ hbox.pack_start(label, False, False, 3)
        # ~ button = Gtk.Button()
        # ~ button.add(hbox)
        # ~ button.set_relief(Gtk.ReliefStyle.NONE)
        # ~ box.pack_end(button, False, False, 0)
        # ~ self.srvgui.add_widget('gtk_button_logviewer', button)
        # ~ self.srvgui.add_signal('gtk_button_logviewer', 'clicked', 'self.srvclb.display_log')

        ### Settings
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-settings', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("Settings")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_settings', button)
        self.srvgui.add_signal('gtk_button_settings', 'clicked', 'self.srvclb.display_settings')
        box.pack_start(button, False, False, 0)

        return rhbox

    def setup_widgets(self):
        # Main box
        mainbox = self.srvgui.add_widget('gtk_vbox_container_main', Gtk.VBox())
        mainbox.set_homogeneous(False)
        mainbox.set_hexpand(True)

        # Notebook
        notebook = self.srvgui.add_widget('gtk_notebook_main', Gtk.Notebook())
        notebook.set_show_tabs(False)
        page_visors = self.setup_stack_visors()
        page_system = self.setup_stack_system()
        notebook.append_page(page_visors, Gtk.Label("Visors"))
        notebook.append_page(page_system, Gtk.Label("System"))
        mainbox.pack_start(notebook, True, True, 0)

        # Statusbar
        statusbar = self.srvgui.add_widget('widget_statusbar', Statusbar(self.controller))
        mainbox.pack_start(statusbar, False, False, 0)

        self.add(mainbox)
        self.show_all()

    def switch_notebook_page(self, page_num):
        notebook = self.srvgui.get_widget('gtk_notebook_main')
        notebook.set_current_page(page_num)

    def show_stack_system(self, stack_name):
        self.switch_notebook_page(1)
        stack_system = self.srvgui.get_widget('gtk_stack_system')
        stack_system.set_visible_child_name(stack_name)
        self.log.debug("Displaying system %s", stack_name)

    def show_stack_visors(self, stack_name):
        self.switch_notebook_page(0)
        stack_visors = self.srvgui.get_widget('gtk_stack_visors')
        stack_visors.set_visible_child_name(stack_name)
        self.log.debug("Displaying visor %s", stack_name)

    def setup_stack_system(self):
        lhbox = self.srvgui.get_widget('gtk_hbox_hb_left')

        # System Stack (Settings / Help / etc...)
        stack_system = self.srvgui.add_widget('gtk_stack_system', Gtk.Stack())
        stack_system.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack_system.set_transition_duration(250)

        ### Settings stack child
        stack_child = self.setup_stack_system_settings()
        stack_system.add_titled(stack_child, "settings", "Basico Settings")
        stack_system.child_set_property (stack_child, "icon-name", "basico-settings")

        ### Help stack child
        stack_child = self.setup_stack_system_help()
        stack_system.add_titled(stack_child, "help", "Basico Help")
        stack_system.child_set_property (stack_child, "icon-name", "basico-help")

        # ~ ### About stack child
        stack_child = self.setup_stack_system_about()
        stack_system.add_titled(stack_child, "about", "About Basico")
        stack_system.child_set_property (stack_child, "icon-name", "basico-about")

        ### Log stack child
        stack_child = self.setup_stack_system_log()
        stack_system.add_titled(stack_child, "log", "Event Viewer")

        stack_system.show_all()
        return stack_system

    def setup_stack_visors(self):
        box = Gtk.VBox()
        box.set_hexpand(True)

        ### Stack for visors
        stack_visors = self.srvgui.add_widget('gtk_stack_visors', Gtk.Stack())
        stack_visors.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack_visors.set_transition_duration(250)
        box.pack_start(stack_visors, True, True, 0)

        #### Stack for Visor SAP Notes
        stack_child = self.setup_stack_visor_sapnotes()
        stack_visors.add_titled(stack_child, "visor-sapnotes", "SAP Notes")
        stack_visors.child_set_property (stack_child, "icon-name", "basico-sapnote")

        #### Stack for Visor KB
        stack_child = self.setup_stack_visor_kb()
        stack_visors.add_titled(stack_child, "visor-kb", "Basico KB")
        stack_visors.child_set_property (stack_child, "icon-name", "basico-annotation")

        return box

    def setup_stack_visor_sapnotes(self):
        box = Gtk.VBox()
        box.set_hexpand(True)

        ### Visor
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        visor_sapnotes = self.srvgui.add_widget('visor_sapnotes', SAPNotesVisor(self.controller))
        visor_sapnotes.set_hexpand(True)
        visor_sapnotes.set_vexpand(True)
        vwp.add(visor_sapnotes)
        scr.add(vwp)
        box.pack_start(scr, True, True, 0)
        visor_sapnotes.show_all()
        box.show_all()
        return box

    def setup_stack_visor_kb(self):
        ### KB Visor and Editor
        return KBWidget(self.controller)

    def setup_stack_system_about(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        about = self.srvgui.add_widget('widget_about', About(self.controller))
        box.pack_start(about, True, True, 0)
        box.show_all()
        return box

    def setup_stack_system_settings(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        settings = self.srvgui.add_widget('widget_settings', SettingsView(self.controller))
        box.pack_start(settings, True, True, 0)
        box.show_all()
        return box

    def setup_stack_system_log(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        logviewer = self.srvgui.add_widget('widget_logviewer', LogViewer(self.controller))
        box.pack_start(logviewer, True, True, 0)
        box.show_all()
        return box

    def setup_stack_system_help(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        browser = BasicoBrowser(self.controller)
        self.log.debug(FILE['HELP_INDEX'])
        help_page = "file://%s" % FILE['HELP_INDEX']
        browser.load_url(help_page)
        self.log.debug("Loading help page: %s", help_page)
        box.pack_start(browser, True, True, 0)
        box.show_all()
        return box

    def run(self):
        menuview = self.srvgui.get_widget('menuview')
        # Get from settings last view and row used from config
        try:
            view = menuview.get_config_value('view')
        except:
            view = None

        try:
            path = menuview.get_config_value('path')
        except:
            path = 0

        self.log.debug("Displaying path %s for view %s   ", path, view)
        menuview.set_view(view)
        menuview.select_row(path)
        self.show_stack_visors('visor-sapnotes')
