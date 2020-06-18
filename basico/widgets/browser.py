#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: browser.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Web browser module based on
# https://lazka.github.io/pgi-docs/WebKit2-4.0/classes/WebView.html
# https://lazka.github.io/pgi-docs/WebKit2-4.0/classes/PolicyDecision.html#WebKit2.PolicyDecision
# https://lazka.github.io/pgi-docs/WebKit2-4.0/enums.html#WebKit2.PolicyDecisionType
"""

import gi
gi.require_version('Gtk', '3.0')

try:
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2 as WebKit
    WEBKIT_RELEASE = 4
except:
    gi.require_version('WebKit', '3.0')
    from gi.repository import WebKit
    WEBKIT_RELEASE = 3

from gi.repository import Gtk
from gi.repository import Gio

from basico.core.env import FILE
from basico.core.wdg import BasicoWidget


class BasicoBrowser(BasicoWidget, Gtk.VBox):
    def __init__(self, app, name=None):
        if name is not None:
            self.name = name
        else:
            self.name = __class__.__name__
        super().__init__(app, self.name)
        Gtk.VBox.__init__(self)
        self.app = app
        if WEBKIT_RELEASE == 4:
            self.log.debug("Using WebKit2 (4.0)")
        else:
            self.log.debug("Using WebKit (3.0)")
        self.srvgui = self.app.get_service('GUI')
        self.webview = self.srvgui.add_widget('gtk_webkit_%s' % self.name, WebKit.WebView())
        self.webview.connect('context-menu', self.append_items)
        self.webview.connect('decide-policy', self.decide_policy)
        self.webview.connect('load-changed', self.load_changed)
        settings = self.webview.get_settings()
        if WEBKIT_RELEASE == 3:

            settings.set_property('enable-developer-extras', False)
            settings.set_property('enable-default-context-menu', True)
            settings.set_property('default-encoding', 'utf-8')
            settings.set_property('enable-private-browsing', False)
            settings.set_property('enable-html5-local-storage', True)

            # disable plugins, like Adobe Flash and Java
            settings.set_property('enable-plugins', False)

            # scale other content besides from text as well
            self.webview.set_full_content_zoom(True)
        else:
            settings.set_property('enable-smooth-scrolling', True)
            settings.set_property('enable-plugins', False)
            settings.set_property('enable-fullscreen', False)
            settings.set_property('enable-html5-database', False)
            settings.set_property('enable-html5-local-storage', False)
            settings.set_property('enable-media-stream', False)
            settings.set_property('enable-mediasource', False)
            settings.set_property('enable-offline-web-application-cache', True)
            settings.set_property('enable-page-cache', True)
            settings.set_property('enable-webaudio', False)
            settings.set_property('enable-webgl', False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.webview)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.pack_start(scrolled_window, True, True, 0)

    def append_items(self, webview, context_menu, hit_result_event, event):
        """Attach custom actions to browser context menu"""
        pass
        # ~ action = Gtk.Action("help", "Basico Help", None, None)
        # ~ action.connect("activate", self.display_help)
        # ~ option = WebKit.ContextMenuItem().new(action)
        # ~ context_menu.prepend(option)

    def display_help(self, *args):
        self.load_url(FILE['HELP_INDEX'])

    def load_url(self, url):
        self.log.debug("Loading url: %s", url)
        self.webview.load_uri(url)

    def decide_policy(self, webview, policy, ntype):
        return False
        # ~ self.log.debug(args)
        # ~ if policy == WebKit.PolicyDecisionType.RESPONSE:
            # ~ self.log.debug("Current URL: %s", webview.get_uri())
            # ~ self.log.debug("\t- policy: %s", policy)
            # ~ self.log.debug("\t- type: %s", ntype)

    def load_changed(self, *args):
        pass
        # ~ webview = self.srvgui.get_widget('gtk_webkit_%s' % self.name)
        # ~ self.log.debug("Current URL: %s", webview.get_uri())

