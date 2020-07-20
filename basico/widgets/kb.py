#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: kb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Set of widgets for working with KB4IT
"""

import os
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

def AreYouSure(parent, title):
    dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, 'Are You Sure?')
    dialog.format_secondary_text(title)
    dialog.set_transient_for(parent)
    response = dialog.run()
    dialog.destroy()
    return response == Gtk.ResponseType.YES

class Tab(IntEnum):
    VISOR = 0
    EDITOR = 1

class KBUISettings(BasicoWidget, Gtk.Dialog):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)

    def get_services(self):
        self.srvkbb = self.get_service('KB4IT')
        self.srvclb = self.get_service('Callbacks')

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
        vboxup = Gtk.VBox()
        vboxdw = Gtk.VBox()
        vbox.pack_start(vboxup, True, True, 6)
        vbox.pack_start(vboxdw, False, False, 0)

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
        hbox.pack_start(button, False, False, 6)
        vboxup.pack_start(hbox, True, True, 6)

        # Source directory
        sources = self.srvkbb.get_config_value('source_dir') or  LPATH['DOC_SOURCE']
        hbox = Gtk.HBox()
        tip = Gtk.Label()
        tip.set_xalign(0.0)
        tip.set_markup('<b>Source directory</b>')
        hbox.pack_start(tip, True, True, 6)
        button = Gtk.FileChooserButton(Gtk.FileChooserAction.CREATE_FOLDER)
        button.set_filename(sources)
        button.set_create_folders(True)
        button.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        button.connect("file-set",self._on_update_select_source_folder)
        hbox.pack_start(button, True, True, 6)
        vboxup.pack_start(hbox, False, False, 6)

        # Target directory
        sources = self.srvkbb.get_config_value('target_dir') or  LPATH['DOC_TARGET']
        hbox = Gtk.HBox()
        tip = Gtk.Label()
        tip.set_xalign(0.0)
        tip.set_markup('<b>Target directory</b>')
        hbox.pack_start(tip, True, True, 6)
        button = Gtk.FileChooserButton(Gtk.FileChooserAction.CREATE_FOLDER)
        button.set_filename(sources)
        button.set_create_folders(True)
        button.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        button.connect("file-set",self._on_update_select_target_folder)
        hbox.pack_start(button, True, True, 6)
        vboxup.pack_start(hbox, False, False, 6)

        sep = Gtk.HSeparator()
        vboxdw.pack_start(sep, False, False, 6)

        # Initialize KB
        hbox = Gtk.HBox()
        tip = Gtk.Label()
        tip.set_xalign(0.0)
        tip.set_markup('<b>Initialize KB</b>')
        hbox.pack_start(tip, True, True, 6)
        button = Gtk.Button('Initialize')
        button.connect("clicked", self._on_initialize_kb)
        hbox.pack_start(button, False, False, 6)
        vboxdw.pack_start(hbox, False, False, 6)

        # ~ # Auto-update KB
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

    def _on_update_select_source_folder(self, chooser):
        folder = chooser.get_filename()
        self.srvkbb.set_config_value('source_dir', folder)
        self.log.info("Source directory for Basico KB set to: %s", folder)

    def _on_update_select_target_folder(self, chooser):
        folder = chooser.get_filename()
        self.srvkbb.set_config_value('target_dir', folder)
        self.log.info("Target directory for Basico KB set to: %s", folder)

    def _on_initialize_kb(self, button):
        self.log.info("Initializing KB")
        parent = self.srvuif.get_window_parent()
        SURE = AreYouSure(parent, "Your KB will be destroyed and initialized")
        if SURE:
            self.srvkbb.reset()
        self.destroy()


class KBUIAPI(Service):
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

    def delete(self, adoc):
        visor_kb = self.srvgui.get_widget('visor_kb')
        uri = visor_kb.get_uri()
        basename = os.path.basename(uri)
        adoc = basename.replace('.html', '')
        self.srvkbb.delete_document([adoc])

    def settings(self, *args):
        self.log.debug("Show settings dialog")
        dialog = KBUISettings(self.app)
        dialog.run()
        dialog.destroy()

    def update(self, *args):
        self.srvkbb.request_update()

class KBUI(BasicoWidget, Gtk.Notebook):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)

    def _setup_widget(self):
        Gtk.Notebook.__init__(self)
        self.srvgui.add_widget('gtk_notebook_kb', self)
        self.set_show_tabs(False)
        self.set_show_border(False)
        self.append_page(KBVisor(self.app), Gtk.Label("Visor"))
        self.append_page(Gtk.Label("Not implemented"), Gtk.Label("Editor"))


class KBUIBrowser(BasicoBrowser):
    def __init__(self, app):
        super().__init__(app,  __class__.__name__)

    def setup_widget(self):
        self.web_context.register_uri_scheme('basico', self._on_basico_scheme)
        WebKit.WebView.__init__(self,
                                 web_context=self.web_context,
                                 settings=self.web_settings)
        self.app.register_service('API', KBUIAPI())
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

        self.log.debug("API => Action[%s] Arguments[%s]", action, ', '.join(args))
        self.srvapi.execute(action, args)
        if action != 'delete':
            self.reload_page()
        else:
            target_dir = self.srvkbb.get_config_value('target_dir') or  LPATH['DOC_TARGET']
            homepage = "file://%s" % os.path.join(target_dir, 'index.html')
            self.load_url(homepage)

    def _on_load_failed(self, webview, load_event, failing_uri, error):
        if failing_uri.startswith('basico://'):
            return

        target_dir = self.srvkbb.get_config_value('target_dir') or  LPATH['DOC_TARGET']
        homepage = "%s" % os.path.join(target_dir, 'index.html')
        self.log.debug("Home page: %s", homepage)
        if failing_uri.replace('file://', '') == homepage:
            self.log.debug("Home page doesn't exist. Rebuilding KB")
            self.rebuild_database()
        else:
            self.log.warning("%s failed to load. Loading home page", failing_uri)
            self.stop_loading()
            self.load_url(homepage)
            self.load_url(homepage)

    def load_url(self, uri):
        self.log.debug("Clear browser cache")
        self.web_context.clear_cache()
        url = uri.replace('file://', '')
        # ~ self.log.debug("KB URI: %s", url)
        if not os.path.exists(url):
            # ~ self.log.warning("Page doesn't exist")
            target_dir = self.srvkbb.get_config_value('target_dir') or  LPATH['DOC_TARGET']
            homepage = "file://%s" % os.path.join(target_dir, 'index.html')
            self.load_uri(homepage)
            self.log.info("KB index page loaded")
        else:
            self.load_uri(uri)

    def reload_page(self, *args):
        self.log.debug("Reload page: %s", self.get_uri())
        self.reload()

    def rebuild_database(self, *args):
        self.srvkbb.request_update()
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
        visor_kb = self.srvgui.add_widget('visor_kb', KBUIBrowser(self.app))
        visor_kb.load_url("file://%s" % FILE['KB4IT_INDEX'])
        visor_kb.set_hexpand(True)
        visor_kb.set_vexpand(True)
        vwp.add(visor_kb)
        scr.add(vwp)
        self.pack_start(scr, True, True, 0)
        self.show_all()
