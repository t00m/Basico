#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_iconmgt.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Icon manager service
"""

import os

import pkg_resources

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from basico.core.mod_env import GPATH
from basico.core.mod_srv import Service


class IconManager(Service):
    def initialize(self):
        self.log.debug("Attached Icons DIR: %s" % GPATH['ICONS'])
        self.icondict = {}
        self.imgdict = {}
        self.theme = Gtk.IconTheme.get_default()
        self.theme.prepend_search_path (GPATH['ICONS'])


    def get_themed_icon(self, icon_name):
        ICON = GPATH['ICONS'] + icon_name + '.png'
        icon = Gio.ThemedIcon.new(ICON)

        return icon



    def get_icon(self, name, width=24, height=24):
        key = "%s-%d-%d" % (name, width, height)

        # Get icon from cache if exists or add a new one
        try:
            icon = self.icondict[key]
        except:
            iconinfo = self.theme.lookup_icon(name, width, Gtk.IconLookupFlags.GENERIC_FALLBACK)
            icon = iconinfo.load_icon()
            self.icondict[key] = icon

        return icon


    def get_pixbuf_icon(self, name, width=36, height=36):
        key = "%s-%d-%d" % (name, width, height)

        # Get icon from cache if exists or add a new one
        try:
            icon = self.icondict[key]
        except Exception as error:
            icon = None
            if name in self.theme.list_icons():
                icon = self.theme.load_icon(name, width, Gtk.IconLookupFlags.GENERIC_FALLBACK)
            self.icondict[key] = icon

        return icon


    def get_new_image_icon(self, name, width=36, height=36):
        pixbuf = self.get_pixbuf_icon(name, width, height)
        icon = Gtk.Image()
        icon.set_from_pixbuf(pixbuf)

        return icon


    def get_image_icon(self, name, width=36, height=36):
        key = "%s-%d-%d" % (name, width, height)
        try:
            icon = self.imgdict[key]
        except Exception as error:
            icon = None
            if name in self.theme.list_icons():
                pixbuf = self.theme.load_icon(name, width, Gtk.IconLookupFlags.GENERIC_FALLBACK)
                icon = Gtk.Image()
                icon.set_from_pixbuf(pixbuf)
            self.imgdict[key] = icon

        return icon
