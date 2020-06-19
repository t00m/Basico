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
gi.require_version('Soup', '2.4')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Soup
from gi.repository import WebKit2 as WebKit

from basico.core.env import FILE
from basico.core.wdg import BasicoWidget


class BasicoBrowser(BasicoWidget, WebKit.WebView):
    def __init__(self, app, name=None):
        if name is not None:
            self.name = name
        else:
            self.name = __class__.__name__
        super().__init__(app, self.name)
        WebKit.WebView.__init__(self)
        self.srvgui = self.app.get_service('GUI')
        self.srvuif = self.app.get_service('UIF')
        self.setup()

    def setup(self):
        self.srvgui.add_widget('browser_%s' % self.name, self)

        # Webkit context
        web_context = WebKit.WebContext.get_default()
        web_context.set_cache_model(WebKit.CacheModel.DOCUMENT_VIEWER)
        web_context.set_process_model(WebKit.ProcessModel.MULTIPLE_SECONDARY_PROCESSES)
        web_context.register_uri_scheme('basico', self._on_basico_scheme)

        # Webkit settings
        web_settings = WebKit.Settings()
        web_settings.set_enable_smooth_scrolling(True)
        web_settings.set_enable_plugins(False)
        # ~ settings = self.get_settings()
        # ~ settings.set_property('enable-smooth-scrolling', True)
        # ~ settings.set_property('enable-plugins', False)
        # ~ settings.set_property('enable-fullscreen', False)
        # ~ settings.set_property('enable-html5-database', False)
        # ~ settings.set_property('enable-html5-local-storage', False)
        # ~ settings.set_property('enable-media-stream', False)
        # ~ settings.set_property('enable-mediasource', False)
        # ~ settings.set_property('enable-offline-web-application-cache', True)
        # ~ settings.set_property('enable-page-cache', True)
        # ~ settings.set_property('enable-webaudio', False)
        # ~ settings.set_property('enable-webgl', False)

        self.connect('context-menu', self._on_append_items)
        self.connect('decide-policy', self._on_decide_policy)
        self.connect('load-changed', self.load_changed)



        # ~ scrolled_window = Gtk.ScrolledWindow()
        # ~ scrolled_window.add(self.webview)
        # ~ scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        # ~ scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        # ~ scrolled_window.set_hexpand(True)
        # ~ scrolled_window.set_vexpand(True)
        # ~ self.pack_start(scrolled_window, True, True, 0)


    def _get_api(self, uri):
        """Use Soup.URI to split uri
        Args:
            uri (str)
        Returns:
            A list with two strings representing a path and fragment
        """
        path = None
        fragment = None

        if uri:
            soup_uri = Soup.URI.new(uri)
            action = soup_uri.host
            args = soup_uri.path.split('/')[1:]

        return [action, args]

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
        dialog = self.srvuif.message_dialog_info("Action: %s" % action, "Arguments: %s" % ', '.join(args))
        dialog.run()
        dialog.destroy()

    def _on_append_items(self, webview, context_menu, hit_result_event, event):
        """Attach custom actions to browser context menu"""
        pass
        # ~ action = Gtk.Action("help", "Basico Help", None, None)
        # ~ action.connect("activate", self.display_help)
        # ~ option = WebKit.ContextMenuItem().new(action)
        # ~ context_menu.prepend(option)

    # ~ def display_help(self, *args):
        # ~ self.load_url(FILE['HELP_INDEX'])

    def load_url(self, url):
        self.log.debug("Loading url: %s", url)
        self.load_uri(url)

    def _on_decide_policy(self, webview, decision, decision_type):
        """Decide what to do when clicked on link
        Args:
            webview (WebKit2.WebView)
            decision (WebKit2.PolicyDecision)
            decision_type (WebKit2.PolicyDecisionType)
        Returns:
            True to stop other handlers from being invoked for the event.
            False to propagate the event further.
        """
        if decision_type is WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            action = WebKit.NavigationPolicyDecision.get_navigation_action(decision)
            click = action.get_mouse_button() != 0
            uri = webview.get_uri()
            if click:
                self.log.debug("User clicked in link: %s", uri)


    def load_changed(self, webview, event):
        uri = webview.get_uri()
        if event == WebKit.LoadEvent.STARTED:
            self.log.debug("Load started for url: %s", uri)
        elif event == WebKit.LoadEvent.COMMITTED:
            self.log.debug("Load committed for url: %s", uri)
        elif event == WebKit.LoadEvent.FINISHED:
            self.log.debug("Load finished for url: %s", uri)
            if len(uri) == 0:
                self.log.debug("Url not loaded")
