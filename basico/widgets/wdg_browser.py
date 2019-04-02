#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: browser.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Web browser module
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')

from gi.repository import Gtk
from gi.repository import WebKit


class BasicoBrowser(Gtk.VBox):
    def __init__(self, *args, **kwargs):
        super(BasicoBrowser, self).__init__(*args, **kwargs)

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        settings.set_property('enable-developer-extras', True)
        settings.set_property('enable-default-context-menu', True)

        settings.set_property('default-encoding', 'utf-8')
        settings.set_property('enable-private-browsing', True)
        settings.set_property('enable-html5-local-storage', True)

        # disable plugins, like Adobe Flash and Java
        settings.set_property('enable-plugins', True)

        # scale other content besides from text as well
        self.webview.set_full_content_zoom(True)

        self.show()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.webview)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.pack_start(scrolled_window, True, True, 0)
        scrolled_window.show_all()


    def load_url(self, url):
        self.webview.load_uri(url)
