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
from basico.core.srv import Service
from basico.core.wdg import BasicoWidget
from basico.widgets.browser import BasicoBrowser

class Tab(IntEnum):
    VISOR = 0
    EDITOR = 1

class DialogKBSettings(BasicoWidget, Gtk.Dialog):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)

    def get_services(self):
        self.srvkbb = self.get_service('KB4IT')

    def _setup_widget(self):
        parent = self.srvuif.get_window_parent()
        Gtk.Dialog.__init__(
            self, "KB Basico Settings", parent, 0,
            (
                # ~ Gtk.STOCK_CANCEL,
                # ~ Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )
        box = self.get_content_area()
        self.set_default_size(400, 300)

        # Settings box
        vbox = Gtk.VBox()
        vbox.set_property('margin-left', 6)
        vbox.set_property('margin-right', 6)

        # Force compilation
        force = self.srvkbb.get_config_value('force')
        button = Gtk.ToggleButton("Force compilation")
        button.set_active(force)
        button.connect("toggled", self._on_force_compilation)
        vbox.pack_start(button, False, False, 6)
        box.add(vbox)
        self.show_all()

    def _on_force_compilation(self, button):
        force = button.get_active()
        self.srvkbb.set_config_value('force', force)


class KBAPI(Service):
    def get_services(self):
        self.srvkbb = self.get_service('KB4IT')

    def execute(self, api, args=None):
        fnc = 'self.%s(%s)' % (api, args)
        try:
            eval(fnc)
        except Exception as error:
            self.log.error(error)
            self.log.warning("Callback not implemented for KB API '%s'" % api)

    def settings(self, *args):
        self.log.debug("Show settings dialog")
        dialog = DialogKBSettings(self.app)
        dialog.run()
        dialog.destroy()

    def update(self, *args):
        self.srvkbb.request_update()

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
        self.app.register_service('API', KBAPI())
        self.srvapi = self.get_service('API')

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
        self.log.debug("API => Action[%s] Arguments[%s]", action, ', '.join(args))
        self.srvapi.execute(action, args)
        return False

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
