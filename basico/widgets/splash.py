#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: setup.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: splash screen for Basico
#
# !!!
# Code borrowed and modified from: https://github.com/SolydXK/solydxk-system/blob/origin/master/usr/lib/solydxk/system/splash.py
# !!!
#
"""

import os
import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Splash():
    def __init__(self, title, width=400, height=250, font=36, font_weight='normal', font_color='000000', background_color='ffffff', background_image=None, app=None):
        self.app = app
        self.log = logging.getLogger(__class__.__name__)
        self.log.addHandler(self.app.intercepter)
        self.title = title
        self.width = width
        self.height = height
        self.font = font
        self.font_weight = font_weight
        self.font_color = self.prep_hex_color(font_color)
        self.background_image = '' if background_image is None else background_image


        # Window settings
        self.window = Gtk.Window(Gtk.WindowType.POPUP)
        self.window.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_title(self.title)

        # Create overlay with a background image
        overlay = Gtk.Overlay()
        self.window.add(overlay)
        if os.path.exists(self.background_image):
            # Window will adjust to image size automatically
            bg = Gtk.Image.new_from_file(self.background_image)
            overlay.add(bg)
        else:
            # Set window dimensions
            self.window.set_default_size(self.width, self.height)
            # Set background color
            self.window.override_background_color(Gtk.StateType.NORMAL,
                                                  self.hex_to_rgba(background_color, True))

        # Add box with label
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_top(self.height / 3)
        box.set_margin_left(20)
        box.set_margin_right(20)

        # Add the box to a new overlay in the existing overlay
        overlay.add_overlay(box)
        lbl_title = Gtk.Label()
        lbl_title.set_line_wrap(True)
        lbl_title.set_justify(Gtk.Justification.CENTER)
        # Markup format: https://developer.gnome.org/pango/stable/PangoMarkupFormat.html
        lbl_title.set_markup('<span font="{}" color="#{}" weight="{}">{}</span>'.format(self.font,
                                                                                        self.font_color,
                                                                                        self.font_weight,
                                                                                        self.title))
        box.pack_start(lbl_title, False, True, 0)

        self.run()


    def run(self):
        # Show the splash screen
        self.window.show_all()
        # Without this ugly one-liner, the window won't show
        while Gtk.events_pending():
            Gtk.main_iteration()
        # ~ self.log.debug("Show the splash screen")


    def prep_hex_color(self, hex_color):
        hex_color = hex_color.strip('#')
        # Fill up with last character until length is 6 characters
        if len(hex_color) < 6:
            hex_color = hex_color.ljust(6, hex_color[-1])
        # Add alpha channel if it's not there
        hex_color = hex_color.ljust(8, 'f')
        return hex_color


    def hex_to_rgba(self, hex_color, as_gdk_rgba=False):
        hex_color = self.prep_hex_color(hex_color)
        # Create a list with rgba values from hex_color
        rgba = list(int(hex_color[i : i + 2], 16) for i in (0, 2 ,4, 6))
        if as_gdk_rgba:
            # Change values to float between 0 and 1 for Gdk.RGBA
            for i, val in enumerate(rgba):
                if val > 0:
                    rgba[i] = 1 / (255 / val)
            # Return the Gdk.RGBA object
            return Gdk.RGBA(rgba[0], rgba[1], rgba[2], rgba[3])
        return rgba


    def show(self):
        self.window.show()
        self.log.debug("Show the splash screen")


    def hide(self):
        self.window.hide()
        self.log.debug("Hide the splash screen")


    def destroy(self):
        while Gtk.events_pending(): Gtk.main_iteration()
        self.window.destroy()
        # ~ self.log.debug("Hide the splash screen")
