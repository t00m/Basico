#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: kb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Set of widgets for working with KB4IT
"""

from enum import IntEnum

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
try:
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2 as WebKit
except:
    gi.require_version('WebKit', '3.0')
    from gi.repository import WebKit

from basico.core.env import FILE
from basico.core.wdg import BasicoWidget
from basico.widgets.browser import BasicoBrowser

class Tab(IntEnum):
    VISOR = 0
    EDITOR = 1

class KB4Basico(BasicoWidget, Gtk.Notebook):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)

    def _setup_widget(self):
        Gtk.Notebook.__init__(self)
        self.srvgui.add_widget('gtk_notebook_kb', self)
        self.set_show_tabs(False)
        self.set_show_border(False)
        self.append_page(KBVisor(self.app), Gtk.Label("Visor"))
        self.append_page(Gtk.Label("Not implemented"), Gtk.Label("Editor"))


class KBBrowser(BasicoBrowser):
    def __init__(self, app):
        super().__init__(app,  __class__.__name__)

    def setup_widget(self):
        self.web_context.register_uri_scheme('basico', self._on_basico_scheme)
        WebKit.WebView.__init__(self,
                                 web_context=self.web_context,
                                 settings=self.web_settings)

    def _on_basico_scheme(self, request):
        """Get api callback for Basico scheme requests
        Args:
            request (WebKit2.URISchemeRequest)
        """
        uri = request.get_uri()

        try:
            action, args = self._get_api(uri)
        except Exception as e:
            error_str = e.args[1]
            request.finish_error(GLib.Error(error_str))
            return
        self.log.info("API => Action[%s] Arguments[%s]", action, ', '.join(args))
        dialog = self.srvuif.message_dialog_info("Action: %s" % action, "Arguments: %s" % ', '.join(args))
        dialog.run()
        dialog.destroy()

class KBVisor(BasicoWidget, Gtk.VBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.VBox.__init__(self)
        self.setup()

    def setup(self):
        self.srvgui.add_widget('gtk_vbox_kb_visor', self)
        self.set_hexpand(True)
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        visor_kb = self.srvgui.add_widget('visor_kb', KBBrowser(self.app))
        visor_kb.load_url("file://%s" % FILE['KB4IT_INDEX'])
        visor_kb.set_hexpand(True)
        visor_kb.set_vexpand(True)
        vwp.add(visor_kb)
        scr.add(vwp)
        self.pack_start(scr, True, True, 0)
        self.show_all()
