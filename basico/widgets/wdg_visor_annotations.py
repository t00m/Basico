#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_visor_annotations.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAPNoteViewVisor widgets
"""

import os
from os.path import sep as SEP
from html import escape
import glob
import json
import html
from enum import IntEnum

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango
from gi.repository import GObject

from basico.core.mod_env import LPATH, ATYPES
from basico.core.mod_wdg import BasicoWidget
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_import import ImportWidget

class COLUMN(IntEnum):
    AID = 0
    ICON = 1
    CHECKBOX = 2
    SID = 3
    TITLE = 4
    COMPONENT = 5
    TYPE = 6
    SCOPE = 7
    PRODUCT = 8
    PRIORITY = 9
    UPDATED = 10
    UPDATED_TIMESTAMP = 11
    CREATED = 12
    CREATED_TIMESTAMP = 13


class AnnotationsVisor(BasicoWidget, Gtk.HBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.HBox.__init__(self, app)
        self.set_homogeneous(False)
        self.bag = []
        self.__get_services()
        self.__setup_panel()
        self.__set_initial_panel_button_status()
        self.__setup_visor()
        self.icons = {}
        self.icons['type'] = {}
        for atype in ATYPES:
            self.icons['type'][atype.lower()] = self.srvicm.get_pixbuf_icon('basico-annotation-type-%s' % atype.lower(), 32)
        self.log.debug("Annotation Visor initialized")

        # ~ self.connect_signals()


    def __get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvuif = self.get_service("UIF")
        self.srvutl = self.get_service("Utils")
        self.srvant = self.get_service('Annotation')


    def __set_initial_panel_button_status(self):
        # Categories
        self.srvgui.set_key_value('ANNOTATIONS_CATEGORY_INBOX_VISIBLE', True)
        self.srvgui.set_key_value('ANNOTATIONS_CATEGORY_DRAFTS_VISIBLE', False)
        self.srvgui.set_key_value('ANNOTATIONS_CATEGORY_ARCHIVED_VISIBLE', False)

        # Types
        for atype in ATYPES:
            self.srvgui.set_key_value('ANNOTATIONS_TYPE_%s_VISIBLE' % atype.upper(), True)

        # Priorty
        for priority in ['High', 'Normal', 'Low']:
            self.srvgui.set_key_value('ANNOTATIONS_PRIORITY_%s_VISIBLE' % priority.upper(), True)


    def __sort_by_timestamp(self):
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        sorted_model.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP, Gtk.SortType.DESCENDING)


    def __setup_panel(self):
        vbox_main = Gtk.VBox()
        self.pack_start(vbox_main, False, False, 3)
        # ~ separator = Gtk.Separator(orientation = Gtk.Orientation.VERTICAL)
        # ~ self.pack_start(separator, False, False, 3)
        vbox_main.set_hexpand(False)
        # ~ vbox_main.set_property('margin-top', 6)
        vbox_main.set_property('margin-left', 6)
        vbox_main.set_property('margin-right', 6)
        vbox_main.set_property('margin-bottom', 3)

        def create_panel_elem_button(icon, title):
            button = self.srvgui.add_widget('gtk_togglebutton_%s' % title, Gtk.ToggleButton())
            button.set_relief(Gtk.ReliefStyle.NONE)
            icon = self.srvicm.get_image_icon(icon, 36, 36)
            label = Gtk.Label('')
            label.set_markup('%s' % title.capitalize())
            hbox_cat_elem = Gtk.HBox()
            hbox_cat_elem.set_hexpand(False)
            hbox_cat_elem.pack_start(icon, False, False, 3)
            hbox_cat_elem.pack_start(label, False, False, 3)
            button.add(hbox_cat_elem)

            return button

        # Separator
        # ~ separator = Gtk.Separator()
        # ~ vbox_main.pack_start(separator, False, False, 6)

        # Scope filter
        hbox_scope = Gtk.VBox()
        label = Gtk.Label()
        label.set_markup("<big><b>Scope </b></big>")
        label.set_xalign(0.0)
        model = Gtk.ListStore(str)
        scope = Gtk.ComboBox.new_with_model(model)
        signal = scope.connect('changed', self.__clb_scope_changed)
        self.srvgui.add_signal('gtk_combobox_filter_scope', 'changed', signal)
        self.srvgui.add_widget('gtk_combobox_filter_scope', scope)
        renderer = Gtk.CellRendererText()
        scope.pack_start(renderer, True)
        scope.add_attribute(renderer, "markup", 0)
        # ~ hbox_scope.pack_start(label, False, False, 0)
        hbox_scope.pack_start(scope, True, True, 0)
        vbox_main.pack_start(hbox_scope, False, False, 6)

        # Product filter
        hbox_product = Gtk.VBox()
        label = Gtk.Label()
        label.set_markup("<big><b>Product </b></big>")
        label.set_xalign(0.0)
        model = Gtk.ListStore(str)
        product = Gtk.ComboBox.new_with_model(model)
        signal = product.connect('changed', self.__clb_product_changed)
        self.srvgui.add_signal('gtk_combobox_filter_product', 'changed', signal)
        self.srvgui.add_widget('gtk_combobox_filter_product', product)
        renderer = Gtk.CellRendererText()
        product.pack_start(renderer, True)
        product.add_attribute(renderer, "markup", 0)
        # ~ hbox_product.pack_start(label, False, False, 0)
        hbox_product.pack_start(product, True, True, 0)
        vbox_main.pack_start(hbox_product, False, False, 6)

        hbox_main = Gtk.HBox()
        hbox_main.set_homogeneous(True)
        vbox_main.pack_start(hbox_main, False, False, 0)

        # Separator
        # ~ separator = Gtk.Separator()
        # ~ vbox_main.pack_start(separator, False, False, 6)

        # Categories
        button = self.srvgui.add_widget('gtk_togglebutton_categories', Gtk.ToggleButton())
        button.set_relief(Gtk.ReliefStyle.NORMAL)
        icon = self.srvicm.get_image_icon('basico-category', 24, 24)
        label = Gtk.Label('')
        label.set_markup('<big><b>Categories</b></big>')
        hbox_cat = Gtk.HBox()
        hbox_cat.set_hexpand(False)
        # ~ hbox_cat.pack_start(icon, False, False, 3)
        hbox_cat.pack_start(label, False, False, 3)
        button.add(hbox_cat)
        vbox_main.pack_start(button, False, False, 6)

        revealer = self.srvgui.add_widget('gtk_revealer_annotations_categories', Gtk.Revealer())
        vbox_revealer = Gtk.VBox()
        vbox_revealer.set_hexpand(False)

        for name in ['inbox', 'drafts', 'archived']:
            button = create_panel_elem_button('basico-%s' % name.lower(), name)
            self.srvgui.add_widget('gtk_button_category_%s' % name, button)
            vbox_revealer.pack_start(button, False, False, 2)

        revealer.add(vbox_revealer)
        vbox_main.pack_start(revealer, False, False, 3)

        # Types
        button = self.srvgui.add_widget('gtk_togglebutton_types', Gtk.ToggleButton())
        button.set_relief(Gtk.ReliefStyle.NORMAL)
        icon = self.srvicm.get_image_icon('basico-type', 24, 24)
        label = Gtk.Label('')
        label.set_markup('<big><b>Types</b></big>')
        hbox_type = Gtk.HBox()
        hbox_type.set_hexpand(False)

        # ~ hbox_type.pack_start(icon, False, False, 3)
        hbox_type.pack_start(label, False, False, 3)
        button.add(hbox_type)
        vbox_main.pack_start(button, False, False, 0)

        revealer = self.srvgui.add_widget('gtk_revealer_annotations_types', Gtk.Revealer())
        vbox_revealer = Gtk.VBox()
        vbox_revealer.set_hexpand(False)

        hbox_sel = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(True)
        switch.set_state(True)
        switch.connect('state-set', self.__clb_switch_selection_atypes)
        label_select = Gtk.Label()
        label_select.set_markup("<b>All selected</b>")
        label = self.srvgui.add_widget('gtk_label_switch_select_atypes', label_select)
        hbox_sel.pack_start(label, False, False, 6)
        hbox_sel.pack_start(switch, False, False, 6)
        vbox_revealer.pack_start(hbox_sel, False, False, 6)

        for name in ATYPES:
            button = create_panel_elem_button('basico-annotation-type-%s' % name.lower(), name.lower())
            self.srvgui.add_widget('gtk_button_type_%s' % name.lower(), button)
            button.set_active(True)
            vbox_revealer.pack_start(button, False, False, 2)

        revealer.add(vbox_revealer)
        vbox_main.pack_start(revealer, False, False, 6)

        # ~ separator = Gtk.Separator()
        # ~ vbox_main.pack_start(separator, False, False, 6)


        return vbox_main


    def __clb_set_visible_categories(self, togglebutton):
        types = self.srvgui.get_widget('gtk_togglebutton_types')
        revealer = self.srvgui.get_widget('gtk_revealer_annotations_categories')

        active = togglebutton.get_active()
        if active:
            types.set_active(False)
        revealer.set_reveal_child(active)


    def __clb_set_visible_types(self, togglebutton):
        categories = self.srvgui.get_widget('gtk_togglebutton_categories')
        revealer = self.srvgui.get_widget('gtk_revealer_annotations_types')

        active = togglebutton.get_active()
        if active:
            categories.set_active(False)
        revealer.set_reveal_child(active)


    def __clb_set_visible_priority(self, togglebutton):
        categories = self.srvgui.get_widget('gtk_togglebutton_categories')
        revealer = self.srvgui.get_widget('gtk_revealer_annotations_priority')

        active = togglebutton.get_active()
        if active:
            priority.set_active(False)
        revealer.set_reveal_child(active)


    def __clb_set_visible_category(self, togglebutton, title):
        active = togglebutton.get_active()
        self.srvgui.set_key_value('ANNOTATIONS_CATEGORY_%s_VISIBLE' % title.upper(), active)
        self.__set_bag()
        self.populate()


    def __clb_set_visible_annotation_type(self, togglebutton, atype):
        active = togglebutton.get_active()
        self.srvgui.set_key_value('ANNOTATIONS_TYPE_%s_VISIBLE' % atype.upper(), active)
        self.__set_bag()
        self.populate()


    def __clb_set_visible_priority(self, togglebutton, title):
        active = togglebutton.get_active()
        self.srvgui.set_key_value('ANNOTATIONS_PRIORITY_%s_VISIBLE' % title.upper(), active)
        self.__set_bag()
        self.populate()


    def __setup_visor(self):
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        treeview = self.srvgui.add_widget('visor_annotation_treeview', Gtk.TreeView())
        scr.add(treeview)
        scr.set_hexpand(True)
        self.pack_start(scr, True, True, 0)

        # Setup model
        model = Gtk.TreeStore(
            str,        # Annotation Id
            Pixbuf,     # Icon
            int,        # checkbox
            str,        # sid
            str,        # title
            str,        # component
            str,        # type
            str,        # Scope
            str,        # Product
            str,        # priority
            str,        # last update
            str,        # Timestamp updated
            str,        # Annotation created
            str,        # Timestamp created
        )
        self.srvgui.add_widget('gtk_model_annotation', model)

        # Setup columns
        def get_column_header_widget(title, icon_name=None, width=28, height=28):
            hbox = Gtk.HBox()
            icon = self.srvicm.get_new_image_icon(icon_name, width, height)
            label = Gtk.Label()
            label.set_markup("<b>%s</b>" % title)
            # ~ label.modify_font(Pango.FontDescription('Monospace 10'))
            hbox.pack_start(icon, False, False, 3)
            hbox.pack_start(label, True, True, 3)
            hbox.show_all()
            return hbox

        # Annotation key
        self.renderer_key = Gtk.CellRendererText()
        self.column_key = Gtk.TreeViewColumn('Key', self.renderer_key, text=COLUMN.AID)
        self.column_key.set_visible(False)
        self.column_key.set_expand(False)
        self.column_key.set_clickable(False)
        self.column_key.set_sort_indicator(True)
        treeview.append_column(self.column_key)

        # Annotation Icon
        self.renderer_icon = Gtk.CellRendererPixbuf()
        self.renderer_icon.set_alignment(0.0, 0.5)
        self.column_icon = Gtk.TreeViewColumn('', self.renderer_icon, pixbuf=COLUMN.ICON)
        # ~ widget = get_column_header_widget('', 'basico-type')
        # ~ self.column_icon.set_widget(widget)
        self.column_icon.set_visible(True)
        self.column_icon.set_expand(False)
        self.column_icon.set_clickable(True)
        self.column_icon.set_sort_indicator(True)
        self.column_icon.set_sort_column_id(COLUMN.TYPE)
        treeview.append_column(self.column_icon)

        # Annotation Checkbox
        self.renderer_checkbox = Gtk.CellRendererToggle()
        self.renderer_checkbox.connect("toggled", self.__clb_row_toggled)
        self.column_checkbox = Gtk.TreeViewColumn('', self.renderer_checkbox, active=COLUMN.CHECKBOX)
        widget = get_column_header_widget('', 'basico-check-accept')
        self.column_checkbox.set_widget(widget)
        self.column_checkbox.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_checkbox.set_visible(True)
        self.column_checkbox.set_expand(False)
        # ~ self.column_checkbox.set_clickable(True)
        # ~ self.column_checkbox.set_sort_indicator(True)
        # ~ self.column_checkbox.set_sort_column_id(2)
        self.column_checkbox.set_property('spacing', 50)
        treeview.append_column(self.column_checkbox)

        # Annotation Id
        self.renderer_sid = Gtk.CellRendererText()
        self.renderer_sid.set_property('xalign', 1.0)
        self.renderer_sid.set_property('height', 36)
        self.renderer_sid.set_property('background', '#F0E3E3')
        self.column_sid = Gtk.TreeViewColumn('SAP Note Id', self.renderer_sid, markup=COLUMN.SID)
        widget = get_column_header_widget('SAP Note Id', 'basico-sid')
        self.column_sid.set_widget(widget)
        self.column_sid.set_visible(True)
        self.column_sid.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_sid.set_expand(False)
        self.column_sid.set_clickable(True)
        self.column_sid.set_sort_indicator(True)
        # ~ self.column_sid.set_sort_column_id(0)
        treeview.append_column(self.column_sid)

        # Annotation title
        self.renderer_title = Gtk.CellRendererText()
        self.renderer_title.set_property('background', '#FFFEEA')
        self.renderer_title.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_title = Gtk.TreeViewColumn('Title', self.renderer_title, markup=COLUMN.TITLE)
        widget = get_column_header_widget('Title', 'basico-tag')
        self.column_title.set_widget(widget)
        self.column_title.set_visible(True)
        self.column_title.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_title.set_expand(True)
        self.column_title.set_clickable(True)
        self.column_title.set_sort_indicator(True)
        self.column_title.set_sort_column_id(COLUMN.TITLE)
        treeview.append_column(self.column_title)

        # Annotation Component
        self.renderer_component = Gtk.CellRendererText()
        self.renderer_component.set_property('background', '#E3E3F0')
        self.column_component = Gtk.TreeViewColumn('Component', self.renderer_component, markup=COLUMN.COMPONENT)
        widget = get_column_header_widget('Component', 'basico-component')
        self.column_component.set_widget(widget)
        self.column_component.set_visible(False)
        self.column_component.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_component.set_expand(False)
        self.column_component.set_clickable(True)
        self.column_component.set_sort_indicator(True)
        self.column_component.set_sort_column_id(COLUMN.COMPONENT)
        treeview.append_column(self.column_component)

        # Annotation Type
        self.renderer_component = Gtk.CellRendererText()
        self.renderer_component.set_property('background', '#E3E3F0')
        self.column_component = Gtk.TreeViewColumn('Type', self.renderer_component, markup=COLUMN.TYPE)
        # ~ widget = get_column_header_widget('Type', 'basico-type')
        # ~ self.column_component.set_widget(widget)
        self.column_component.set_visible(False)
        self.column_component.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_component.set_expand(False)
        self.column_component.set_clickable(True)
        self.column_component.set_sort_indicator(True)
        self.column_component.set_sort_column_id(COLUMN.TYPE)
        treeview.append_column(self.column_component)

        # Annotation Scope
        self.renderer_scope = Gtk.CellRendererText()
        self.renderer_scope.set_property('background', '#E3F1E3')
        self.column_scope = Gtk.TreeViewColumn('Scope', self.renderer_scope, markup=COLUMN.SCOPE)
        widget = get_column_header_widget('Scope', 'basico-scope')
        self.column_scope.set_widget(widget)
        self.column_scope.set_visible(True)
        self.column_scope.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_scope.set_expand(False)
        self.column_scope.set_clickable(True)
        self.column_scope.set_sort_indicator(True)
        self.column_scope.set_sort_column_id(COLUMN.SCOPE)
        treeview.append_column(self.column_scope)

        # Annotation Product
        self.renderer_type = Gtk.CellRendererText()
        self.renderer_type.set_property('background', '#DADAFF')
        # ~ self.renderer_type.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_type = Gtk.TreeViewColumn('Type', self.renderer_type, markup=COLUMN.PRODUCT)
        widget = get_column_header_widget('Product', 'basico-type')
        self.column_type.set_widget(widget)
        self.column_type.set_visible(True)
        self.column_type.set_expand(False)
        self.column_type.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_type.set_clickable(True)
        self.column_type.set_sort_indicator(True)
        self.column_type.set_sort_column_id(COLUMN.PRODUCT)
        treeview.append_column(self.column_type)

        # Annotation Priority
        self.renderer_priority = Gtk.CellRendererText()
        self.renderer_priority.set_property('background', '#e4f1f1')
        self.column_priority = Gtk.TreeViewColumn('Priority', self.renderer_priority, markup=COLUMN.PRIORITY)
        widget = get_column_header_widget('Priority', 'basico-priority')
        self.column_priority.set_widget(widget)
        self.column_priority.set_visible(True)
        self.column_priority.set_expand(False)
        self.column_priority.set_clickable(True)
        self.column_priority.set_sort_indicator(True)
        self.column_priority.set_sort_column_id(COLUMN.PRIORITY)
        treeview.append_column(self.column_priority)

        # Annotation Updated On
        self.renderer_updated = Gtk.CellRendererText()
        self.renderer_updated.set_property('background', '#FFE6D1')
        self.column_updated = Gtk.TreeViewColumn('Updated', self.renderer_updated, markup=COLUMN.UPDATED)
        widget = get_column_header_widget('Updated', 'basico-chronologic')
        self.column_updated.set_widget(widget)
        self.column_updated.set_visible(True)
        self.column_updated.set_expand(False)
        self.column_updated.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_updated.set_clickable(True)
        self.column_updated.set_sort_indicator(True)
        self.column_updated.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP)
        self.column_updated.set_sort_order(Gtk.SortType.DESCENDING)
        model.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP, Gtk.SortType.DESCENDING)
        treeview.append_column(self.column_updated)

        # Timestamp updated
        self.renderer_timestamp_updated = Gtk.CellRendererText()
        self.column_timestamp_updated = Gtk.TreeViewColumn('Timestamp updated', self.renderer_timestamp_updated, text=COLUMN.UPDATED_TIMESTAMP)
        self.column_timestamp_updated.set_visible(False)
        self.column_timestamp_updated.set_expand(False)
        self.column_timestamp_updated.set_clickable(False)
        self.column_timestamp_updated.set_sort_indicator(True)
        self.column_timestamp_updated.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP)
        self.column_timestamp_updated.set_sort_order(Gtk.SortType.ASCENDING)
        treeview.append_column(self.column_timestamp_updated)

        # Annotation Created On
        self.renderer_created = Gtk.CellRendererText()
        self.renderer_created.set_property('background', '#FFE6D1')
        self.column_created = Gtk.TreeViewColumn('Created', self.renderer_created, markup=COLUMN.CREATED)
        widget = get_column_header_widget('Created', 'basico-chronologic')
        self.column_created.set_widget(widget)
        self.column_created.set_visible(False)
        self.column_created.set_expand(False)
        self.column_created.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_created.set_clickable(True)
        self.column_created.set_sort_indicator(True)
        self.column_created.set_sort_column_id(COLUMN.CREATED_TIMESTAMP)
        self.column_created.set_sort_order(Gtk.SortType.DESCENDING)
        model.set_sort_column_id(COLUMN.CREATED_TIMESTAMP, Gtk.SortType.DESCENDING)
        treeview.append_column(self.column_created)

        # Timestamp
        self.renderer_timestamp_created = Gtk.CellRendererText()
        self.column_timestamp_created = Gtk.TreeViewColumn('Timestamp created', self.renderer_timestamp_created, text=COLUMN.CREATED_TIMESTAMP)
        self.column_timestamp_created.set_visible(False)
        self.column_timestamp_created.set_expand(False)
        self.column_timestamp_created.set_clickable(False)
        self.column_timestamp_created.set_sort_indicator(True)
        self.column_timestamp_created.set_sort_column_id(COLUMN.CREATED_TIMESTAMP)
        self.column_timestamp_created.set_sort_order(Gtk.SortType.ASCENDING)
        treeview.append_column(self.column_timestamp_created)

        # Treeview properties
        treeview.set_can_focus(False)
        treeview.set_enable_tree_lines(True)
        treeview.set_headers_visible(True)
        treeview.set_enable_search(True)
        treeview.set_hover_selection(False)
        treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        treeview.set_enable_tree_lines(True)
        treeview.set_level_indentation(10)
        treeview.connect('button_press_event', self.__clb_row_right_click)

        treeview.modify_font(Pango.FontDescription('Monospace 9'))

        # DOC: In order to have a Gtk.Widged with sorting and filtering
        # capabilities, you have to filter the model first, and use this
        # new model to create the sorted model. Then, attach the sorted
        # model to the treeview...

        # Treeview filtering:
        visible_filter = self.srvgui.add_widget('visor_annotation_visible_filter', model.filter_new())
        visible_filter.set_visible_func(self.__visible_function)

        # TreeView sorting
        sorted_model = Gtk.TreeModelSort(model=visible_filter)
        self.srvgui.add_widget('visor_annotation_sorted_model', sorted_model)
        sorted_model.set_sort_func(COLUMN.AID, self.__sort_function, None)

        # Selection
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        selection.connect('changed', self.__clb_row_changed)

        # Set model (filtered and sorted)
        sorted_model.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP, Gtk.SortType.ASCENDING)
        treeview.set_model(sorted_model)

        # Other signals
        treeview.connect('row-activated', self.__clb_row_double_click)

        self.show_all()


    def __sort_function(self, model, row1, row2, user_data):
        sort_column = 0

        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)

        if value1 < value2:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1


    def __visible_function(self, model, itr, data):
        entry = self.srvgui.get_widget('gtk_entry_filter_visor')
        text = self.srvutl.clean_html(entry.get_text())
        title = model.get(itr, COLUMN.TITLE)[0]
        scope = model.get(itr, COLUMN.SCOPE)[0]
        product = model.get(itr, COLUMN.PRODUCT)[0]
        match = text.upper() in title.upper()

        cmb_scope = self.srvgui.get_widget('gtk_combobox_filter_scope')
        scope_filter = self.srvutl.clean_html(self.srvuif.get_combobox_text(cmb_scope, 0))
        cmb_product = self.srvgui.get_widget('gtk_combobox_filter_product')
        product_filter = self.srvutl.clean_html(self.srvuif.get_combobox_text(cmb_product, 0))


        if scope_filter in [scope, 'All', '', 'Scope']:
            match = match and True
        elif scope_filter == 'None' and scope == '':
            match = True
        else:
            match = match and False

        if product_filter in [product, 'All', '', 'Product']:
            match = match and True
        elif product_filter == 'None' and product == '':
            match = True
        else:
            match = match and False

        return match


    def update_total_annotations_count(self):
        visible_filter = self.srvgui.get_widget('visor_annotation_visible_filter')
        statusbar = self.srvgui.get_widget('widget_statusbar')
        lblnotescount = self.srvgui.get_widget('gtk_label_total_notes')
        lblnotescount.modify_font(Pango.FontDescription('Monospace 12'))
        total = self.srvant.get_total()
        count = len(visible_filter)
        selected = len(self.rows_toggled())
        lblnotescount.set_markup("<b><small>%d</small>/%d/<big>%d</big></b>" % (selected, count, total))
        msg = 'View populated with %d annotations' % count
        # ~ self.srvuif.statusbar_msg(msg)


    def get_visible_filter(self):
        return self.visible_filter


    def row_current(self, *args):
        treeview = self.srvgui.get_widget('visor_annotation_treeview')
        selection = treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            aid = model.get(treeiter, 0)[0]
            # ~ self.log.debug(aid)
        else:
            aid = ''
        return aid


    def row_previous(self, *args):
        treeview = self.srvgui.get_widget('visor_annotation_treeview')
        selection = treeview.get_selection()
        model, iter_current = selection.get_selected()
        if iter_current is not None:
            iter_previous = model.iter_previous(iter_current)
            if iter_previous:
                selection.select_iter(iter_previous)
                widget_annotation = self.srvgui.get_widget('widget_annotation')
                widget_annotation.preview()


    def row_next(self, *args):
        treeview = self.srvgui.get_widget('visor_annotation_treeview')
        selection = treeview.get_selection()
        model, iter_current = selection.get_selected()
        if iter_current is not None:
            iter_next = model.iter_next(iter_current)
            if iter_next:
                selection.select_iter(iter_next)
                path, col = treeview.get_cursor()
                row = self.srvuif.tree_path_to_row(path)
                treeview.scroll_to_cell(row, column=None, use_align=False, row_align=0.5, col_align=0)
                widget_annotation = self.srvgui.get_widget('widget_annotation')
                widget_annotation.preview()


    def rows_toggled(self):
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        selected = []

        def get_toggled_rows(model, path, itr):
            aid = sorted_model.get(itr, COLUMN.AID)[0]
            checked = sorted_model.get(itr, COLUMN.CHECKBOX)[0]
            if checked:
                selected.append(str(aid))
        sorted_model.foreach(get_toggled_rows)

        return selected


    def __clb_row_changed(self, selection):
        try:
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                component = model[treeiter][COLUMN.COMPONENT]
                if component == 'Annotation':
                    aid = model[treeiter][COLUMN.AID]
                    is_valid = self.srvant.is_valid(aid)
                    if is_valid:
                        widget_annotation = self.srvgui.get_widget('widget_annotation')
                        widget_annotation.set_metadata_to_widget(aid)
                        # ~ widget_annotation.preview()
                else:
                    aid = None
                    # ~ self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
        except Exception as error:
            pass
            # ~ head = "Error reading annotation's contents"
            # ~ body = "<i>%s</i>\n\n" % error
            # ~ body += "As a workaround, a new file will be created"
            # ~ dialog = self.srvuif.message_dialog_error(head, body)
            # ~ self.log.debug(error)
            # ~ self.log.debug(self.get_traceback())
            # ~ dialog.run()
            # ~ dialog.destroy()
            #FIXME: create an empty file for contents


    def __clb_row_toggled(self, cell, path):
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        model = sorted_model.get_model()
        rpath = sorted_model.convert_path_to_child_path(Gtk.TreePath(path))
        model[rpath][COLUMN.CHECKBOX] = not model[rpath][COLUMN.CHECKBOX]
        self.update_total_annotations_count()


    def __get_node(self, key, icon, checkbox, sid, title, component, atype, scope='', sntype='', priority='', updated='', ts_updated='', created='', ts_created=''):
        # Add completion entries
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        title = self.srvutl.clean_html(title)
        completion_model.append([title])

        node = []
        node.append(key)
        node.append(icon)
        node.append(checkbox)
        node.append(sid)
        node.append(title)
        node.append(component)
        node.append(atype)
        node.append(scope)
        node.append(sntype)
        node.append(priority)
        node.append(updated)
        node.append(ts_updated)
        node.append(created)
        node.append(ts_created)
        return node


    def __set_bag(self, annotations=None):
        self.bag = annotations


    def get_bag(self):
        return self.bag


    def populate(self, annotations=None):
        treeview = self.srvgui.get_widget('visor_annotation_treeview')
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        model = self.srvgui.get_widget('gtk_model_annotation')
        self.column_sid.set_visible(False)
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        completion_model.clear()

        treeview.set_model(None)
        model.clear()

        if annotations is None:
            annotations = self.get_bag()
            if annotations is None:
                annotations = self.srvant.get_all()
            else:
                self.log.debug("Displaying last query")
        else:
            self.log.debug("Displaying following annotations: %s", annotations)
            self.__set_bag(annotations)

        dcats = {}
        snpids = {}
        nodes = []
        bag = set()

        for fname in annotations:
            try:
                with open(fname, 'r') as fa:
                    try:
                        try:
                            annotation = json.load(fa)
                        except Exception as error:
                            self.log.error("Annotation: %s", fname)
                            self.log.error(error)
                        # Get Scope
                        try:
                            scope = annotation['Scope']
                        except:
                            scope = ''

                        # Get Product
                        try:
                            product = annotation['Product']
                        except:
                            product = ''

                        # ~ self.log.debug("Annotation: %s", annotation['Title'])
                        category = annotation['Category']
                        atype = annotation['Type']
                        cat_key = 'ANNOTATIONS_CATEGORY_%s_VISIBLE' % category.upper()
                        type_key = 'ANNOTATIONS_TYPE_%s_VISIBLE' % atype.upper()
                        category_active = self.srvgui.get_key_value(cat_key)
                        try:
                            type_active = self.srvgui.get_key_value(type_key)
                        except Exception as error:
                            self.log.error(error)
                            type_active = True
                        if category_active:
                            if type_active:
                                ppid = None
                                sid = self.srvant.get_sid(annotation['AID'])
                                try:
                                    icon = self.icons['type']['%s' % atype.lower()]
                                except:
                                    icon = None
                                if sid != '0000000000':
                                    title = "<b>[SAP Note %d]</b> %s" % (int(sid), annotation['Title'])
                                else:
                                    title = annotation['Title']

                                try:
                                    annotation['Priority']
                                except:
                                    annotation['Priority'] = 'Normal'

                                node = self.__get_node(   annotation['AID'],
                                                        icon,
                                                        False,
                                                        str(int(sid)),
                                                        title,
                                                        annotation['Component'],
                                                        annotation['Type'],
                                                        scope,
                                                        product,
                                                        annotation['Priority'],
                                                        self.srvutl.fuzzy_date_from_timestamp(annotation['Timestamp']),
                                                        annotation['Timestamp'],
                                                        self.srvutl.fuzzy_date_from_timestamp(annotation['Created']),
                                                        annotation['Created']
                                                    )
                                nodes.append(node)
                    except Exception as error:
                        self.log.error(error)
                        self.log.error(self.get_traceback())
            except Exception as error:
                # Whenever an annotation is deleted, after reloading
                # the view, it fails. Then, skip it
                pass

        for node in nodes:
            model.append(None, node)

        treeview.set_model(sorted_model)
        self.__sort_by_timestamp()
        self.__update_panel_values()
        self.update_total_annotations_count()


    # ~ def __clb_preview(self, button, aid):
        # ~ self.srvclb.action_annotation_preview(aid)


    # ~ def __clb_edit(self, button, aid):
        # ~ self.srvclb.action_annotation_edit(aid)


    def __clb_row_double_click(self, treeview, row, col):
        try:
            selection = treeview.get_selection()
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                component = model[treeiter][COLUMN.COMPONENT]
                if component == 'Annotation':
                    aid = model[treeiter][COLUMN.AID]
                    is_valid = self.srvant.is_valid(aid)
                    if is_valid:
                        # ~ self.srvclb.action_annotation_preview(aid)
                        raise # Enabled with purpose. Disable when necessary
        except Exception as error:
            self.log.error(error)


    def __clb_row_right_click(self, treeview, event, data=None):
        treeview = self.srvgui.get_widget('visor_annotation_treeview')
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.x = x = int(event.x)
            rect.y = y = int(event.y)
            pthinfo = treeview.get_path_at_pos(x,y)
            if pthinfo is not None:
                path,col,cellx,celly = pthinfo
                model = treeview.get_model()
                treeiter = model.get_iter(path)
                component = model[treeiter][COLUMN.COMPONENT]
                aid = model[treeiter][COLUMN.AID]
                popover = self.srvgui.add_widget('gtk_popover_visor_row', Gtk.Popover.new(treeview))
                popover.set_pointing_to(rect)
                box = self.__build_popover(aid, popover, component)
                if box is not None:
                    visor_annotations = self.srvgui.get_widget('visor_annotations')
                    width, height = visor_annotations.get_size_request()
                    popover.add(box)
                    self.srvclb.gui_show_popover(None, popover)



    def __build_popover(self, aid, popover, component):
        sid = self.srvant.get_sid(aid)

        def get_popover_button(text, icon_name):
            button = Gtk.Button()
            button.set_relief(Gtk.ReliefStyle.NONE)
            hbox = Gtk.HBox()
            icon = self.srvicm.get_new_image_icon(icon_name, 24, 24)
            hbox.pack_start(icon, False, False, 3)
            if len(text) > 0:
                lbltext = Gtk.Label()
                lbltext.set_xalign(0.0)
                lbltext.set_markup('%s' % text)
                hbox.pack_start(lbltext, True, True, 3)
            button.add(hbox)
            return button

        if component == 'Annotation':
            box = Gtk.Box(spacing = 3, orientation="vertical")

            hbox_sel = Gtk.HBox()
            button = get_popover_button("", 'basico-check-all')
            button.set_tooltip_markup("Select all")
            button.connect('clicked', self.__clb_select_all, True)
            hbox_sel.pack_start(button, True, False, 0)

            button = get_popover_button("", 'basico-check-none')
            button.set_tooltip_markup("Select none")
            button.connect('clicked', self.__clb_select_all, False)
            hbox_sel.pack_start(button, True, False, 0)

            button = get_popover_button("", 'basico-check-invert')
            button.set_tooltip_markup("Invert selection")
            button.connect('clicked', self.__clb_select_all, None)
            hbox_sel.pack_start(button, True, False, 0)

            box.pack_start(hbox_sel, False, False, 0)
            box.show_all()

            if len(self.rows_toggled()) > 0:
                separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
                box.pack_start(separator, False, False, 0)

                button = get_popover_button("<b>Delete</b> annotations", 'basico-delete')
                button.show_all()
                # ~ button.connect('clicked', self.srvclb.action_annotation_delete)
                box.pack_start(button, False, False, 0)

                button = get_popover_button("<b>Backup</b> annotations", 'basico-backup')
                button.show_all()
                # ~ button.connect('clicked', self.srvclb.action_annotation_backup)
                box.pack_start(button, False, False, 0)

            else:
                separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
                box.pack_start(separator, False, False, 0)

                # Popover button "Jump to SAP Note"
                if sid != '0000000000':
                    # Jump to SAP Note
                    button = get_popover_button("<b>Jump</b> to SAP Note %d" % int(sid), 'basico-jump-sapnote')
                    button.show_all()
                    button.connect('clicked', self.srvclb.gui_jump_to_sapnote, sid)
                    box.pack_start(button, False, False, 0)

                button = get_popover_button("<b>Preview</b> annotation", 'basico-preview')
                button.show_all()
                # ~ button.connect('clicked', self.__clb_preview, aid)
                box.pack_start(button, False, False, 0)

                button = get_popover_button("<b>Edit</b> annotation", 'basico-edit')
                button.show_all()
                # ~ button.connect('clicked', self.__clb_edit, aid)
                box.pack_start(button, False, False, 0)

                button = get_popover_button("<b>Duplicate</b> annotation", 'basico-copy-paste')
                button.show_all()
                # ~ button.connect('clicked', self.srvclb.duplicate_sapnote, aid)
                box.pack_start(button, False, False, 0)

            return box


    def __clb_select_all(self, button, checked):
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        def check_row(model, path, itr):
            if checked is not None:
                model[path][COLUMN.CHECKBOX] = checked
            else:
                state = model[path][COLUMN.CHECKBOX]
                model[path][COLUMN.CHECKBOX] = not state

        model = sorted_model.get_model()
        model.foreach(check_row)
        self.update_total_annotations_count()
        self.srvuif.grab_focus()


    def set_menuview_signals(self):
        # Categories
        button = self.srvgui.get_widget('gtk_togglebutton_categories')
        button.connect('toggled', self.__clb_set_visible_categories)

        for name in ['inbox', 'drafts', 'archived']:
            button = self.srvgui.get_widget('gtk_button_category_%s' % name)
            button.connect('toggled', self.__clb_set_visible_category, name)

        # Types
        button = self.srvgui.get_widget('gtk_togglebutton_types')
        button.connect('toggled', self.__clb_set_visible_types)

        for name in ATYPES:
            button = self.srvgui.get_widget('gtk_button_type_%s' % name.lower())
            button.connect('toggled', self.__clb_set_visible_annotation_type, name)


    def set_active_categories(self):
        category = self.srvgui.get_widget('gtk_togglebutton_inbox')
        category.set_active(True)


    def __update_panel_values(self):
        self.__update_scopes()
        self.__update_products()

    def __update_scopes(self):
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        scopes = set()

        def get_values(model, path, itr):
            scope = sorted_model.get(itr, COLUMN.SCOPE)[0]
            scopes.add(scope)
        sorted_model.foreach(get_values)

        # Update scope combo
        cmb_scope = self.srvgui.get_widget('gtk_combobox_filter_scope')
        signal = self.srvgui.get_signal('gtk_combobox_filter_scope', 'changed')
        GObject.signal_handler_block(cmb_scope, signal)
        model = cmb_scope.get_model()
        model.clear()
        first = model.append(['<big><b>Scope</b></big>'])
        model.append(['All'])
        model.append(['None'])
        cmb_scope.set_active_iter(first)
        lscopes = list(scopes)
        lscopes.sort()
        for item in lscopes:
            if len(item) > 0:
                model.append([item])
        GObject.signal_handler_unblock(cmb_scope, signal)


    def __update_products(self):
        sorted_model = self.srvgui.get_widget('visor_annotation_sorted_model')
        products = set()

        def get_values(model, path, itr):
            product = sorted_model.get(itr, COLUMN.PRODUCT)[0]
            products.add(product)
        sorted_model.foreach(get_values)

        # Update product combo
        cmb_product = self.srvgui.get_widget('gtk_combobox_filter_product')
        signal = self.srvgui.get_signal('gtk_combobox_filter_product', 'changed')
        GObject.signal_handler_block(cmb_product, signal)
        model = cmb_product.get_model()
        model.clear()
        first = model.append(['<big><b>Product</b></big>'])
        model.append(['All'])
        model.append(['None'])
        cmb_product.set_active_iter(first)
        lproducts = list(products)
        lproducts.sort()
        for item in lproducts:
            if len(item) > 0:
                model.append([item])
        GObject.signal_handler_unblock(cmb_product, signal)


    def __clb_scope_changed(self, *args):
        visible_filter = self.srvgui.get_widget('visor_annotation_visible_filter')
        visible_filter.refilter()
        self.update_total_annotations_count()
        self.update_products()


    def __clb_product_changed(self, *args):
        visible_filter = self.srvgui.get_widget('visor_annotation_visible_filter')
        visible_filter.refilter()
        self.update_total_annotations_count()
        self.update_scopes()


    def __clb_switch_selection_atypes(self, switch, state):
        label = self.srvgui.get_widget('gtk_label_switch_select_atypes')
        switched = switch.get_active()
        switch.set_state(switched)
        if switched is True:
            label.set_text ("All selected")

        else:
            label.set_text("None selected")

        for name in ATYPES:
            button = self.srvgui.get_widget('gtk_button_type_%s' % name.lower())
            button.set_state(switched)
            button.set_active(switched)
