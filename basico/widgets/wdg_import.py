#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_import.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Import SAP Notes Widget
"""

from os.path import sep as SEP
from html import escape
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from basico.core.mod_wdg import BasicoWidget
from basico.core.mod_env import ROOT, USER_DIR, APP, LPATH, GPATH, FILE

class ImportWidget(BasicoWidget, Gtk.VBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.VBox.__init__(self)
        self.get_services()
        self.setup()

    def get_services(self):
        """Load services to be used in this class
        """
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvicm = self.get_service('IM')
        self.srvdtb = self.get_service('DB')
        self.srvsap = self.get_service('SAP')

    def setup(self):
        # Import Header
        header = Gtk.VBox()
        hbox = Gtk.HBox()
        icon = self.srvicm.get_new_image_icon('basico-add')
        title = Gtk.Label()
        title.set_markup('<big><b>Import SAP Notes from Launchpad</b></big>')
        title.set_xalign(0.0)
        hbox.pack_start(icon, False, False, 6)
        hbox.pack_start(title, True, True, 0)
        separator = Gtk.Separator()
        header.pack_start(hbox, False, False, 0)
        header.pack_start(separator, False, False, 3)
        self.pack_start(header, False, False, 0)

        # Import body
        vbox = Gtk.VBox()
        vbox.set_size_request(400,320)
        label = Gtk.Label()
        message = "Write down the list of SAP Notes that you want to download.\nThey can be separated by a new line or by commas."
        label.set_markup('%s' % message)
        label.set_property('margin-top', 3)
        label.set_property('margin-bottom', 3)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0.0)
        vbox.pack_start(label, False, True, 0)
        custom_scroller = Gtk.ScrolledWindow()
        custom_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        custom_scroller.set_shadow_type(Gtk.ShadowType.IN)
        custom_scroller.set_vexpand(True)
        custom_text_view = self.srvgui.add_widget('gtk_textview_download_launchpad', Gtk.TextView())
        custom_text_view.set_vexpand(True)
        custom_text_buffer = Gtk.TextBuffer()
        custom_text_buffer.set_text('')
        custom_text_view.set_buffer(custom_text_buffer)
        custom_scroller.add(custom_text_view)
        vbox.pack_start(custom_scroller, True, True, 0)
        label = Gtk.Label()
        message = "<small>SAP Notes will be download in background</small>"
        label.set_markup('%s' % message)
        label.set_justify(Gtk.Justification.LEFT)
        vbox.pack_end(label, False, False, 0)
        custom_button = Gtk.Button("Download")
        custom_button.connect('clicked', self.import_from_launchpad)
        vbox.pack_end(custom_button, False, False, 3)
        self.pack_start(vbox, True, True, 0)
        self.show_all()

    def import_from_launchpad(self, *args):
        textview = self.srvgui.get_widget('gtk_textview_download_launchpad')
        dlbuffer = textview.get_buffer()
        istart, iend = dlbuffer.get_bounds()
        text = dlbuffer.get_text(istart, iend, False)

        bag = []
        all_notes = []
        sapnotes = set()

        # Get SAP Notes from textview
        lines = text.replace(' ', ',')
        lines = lines.replace('\n', ',')

        # Get a unique list of SAP Notes to be imported
        for sid in lines.split(','):
            sid = sid.strip()
            if len(sid) > 0:
                sapnotes.add(sid)

        # For those SAP Notes, check which ones are valid
        for sid in sapnotes:
            is_valid = self.srvdtb.is_valid(sid)
            # FIXME: Add checkbox in wdg_import to allow overwrite SAP Notes
            # ~ is_saved = self.srvdtb.get_sapnote_metadata(sid)
            if is_valid: # and not is_saved:
                bag.append(sid)
        lbag = list(bag)

        # If bag is not empty, tell SAP module to start the requests.
        # If Firefox profile is well configured, SAP Notes will be
        # downloaded in background one by one.
        if len(lbag) > 0:
            self.log.debug("Number of SAP Notes to be downloaded: %d", len(lbag))
            self.srvsap.download(lbag)
        dlbuffer.set_text('')
