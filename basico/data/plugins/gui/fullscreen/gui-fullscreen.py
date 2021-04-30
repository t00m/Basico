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
        self.srvicm = self.app.get_service('IM')        
        self.rhbox = self.srvgui.get_widget('gtk_hbox_hb_right')
        icon = self.srvicm.get_new_image_icon('basico-fullscreen', 24, 24)
        box = self.srvgui.add_widget('gtk_box_container_icon_fullscreen', Gtk.Box())
        box.pack_start(icon, False, False, 0)
        self.button = Gtk.Button()
        self.button.set_relief(Gtk.ReliefStyle.NONE)
        self.button.connect('clicked', self.do_fullscreen)
        self.button.add(box)
        self.button.show_all()
        self.rhbox.pack_end(self.button, False, False, 0)
        window = self.srvgui.get_window()
        window.connect('window-keypress-event', self.evaluate_keypress)
        self.log.debug("Plugin fullscreen installed")

    def uninstall(self, *args):
        pass

    def do_fullscreen(self, button):
        window = self.srvgui.get_window()
        window.fullscreen()
    
    def evaluate_keypress(self, window, key):
        self.log.debug("Main window received the key '%s'", key)
        if key == 'Escape':
            window.unfullscreen()
        elif key == 'F11':
            window.fullscreen()
            
        



