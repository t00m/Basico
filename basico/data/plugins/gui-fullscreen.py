#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

# Interfaces

import basico.core.plg as plugintypes

class PluginBasicoGUIFullscreen(plugintypes.IBasicoGUI):
    def init(self, app):
        self.app = app        
        self.log.debug("%s => %s", __class__.__name__, app)
        self.log.debug(self.app.get_services())

    # ~ def run(self, *args):
        # ~ self.log.debug("This is a plugin for Basico GUI with args %s", args)        
        # ~ self.install()
        
    def install(self, *args):        
        """
        Install Fullscreen toggle button
        """
        self.srvgui = self.app.get_service('GUI')
        toolbar_widget = self.srvgui.get_widget('visor_sapnotes_toolbar')
        toolbar = toolbar_widget.get_toolbar()        
        
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        srvicm = self.app.get_service('IM')
        icon = srvicm.get_new_image_icon('basico-fullscreen', 24, 24)
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
            
        