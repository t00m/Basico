#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_statusbar.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Statusbar Widget
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

from basico.core.mod_env import ROOT, USER_DIR, APP, LPATH, GPATH, FILE
from basico.core.mod_wdg import BasicoWidget
from basico.core.mod_log import event_log

class Statusbar(BasicoWidget, Gtk.HBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.HBox.__init__(self)
        GObject.signal_new('statusbar-updated', Statusbar, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        self.get_services()
        self.setup()
        self.connect('realize', self.alive)


    def alive(self, *args):
        logviewer = self.srvgui.get_widget('widget_logviewer')
        logviewer.connect_signals()

    def setup(self):
        vbox = Gtk.VBox()
        viewport = Gtk.Viewport()
        viewport.set_shadow_type(Gtk.ShadowType.NONE)
        hbox = Gtk.HBox()
        viewport.add(hbox)
        separator = Gtk.Separator()

        # PRIORITY
        label_priority = self.srvgui.add_widget('statusbar_label_priority', Gtk.Label())
        label_priority.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        label_priority.set_property('selectable', True)
        label_priority.set_property('margin-left', 6)
        label_priority.set_property('margin-right', 6)
        label_priority.set_property('margin-top', 0)
        label_priority.set_property('margin-bottom', 6)
        label_priority.set_width_chars(8)
        label_priority.set_xalign(0.0)
        label_priority.modify_font(Pango.FontDescription('Monospace 10'))
        hbox.pack_start(label_priority, False, False, 3)

        # MESSAGE
        label_message = self.srvgui.add_widget('statusbar_label_message', Gtk.Label())
        label_message.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        label_message.set_property('selectable', True)
        label_message.set_property('margin-left', 6)
        label_message.set_property('margin-right', 6)
        label_message.set_property('margin-top', 0)
        label_message.set_property('margin-bottom', 6)
        label_message.set_xalign(0.0)
        label_message.modify_font(Pango.FontDescription('Monospace 10'))
        hbox.pack_start(label_message, True, True, 3)

        # CANCEL BUTTON
        button = Gtk.Button()
        icon = self.srvicm.get_pixbuf_icon('basico-check-cancel', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('statusbar_button_cancel', button)
        button.connect('clicked', self.srvweb.cancel_by_user)
        hbox.pack_end(button, False, False, 0)

        # SPINNER
        spinner = self.srvgui.add_widget('statusbar_spinner', Gtk.Spinner())
        spinner.show_all()
        hbox.pack_start(spinner, False, False, 3)

        # ~ vbox.pack_start(separator, True, False, 0)
        vbox.pack_start(viewport, True, False, 0)
        self.add(vbox)

    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvicm = self.get_service("IM")
        self.srvweb = self.get_service("Driver")

    def message(self, record):
        # Display messages with priority INFO|WARNING|ERROR|CRITICAL
        if record.levelno > 10:
            label_message = self.srvgui.get_widget('statusbar_label_message')
            label_priority = self.srvgui.get_widget('statusbar_label_priority')
            priority = record.levelname
            message = record.getMessage()
            label_message.set_markup(message)
            label_priority.set_markup("<b>%s</b>" % priority)

        # Emit signal for logviewer
        self.emit('statusbar-updated', record)


