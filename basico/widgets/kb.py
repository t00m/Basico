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

from basico.core.env import FILE, LPATH
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
        hbox = Gtk.HBox()
        tip = Gtk.Label()
        tip.set_xalign(0.0)
        tip.set_markup('<b>Force compilation?</b>')
        hbox.pack_start(tip, True, True, 6)
        button = Gtk.Switch()
        button.set_active(force)
        button.connect("notify::active", self._on_force_compilation)
        hbox.pack_start(button, True, True, 6)
        vbox.pack_start(hbox, False, False, 6)

        # ~ # Auto update
        # ~ auto = self.srvkbb.get_config_value('auto-update')
        # ~ hbox = Gtk.HBox()
        # ~ tip = Gtk.Label()
        # ~ tip.set_xalign(0.0)
        # ~ tip.set_markup('<b>Auto update Basico KB (monitor changes)</b>')
        # ~ hbox.pack_start(tip, True, True, 6)
        # ~ button = Gtk.Switch()
        # ~ button.set_active(force)
        # ~ button.connect("notify::active", self._on_auto_update)
        # ~ hbox.pack_start(button, True, True, 6)
        # ~ vbox.pack_start(hbox, False, False, 6)


        # Source directory
        sources = self.srvkbb.get_config_value('sources')
        if sources is None:
            sources = LPATH['DOC_SOURCE']
        hbox = Gtk.HBox()
        tip = Gtk.Label()
        tip.set_xalign(0.0)
        tip.set_markup('<b>Sources directory</b>')
        hbox.pack_start(tip, True, True, 6)
        button = Gtk.FileChooserButton(Gtk.FileChooserAction.CREATE_FOLDER)
        button.set_filename(sources)
        button.set_create_folders(True)
        button.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        button.connect("file-set",self._on_update_select_folder)
        hbox.pack_start(button, True, True, 6)
        vbox.pack_start(hbox, False, False, 6)

        box.add(vbox)
        self.show_all()

    def _on_force_compilation(self, button, gparam):
        force = button.get_active()
        self.srvkbb.set_config_value('force', force)
        self.log.info("Force compilation set to: %s", force)

    # ~ def _on_auto_update(self, button, gparam):
        # ~ auto = button.get_active()
        # ~ self.srvkbb.set_config_value('auto-update', auto)
        # ~ self.log.info("Auto update Basico KB set to: %s", auto)

    def _on_update_select_folder(self, chooser):
        folder = chooser.get_filename()
        self.srvkbb.set_config_value('sources', folder)
        self.log.info("Sources directory for Basico KB set to: %s", folder)


class KBAPI(Service):
    def get_services(self):
        self.srvgui = self.get_service('GUI')
        self.srvkbb = self.get_service('KB4IT')
        self.srvclb = self.get_service('Callbacks')

    def execute(self, api, args=None):
        fnc = 'self.%s(%s)' % (api, args)
        try:
            eval(fnc)
        except Exception as error:
            self.log.error(error)
            self.log.warning("Callback not implemented for KB API '%s'" % api)
            raise

    def add(self, params):
        source = params[0]
        if source == 'files':
            self.srvclb.kb_import_from_files()
        elif source == 'directory':
            self.srvclb.kb_import_from_directory()
        elif source == 'template':
            self.srvclb.kb_import_from_template(source)

    def delete(self, url):
        visor_kb = self.srvgui.get_widget('visor_kb')
        uri = visor_kb.get_uri()
        self.log.debug(uri)

    def settings(self, *args):
        self.log.debug("Show settings dialog")
        dialog = DialogKBSettings(self.app)
        dialog.run()
        dialog.destroy()

    def update(self, *args):
        self.srvkbb.request_update()

class KBWidget(BasicoWidget, Gtk.Notebook):
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
        self.srvkbb = self.get_service('KB4IT')
        self.srvkbb.connect('kb-updated', self.reload_page)

    def _on_append_items(self, webview, context_menu, hit_result_event, event):
        """Attach custom actions to browser context menu"""
        action = Gtk.Action("rebuild", "Force a database rebuild", None, None)
        action.connect("activate", self.rebuild_database)
        option = WebKit.ContextMenuItem().new(action)
        context_menu.append(option)

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
        # ~ self.stop_loading ()
        self.log.debug("API => Action[%s] Arguments[%s]", action, ', '.join(args))
        self.srvapi.execute(action, args)
        self.reload_page()

    def _on_load_failed(self, webview, load_event, failing_uri, error):
        if failing_uri.startswith('basico://'):
            return
        if failing_uri == FILE['KB4IT_INDEX']:
            self.rebuild_database()
        else:
            self.log.warning("%s failed to load. Loading home page", failing_uri)
            self.load_url("file://%s" % FILE['KB4IT_INDEX'])

    def reload_page(self, *args):
        self.log.debug("Reload page: %s", self.get_uri())
        self.reload()

    def rebuild_database(self, *args):
        # ~ self.stop_loading()
        self.load_url('basico://update')

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
