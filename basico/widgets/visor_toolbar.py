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
from gi.repository.GdkPixbuf import Pixbuf

from basico.widgets.cols import ColsMgtView
from basico.widgets.sapimport import ImportWidget
from basico.core.wdg import BasicoWidget


class VisorToolbar(BasicoWidget, Gtk.VBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)

    def _setup_widget(self):
        Gtk.Box.__init__(self)
        self.set_homogeneous(False)

        # Toolbar
        self.toolbar = Gtk.Toolbar()
        self.pack_start(self.toolbar, False, True, 0)
        self.toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.toolbar.set_property('margin-bottom', 0)

        # ~ tool = Gtk.ToolButton()
        # ~ tool.set_icon_name('basico-add')
        # ~ tool.set_tooltip_markup('<b>Download or find SAP Notes (if they were already downloaded)</b>')
        # ~ popover = self.srvgui.add_widget('gtk_popover_toolbutton_import', Gtk.Popover.new(tool))
        # ~ tool.connect('clicked', self.srvuif.popover_show, popover)
        # ~ self.toolbar.insert(tool, -1)

        # ~ ## Popover body
        # ~ box = Gtk.VBox(spacing = 0, orientation="vertical")
        # ~ box.set_property('margin', 3)
        # ~ widget_import = self.srvgui.add_widget('widget_import', ImportWidget(self.app))
        # ~ box.pack_start(widget_import, True, True, 6)
        # ~ popover.add(box)

        # ~ # Annotation button
        # ~ tool = Gtk.ToolButton()
        # ~ tool.set_icon_name('basico-annotation')
        # ~ tool.set_tooltip_markup('<b>Create a new annotation (not linked to any SAP Note)</b>')
        # ~ popover = self.srvgui.add_widget('gtk_popover_annotation', Gtk.Popover.new(tool))
        # ~ tool.connect('clicked', self.clb_create_annotation)
        # ~ self.toolbar.insert(tool, -1)

        # ~ ## Attachment button
        # ~ tool = Gtk.ToolButton()
        # ~ tool.set_icon_name('basico-attachment')
        # ~ tool.set_tooltip_markup('<b>Attach any document to this annotation</b>')
        # ~ popover = self.srvgui.add_widget('gtk_button_main_toolbar_attachment', Gtk.Popover.new(tool))
        # ~ tool.connect('clicked', self.srvclb.gui_attachment_add)
        # ~ self.toolbar.insert(tool, -1)

        ## Filter entry

        ### Completion
        self.completion = self.srvgui.add_widget('gtk_entrycompletion_visor', Gtk.EntryCompletion())
        self.completion.set_match_func(self.completion_match_func)
        self.completion_model = Gtk.ListStore(str)
        self.completion.set_model(self.completion_model)
        self.completion.set_text_column(0)

        tool = Gtk.ToolItem.new()

        hbox = Gtk.HBox()
        entry = Gtk.Entry()
        entry.set_completion(self.completion)
        entry.connect('changed', self.entry_filter)
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
            visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
            if icon_pos == Gtk.EntryIconPosition.PRIMARY:
                self.entry_search(entry)
            elif icon_pos == Gtk.EntryIconPosition.SECONDARY:
                visor_sapnotes.filter()

        # ~ entry.connect('changed', self.srvclb.gui_filter_visor)
        entry.connect("icon-press", on_icon_pressed)
        hbox.pack_start(entry, True, True, 0)
        tool.add(hbox)
        tool.set_tooltip_markup('<b>Click left icon to search in all the annotations or just type to filter the current view</b>')
        tool.set_expand(True)
        self.toolbar.insert(tool, -1)

        ## Separator
        tool = Gtk.SeparatorToolItem.new()
        tool.set_draw(False)
        tool.set_expand(True)
        self.toolbar.insert(tool, -1)

        ## Button Total SAP Notes
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        label = self.srvgui.add_widget('gtk_label_total_notes', Gtk.Label())
        hbox = Gtk.HBox()
        hbox.pack_start(label, False, False, 0)
        tool.add(hbox)
        self.toolbar.insert(tool, -1)

        # ~ ## Visor Stack Switcher
        # ~ tool = Gtk.ToolItem()
        # ~ tool.set_expand(False)
        # ~ hbox = self.srvgui.add_widget('gtk_hbox_toolbar_stack_switcher', Gtk.HBox())
        # ~ tool.add(hbox)
        # ~ self.toolbar.insert(tool, -1)

        ## Separator
        tool = Gtk.SeparatorToolItem.new()
        tool.set_draw(True)
        tool.set_expand(False)
        self.toolbar.insert(tool, -1)

        # Fullscreen toggle button
        # ~ tool = Gtk.ToolItem()
        # ~ tool.set_expand(False)
        # ~ icon = self.srvicm.get_new_image_icon('basico-fullscreen', 24, 24)
        # ~ box = self.srvgui.add_widget('gtk_box_container_icon_fullscreen', Gtk.Box())
        # ~ box.pack_start(icon, False, False, 0)
        # ~ button = Gtk.ToggleButton()
        # ~ button.set_relief(Gtk.ReliefStyle.NONE)
        # ~ button.connect('toggled', self.srvclb.gui_toggle_fullscreen)
        # ~ button.add(box)
        # ~ tool.add(button)
        # ~ tool.set_tooltip_markup('<b>Fullscreen/Window mode</b>')
        # ~ self.toolbar.insert(tool, -1)

        ## Import button
        tool = Gtk.ToolButton()
        tool.set_icon_name('basico-add')
        tool.set_tooltip_markup('<b>Add new SAP Notes, annotations or attachments</b>')
        popover = self.srvgui.add_widget('gtk_popover_toolbutton_add', Gtk.Popover.new(tool))
        tool.connect('clicked', self.srvuif.popover_show, popover)
        self.toolbar.insert(tool, -1)

        ## Popover body
        box = Gtk.VBox(spacing = 0, orientation="vertical")
        box.set_property('margin', 3)
        popover.add(box)


        # Import SAP Notes button
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        hbox = Gtk.HBox()
        icon = self.srvicm.get_image_icon('basico-sapnote', 24, 24)
        label = Gtk.Label()
        label.set_markup('<b>New SAP Note(s)</b>')
        label.set_xalign(0.0)
        hbox.pack_start(icon, False, False, 3)
        hbox.pack_start(label, True, True, 0)
        button.add(hbox)
        box.pack_start(button, False, False, 3)
        popoversn = self.srvgui.add_widget('gtk_popover_button_import_notes', Gtk.Popover.new(button))
        popoversn.set_position(Gtk.PositionType.LEFT)
        button.connect('clicked', self.srvuif.popover_show, popoversn)

        boxsn = Gtk.VBox(spacing = 0, orientation="vertical")
        boxsn.set_property('margin', 3)
        popoversn.add(boxsn)
        widget_import = self.srvgui.add_widget('widget_import', ImportWidget(self.app))
        boxsn.pack_start(widget_import, False, False, 3)

        # Import Annotation button
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        # ~ button.connect('clicked', self.clb_create_annotation)
        hbox = Gtk.HBox()
        icon = self.srvicm.get_image_icon('basico-annotation', 24, 24)
        label = Gtk.Label()
        label.set_markup('<b>New annotation</b>')
        label.set_xalign(0.0)
        hbox.pack_start(icon, False, False, 3)
        hbox.pack_start(label, True, True, 0)
        button.add(hbox)
        box.pack_start(button, False, False, 3)

        popoveran = self.srvgui.add_widget('gtk_popover_button_create_annotation', Gtk.Popover.new(button))
        popoveran.set_position(Gtk.PositionType.LEFT)
        button.connect('clicked', self.srvuif.popover_show, popoveran)

        boxan = Gtk.VBox(spacing = 0, orientation="vertical")
        boxan.set_property('margin', 3)
        popoveran.add(boxan)

        ## New annotation
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        hbox = Gtk.HBox()
        icon = self.srvicm.get_new_image_icon('basico-annotation')
        label = Gtk.Label()
        label.set_markup('<b>New annotation</b>')
        label.set_xalign(0.0)
        hbox.pack_start(icon, False, False, 3)
        hbox.pack_start(label, True, True, 0)
        button.add(hbox)
        button.set_tooltip_markup('<b>Create a new annotation (not linked to any SAP Note)</b>')
        # ~ button.connect('clicked', self.clb_create_annotation)
        boxan.pack_start(button, False, False, 3)

        ### New annotation from template
        # ~ combobox = self.combobox_templates()
        # ~ boxan.pack_start(combobox, False, False, 3)

        # ~ widget_import = self.srvgui.add_widget('widget_import', ImportWidget(self.app))
        # ~ boxan.pack_start(widget_import, False, False, 3)

        ## Bookmarks
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        icon = self.srvicm.get_new_image_icon('basico-bookmarks', 24, 24)
        box = Gtk.Box()
        box.pack_start(icon, False, False, 0)
        button = self.srvgui.add_widget('gtk_togglebutton_bookmarks', Gtk.ToggleButton())
        button.set_relief(Gtk.ReliefStyle.NONE)
        sigid = button.connect('toggled', self.srvclb.gui_visor_sapnotes_show_bookmarks)
        self.srvgui.set_key_value('gtk_togglebutton_bookmarks_signal', sigid)
        button.add(box)
        tool.add(button)
        tool.set_tooltip_markup('<b>Show bookmarks</b>')
        self.toolbar.insert(tool, -1)

        ## Show/Hide Menuviews
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        icon = self.srvicm.get_new_image_icon('basico-collection', 18, 18)
        box = Gtk.Box()
        box.pack_start(icon, False, False, 3)
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_active(False)
        self.srvgui.add_widget('gtk_togglebutton_toolbar_menuview', button)
        self.srvgui.add_signal('gtk_togglebutton_toolbar_menuview', 'toggled', 'self.srvclb.gui_menuview_toggled')
        button.add(box)
        tool.add(button)
        tool.set_tooltip_markup('<b>Show/Hide views</b>')
        self.toolbar.insert(tool, -1)

        # Toolbar initial settings
        self.set_visible(True)
        self.set_no_show_all(False)
        self.toolbar.set_hexpand(True)

    def get_services(self):
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvclb = self.get_service('Callbacks')

    def _on_show_bookmarks(self, *args):
        self.log.debug("Hola")

    def completion_match_func(self, completion, key, iter):
        model = completion.get_model()
        text = model.get_value(iter, 0)
        if key.upper() in text.upper():
            return True
        return False

    def combobox_templates(self, *args):
        tpl_aids = self.srvant.get_annotations_by_type('Template')
        # ~ self.log.debug(tpl_aids)

        model = Gtk.ListStore(Pixbuf, str, str)
        icon = self.srvicm.get_pixbuf_icon('basico-annotation-type-template', 32)
        first = model.append([icon, '', '<b>Templates</b>'])
        for aid in tpl_aids:
            atype = self.srvant.get_metadata_value(aid, 'Type')
            icon = self.srvicm.get_pixbuf_icon('basico-annotation-type-%s' % atype.lower(), 32)
            title = self.srvant.get_title(aid)
            # ~ self.log.debug("AID(%s) - Title(%s)", aid, title)
            model.append([icon, aid, title])

        templates = Gtk.ComboBox.new_with_model(model)
        templates.set_active_iter(first)
        # ~ templates.connect('changed', self.clb_template_changed)

        renderer = Gtk.CellRendererPixbuf()
        templates.pack_start(renderer, False)
        templates.add_attribute(renderer, "pixbuf", 0)

        renderer = Gtk.CellRendererText()
        renderer.set_visible(False)
        templates.pack_start(renderer, True)
        templates.add_attribute(renderer, "text", 1)

        renderer = Gtk.CellRendererText()
        templates.pack_start(renderer, True)
        templates.add_attribute(renderer, "markup", 2)

        templates.show_all()
        return templates

    def entry_search(self, *args):
        entry = self.srvgui.get_widget('gtk_entry_filter_visor')
        stack_visors = self.srvgui.get_widget('gtk_stack_visors')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        term = entry.get_text()

        stack_visor = stack_visors.get_visible_child_name()
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        completion_model.clear()
        self.log.debug("Search for '%s'" % term)
        bag = self.srvdtb.search(term)
        visor_sapnotes.populate(bag)
        ebuffer = entry.get_buffer()
        ebuffer.delete_text(0, -1)
        self.log.info("Found %d SAP Notes for term '%s'" % (len(bag), term))

    def entry_filter(self, *args):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        visor_sapnotes.filter()
