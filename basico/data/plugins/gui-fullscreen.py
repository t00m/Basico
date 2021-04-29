#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

import basico.core.plg as plugintypes


class PluginBasicoGUIFullscreen(plugintypes.IBasicoGUI):
    def install(self):
        """
        Install Fullscreen toggle button
        """
        self.srvgui = self.app.get_service('GUI')
        self.srvclb = self.app.get_service('Callbacks')
        self.srvicm = self.app.get_service('IM')
        toolbar_widget = self.srvgui.get_widget('visor_sapnotes_toolbar')
        toolbar = toolbar_widget.get_toolbar()

        tool = Gtk.ToolItem()
        tool.set_expand(False)

        icon = self.srvicm.get_new_image_icon('basico-fullscreen', 24, 24)
        box = self.srvgui.add_widget('gtk_box_container_icon_fullscreen', Gtk.Box())
        box.pack_start(icon, False, False, 0)
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('toggled', self.gui_toggle_fullscreen)
        button.add(box)
        tool.add(button)
        tool.set_tooltip_markup('<b>Fullscreen/Window mode</b>')
        tool.show_all()
        toolbar.insert(tool, -1)
        self.log.debug("Plugin fullscreen installed")

        # System button
        box = self.srvgui.get_widget('gtk_popover_box_system_button')

        ### Settings
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-menu-system', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("Settings")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.connect('clicked', self.srvclb.display_settings)
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_settings', button)
        self.srvgui.add_signal('gtk_button_settings', 'clicked', 'self.srvclb.display_settings')
        box.pack_start(button, False, False, 0)

        # Log viewer
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-logviewer', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("Event viewer")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('clicked', self.srvclb.display_log)
        box.pack_end(button, False, False, 0)
        self.srvgui.add_widget('gtk_button_logviewer', button)
        self.srvgui.add_signal('gtk_button_logviewer', 'clicked', 'self.srvclb.display_log')

    def uninstall(self, *args):
        pass

    def gui_toggle_fullscreen(self, button):
        window = self.srvgui.get_window()
        if button.get_active():
            window.fullscreen()
        else:
            window.unfullscreen()
            box = self.srvgui.get_widget('gtk_box_container_icon_fullscreen')
            del(box)

