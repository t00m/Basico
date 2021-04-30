#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from gi.repository import Gtk, GObject, Pango

from basico.core.wdg import BasicoWidget
import basico.core.plg as plugintypes


class Clock(BasicoWidget, Gtk.ScrolledWindow):
    """
    Clock class
    """
    def __init__(self, app):
        super().__init__(app, __class__.__name__)

    def _setup_widget(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)
        viewport = Gtk.Viewport()
        widget = Gtk.VBox()
        viewport.add(widget)
        widget.set_hexpand(True)
        widget.set_vexpand(True)

        # Set clock
        self.label = Gtk.Label()
        self.label.modify_font(Pango.FontDescription('Monospace 48'))
        widget.pack_start(self.label, False, False, 6)

        self.add(viewport)
        self.show_all()

        # Start clock
        self.start_clock_timer()


    # Displays Timer
    def update_clock(self, *args):
        #  putting our datetime into a var and setting our label to the result.
        #  we need to return "True" to ensure the timer continues to run, otherwise it will only run once.
        datetimenow = str(datetime.now())
        self.label.set_label(datetimenow)
        return True

    # Initialize Timer
    def start_clock_timer(self):
        GObject.timeout_add(1000, self.update_clock)


class PluginBasicoGUIClock(plugintypes.IBasicoGUI):
    def install(self):
        """
        Install Fullscreen toggle button
        """
        self.srvgui = self.app.get_service('GUI')
        self.srvicm = self.app.get_service('IM')

        stack_system = self.srvgui.get_widget('gtk_stack_system')
        self.log.debug(stack_system)
        stack_child = self.setup_stack_system_clock()
        stack_system.add_titled(stack_child, "clock", "Clock")
        stack_system.child_set_property (stack_child, "icon-name", "basico-about")

        self.box = Gtk.Box(spacing=6)

        self.label = Gtk.Label()
        self.box.pack_start(self.label, True, True, 0)

        window = self.srvgui.get_window()
        window.show_stack_system('clock')

    def setup_stack_system_clock(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        about = self.srvgui.add_widget('widget_clock', Clock(self.app))
        box.pack_start(about, True, True, 0)
        box.show_all()
        return box

    def uninstall(self, *args):
        pass




