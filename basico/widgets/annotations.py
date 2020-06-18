#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: annotations.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Annotation widget
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

class AnnotationWidget(BasicoWidget, Gtk.Notebook):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.Notebook.__init__(self)
        self.get_services()
        self.setup()

    def get_services(self):
        self.srvgui = self.get_service('GUI')

    def setup(self):
        self.srvgui.add_widget('gtk_notebook_annotations', self)
        self.set_show_tabs(True)
        self.set_show_border(False)
        self.append_page(AnnotationVisor(self.app), Gtk.Label("Visor"))
        self.append_page(Gtk.Label("Not implemented"), Gtk.Label("Editor"))

class AnnotationBrowser(BasicoWidget, WebKit.WebView):
    __gtype_name__ = 'AnnotationBrowser'

    def __init__(self, app):
        super().__init__(app, 'AnnotBrowser')
        WebKit.WebView.__init__(self)
        self.connect('load-changed', self.load_changed)
        self.get_services()
        self.setup()

    def get_services(self):
        self.srvgui = self.get_service('GUI')

    def setup(self):
        self.srvgui.add_widget('annotations_browser', self)

    def load_url(self, url):
        self.log.debug("Loading url: %s", url)
        self.load_uri(url)

    def load_changed(self, webview, event):
        # https://lazka.github.io/pgi-docs/WebKit2-4.0/enums.html#WebKit2.LoadEvent
        # ~ webview = self.srvgui.get_widget('gtk_webkit_%s' % self.name)
        # ~
        # ~ print("Hola")
        myurl = "file:///home/t00m/.basico/var/doc/html/index.html"
        url = self.get_uri()
        self.log.debug("Current URL: %s", url)
        if event == WebKit.LoadEvent.STARTED:
            self.log.debug("Load started")
            if url == myurl:
                self.stop_loading ()
                self.log.debug("Url loading stopped. Execute callback")
                return False
        elif event == WebKit.LoadEvent.COMMITTED:
            self.log.debug("Load commited")
        elif event == WebKit.LoadEvent.FINISHED:
            self.log.debug("Load finished")
            if len(url) == 0:
                self.log.debug("Good! Url not loaded")


class AnnotationVisor(BasicoWidget, Gtk.VBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.VBox.__init__(self)
        self.get_services()
        self.setup()

    def get_services(self):
        self.srvgui = self.get_service('GUI')

    def setup(self):
        self.srvgui.add_widget('gtk_vbox_annotations_visor', self)
        self.set_hexpand(True)
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        visor_annotations = self.srvgui.add_widget('visor_annotations', AnnotationBrowser(self.app))
        visor_annotations.load_url("file://%s" % FILE['KB4IT_INDEX'])
        visor_annotations.set_hexpand(True)
        visor_annotations.set_vexpand(True)
        vwp.add(visor_annotations)
        scr.add(vwp)
        self.pack_start(scr, True, True, 0)
        self.show_all()
