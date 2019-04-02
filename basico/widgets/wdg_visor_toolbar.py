#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_visor_toolbar.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAPNoteViewVisorToolbar widgets
"""


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_import import ImportWidget
from basico.core.mod_wdg import BasicoWidget


class VisorToolbar(BasicoWidget, Gtk.HBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.Box.__init__(self)
        self.get_services()
        self.set_homogeneous(False)
        self.tool_bar = Gtk.Toolbar()
        self.pack_start(self.tool_bar, False, True, 0)
        self.tool_bar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.tool_bar.set_property('margin-bottom', 0)


        # Import button
        tool = Gtk.ToolButton()
        tool.set_icon_name('basico-add')
        tool.set_tooltip_markup('<b>Download or find SAP Notes (if they were already downloaded)</b>')
        popover = self.srvgui.add_widget('gtk_popover_toolbutton_import', Gtk.Popover.new(tool))
        tool.connect('clicked', self.srvclb.gui_show_popover, popover)
        self.tool_bar.insert(tool, -1)

        ## Popover body
        box = Gtk.VBox(spacing = 0, orientation="vertical")
        box.set_property('margin', 3)
        widget_import = self.srvgui.add_widget('widget_import', ImportWidget(self.app))
        box.pack_start(widget_import, True, True, 6)
        popover.add(box)

        # Annotation button
        tool = Gtk.ToolButton()
        tool.set_icon_name('basico-annotation')
        tool.set_tooltip_markup('<b>Create a new annotation (not linked to any SAP Note)</b>')
        popover = self.srvgui.add_widget('gtk_popover_annotation', Gtk.Popover.new(tool))
        tool.connect('clicked', self.srvclb.gui_annotation_widget_show)
        self.tool_bar.insert(tool, -1)


        # Filter entry

        ## Completion
        self.completion = self.srvgui.add_widget('gtk_entrycompletion_visor', Gtk.EntryCompletion())
        self.completion.set_match_func(self.completion_match_func)
        self.completion_model = Gtk.ListStore(str)
        self.completion.set_model(self.completion_model)
        self.completion.set_text_column(0)

        tool = Gtk.ToolItem.new()

        hbox = Gtk.HBox()
        entry = Gtk.Entry()
        entry.set_completion(self.completion)
        entry.connect('activate', self.srvclb.gui_filter_visor)
        self.srvgui.add_widget('gtk_entry_filter_visor', entry)

        icon = self.srvicm.get_pixbuf_icon('basico-find')
        entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, icon)
        entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, True)
        entry.set_icon_tooltip_markup (Gtk.EntryIconPosition.PRIMARY, "Search in the whole database")

        icon = self.srvicm.get_pixbuf_icon('basico-filter')
        entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.SECONDARY, icon)
        entry.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, True)
        entry.set_icon_tooltip_markup (Gtk.EntryIconPosition.SECONDARY, "Click here to filter results")
        entry.set_placeholder_text("Filter results...")

        def on_icon_pressed(entry, icon_pos, event):
            if icon_pos == Gtk.EntryIconPosition.PRIMARY:
                self.srvclb.action_search(entry)
            elif icon_pos == Gtk.EntryIconPosition.SECONDARY:
                self.srvclb.gui_filter_visor(entry)

        entry.connect('changed', self.srvclb.gui_filter_visor)
        entry.connect("icon-press", on_icon_pressed)
        hbox.pack_start(entry, True, True, 0)
        tool.add(hbox)
        tool.set_tooltip_markup('<b>Click left icon to search in all the annotations or just type to filter the current view</b>')
        tool.set_expand(True)
        self.tool_bar.insert(tool, -1)

        # Separator
        tool = Gtk.SeparatorToolItem.new()
        tool.set_draw(False)
        tool.set_expand(True)
        self.tool_bar.insert(tool, -1)

        # Button Total SAP Notes
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        label = self.srvgui.add_widget('gtk_label_total_notes', Gtk.Label())
        hbox = Gtk.HBox()
        hbox.pack_start(label, False, False, 0)
        tool.add(hbox)
        self.tool_bar.insert(tool, -1)

        # Fullscreen toggle button
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        icon = self.srvicm.get_new_image_icon('basico-fullscreen', 24, 24)
        box = self.srvgui.add_widget('gtk_box_container_icon_fullscreen', Gtk.Box())
        box.pack_start(icon, False, False, 0)
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('toggled', self.srvclb.gui_toggle_fullscreen)
        button.add(box)
        tool.add(button)
        tool.set_tooltip_markup('<b>Fullscreen/Window mode</b>')
        self.tool_bar.insert(tool, -1)

        # Toolbar initial settings
        self.set_visible(True)
        self.set_no_show_all(False)
        self.tool_bar.set_hexpand(True)


    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvuif = self.get_service("UIF")


    def completion_match_func(self, completion, key, iter):
        model = completion.get_model()
        text = model.get_value(iter, 0)
        if key.upper() in text.upper():
            return True
        return False
