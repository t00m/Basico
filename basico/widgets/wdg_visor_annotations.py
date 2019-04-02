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

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango

from basico.core.mod_env import LPATH, ATYPES
from basico.core.mod_wdg import BasicoWidget
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_import import ImportWidget


class AnnotationsVisor(BasicoWidget, Gtk.HBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.HBox.__init__(self, app)
        self.set_homogeneous(False)
        self.bag = []
        self.get_services()
        self.setup_left_panel()
        self.set_initial_panel_button_status()
        self.setup_visor()
        self.icons = {}
        self.icons['type'] = {}
        for atype in ATYPES:
            self.icons['type'][atype.lower()] = self.srvicm.get_pixbuf_icon('basico-annotation-type-%s' % atype.lower())
        self.log.debug("Annotation Visor initialized")


    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvuif = self.get_service("UIF")
        self.srvutl = self.get_service("Utils")
        self.srvant = self.get_service('Annotation')


    def set_initial_panel_button_status(self):
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

    def get_treeview(self):
        return self.treeview


    def sort_by_timestamp(self):
        self.sorted_model.set_sort_column_id(11, Gtk.SortType.DESCENDING)


    def setup_left_panel(self):
        pass


    def set_visible_categories(self, togglebutton):
        types = self.srvgui.get_widget('gtk_togglebutton_types')
        revealer = self.srvgui.get_widget('gtk_revealer_annotations_categories')

        active = togglebutton.get_active()
        if active:
            types.set_active(False)
        revealer.set_reveal_child(active)


    def set_visible_types(self, togglebutton):
        categories = self.srvgui.get_widget('gtk_togglebutton_categories')
        revealer = self.srvgui.get_widget('gtk_revealer_annotations_types')

        active = togglebutton.get_active()
        if active:
            categories.set_active(False)
        revealer.set_reveal_child(active)


    def set_visible_priority(self, togglebutton):
        categories = self.srvgui.get_widget('gtk_togglebutton_categories')
        revealer = self.srvgui.get_widget('gtk_revealer_annotations_priority')

        active = togglebutton.get_active()
        if active:
            priority.set_active(False)
        revealer.set_reveal_child(active)


    def set_visible_category(self, togglebutton, title):
        active = togglebutton.get_active()
        self.srvgui.set_key_value('ANNOTATIONS_CATEGORY_%s_VISIBLE' % title.upper(), active)
        self.populate_annotations()


    def set_visible_annotation_type(self, togglebutton, atype):
        active = togglebutton.get_active()
        self.srvgui.set_key_value('ANNOTATIONS_TYPE_%s_VISIBLE' % atype.upper(), active)
        self.populate_annotations()


    def set_visible_priority(self, togglebutton, title):
        active = togglebutton.get_active()
        self.srvgui.set_key_value('ANNOTATIONS_PRIORITY_%s_VISIBLE' % title.upper(), active)
        self.populate_annotations()


    def setup_visor(self):
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        self.treeview = Gtk.TreeView()
        scr.add(self.treeview)
        scr.set_hexpand(True)
        self.pack_start(scr, True, True, 0)

        # Setup model
        self.model = Gtk.TreeStore(
            int,        # key
            Pixbuf,        # Icon
            int,        # checkbox
            str,        # sid
            str,        # title
            str,        # component
            str,        # category
            str,        # type
            str,        # priority
            str,        # last update
            str,        # Annotation Id (extra key)
            str,        # Timestamp
        )

        # Setup columns
        def get_column_header_widget(title, icon_name=None, width=24, height=24):
            hbox = Gtk.HBox()
            icon = self.srvicm.get_new_image_icon(icon_name, width, height)
            label = Gtk.Label()
            label.set_markup("<b>%s</b>" % title)
            # ~ label.modify_font(Pango.FontDescription('Monospace 10'))
            hbox.pack_start(icon, False, False, 3)
            hbox.pack_start(label, True, True, 3)
            hbox.show_all()
            return hbox

        # SAP Note key
        self.renderer_key = Gtk.CellRendererText()
        self.column_key = Gtk.TreeViewColumn('Key', self.renderer_key, text=0)
        self.column_key.set_visible(False)
        self.column_key.set_expand(False)
        self.column_key.set_clickable(False)
        self.column_key.set_sort_indicator(True)
        self.treeview.append_column(self.column_key)

        # Icon
        self.renderer_icon = Gtk.CellRendererPixbuf()
        self.renderer_icon.set_alignment(0.0, 0.5)
        self.column_icon = Gtk.TreeViewColumn('', self.renderer_icon, pixbuf=1)
        widget = get_column_header_widget('', 'basico-empty')
        self.column_icon.set_widget(widget)
        self.column_icon.set_visible(True)
        self.column_icon.set_expand(False)
        self.column_icon.set_clickable(False)
        self.column_icon.set_sort_indicator(True)
        self.treeview.append_column(self.column_icon)

        # SAP Note Checkbox
        self.renderer_checkbox = Gtk.CellRendererToggle()
        self.renderer_checkbox.connect("toggled", self.toggle_checkbox)
        self.column_checkbox = Gtk.TreeViewColumn('', self.renderer_checkbox, active=2)
        self.column_checkbox.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_checkbox.set_visible(False)
        self.column_checkbox.set_expand(False)
        self.column_checkbox.set_clickable(True)
        self.column_checkbox.set_sort_indicator(True)
        self.column_checkbox.set_property('spacing', 50)
        self.treeview.append_column(self.column_checkbox)

        # SAP Note Id
        self.renderer_sid = Gtk.CellRendererText()
        self.renderer_sid.set_property('xalign', 1.0)
        self.renderer_sid.set_property('height', 36)
        self.renderer_sid.set_property('background', '#F0E3E3')
        self.column_sid = Gtk.TreeViewColumn('SAP Note Id', self.renderer_sid, markup=3)
        widget = get_column_header_widget('SAP Note Id', 'basico-sid')
        self.column_sid.set_widget(widget)
        self.column_sid.set_visible(True)
        self.column_sid.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_sid.set_expand(False)
        self.column_sid.set_clickable(True)
        self.column_sid.set_sort_indicator(True)
        self.column_sid.set_sort_column_id(0)
        self.treeview.append_column(self.column_sid)

        # SAP Note title
        self.renderer_title = Gtk.CellRendererText()
        self.renderer_title.set_property('background', '#FFFEEA')
        self.renderer_title.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_title = Gtk.TreeViewColumn('Title', self.renderer_title, markup=4)
        widget = get_column_header_widget('Title', 'basico-tag')
        self.column_title.set_widget(widget)
        self.column_title.set_visible(True)
        self.column_title.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_title.set_expand(True)
        self.column_title.set_clickable(True)
        self.column_title.set_sort_indicator(True)
        self.column_title.set_sort_column_id(4)
        self.treeview.append_column(self.column_title)

        # SAP Note Component
        self.renderer_component = Gtk.CellRendererText()
        self.renderer_component.set_property('background', '#E3E3F0')
        self.column_component = Gtk.TreeViewColumn('Component', self.renderer_component, markup=5)
        widget = get_column_header_widget('Component', 'basico-component')
        self.column_component.set_widget(widget)
        self.column_component.set_visible(True)
        self.column_component.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_component.set_expand(False)
        self.column_component.set_clickable(True)
        self.column_component.set_sort_indicator(True)
        self.column_component.set_sort_column_id(5)
        self.treeview.append_column(self.column_component)

        # SAP Note Category
        self.renderer_category = Gtk.CellRendererText()
        self.renderer_category.set_property('background', '#E3F1E3')
        self.column_category = Gtk.TreeViewColumn('Category', self.renderer_category, markup=6)
        widget = get_column_header_widget('Category', 'basico-category')
        self.column_category.set_widget(widget)
        self.column_category.set_visible(False)
        self.column_category.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_category.set_expand(False)
        self.column_category.set_clickable(True)
        self.column_category.set_sort_indicator(True)
        self.column_category.set_sort_column_id(6)
        self.treeview.append_column(self.column_category)

        # SAP Note Type
        self.renderer_type = Gtk.CellRendererText()
        self.renderer_type.set_property('background', '#DADAFF')
        self.column_type = Gtk.TreeViewColumn('Type', self.renderer_type, markup=7)
        self.column_type.set_visible(True)
        self.column_type.set_expand(False)
        self.column_type.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_type.set_clickable(True)
        self.column_type.set_sort_indicator(True)
        self.column_type.set_sort_column_id(7)
        self.treeview.append_column(self.column_type)

        # SAP Note Priority
        self.renderer_priority = Gtk.CellRendererText()
        self.renderer_priority.set_property('background', '#e4f1f1')
        self.column_priority = Gtk.TreeViewColumn('Priority', self.renderer_priority, markup=8)
        self.column_priority.set_visible(True)
        self.column_priority.set_expand(False)
        self.column_priority.set_clickable(True)
        self.column_priority.set_sort_indicator(True)
        self.column_priority.set_sort_column_id(8)
        self.treeview.append_column(self.column_priority)

        # SAP Note UpdatedOn
        self.renderer_updated = Gtk.CellRendererText()
        self.renderer_updated.set_property('background', '#FFE6D1')
        self.column_updated = Gtk.TreeViewColumn('Updated On', self.renderer_updated, markup=9)
        self.column_updated.set_visible(True)
        self.column_updated.set_expand(False)
        self.column_updated.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_updated.set_clickable(True)
        self.column_updated.set_sort_indicator(True)
        self.column_updated.set_sort_column_id(11)
        self.column_updated.set_sort_order(Gtk.SortType.DESCENDING)
        self.model.set_sort_column_id(11, Gtk.SortType.DESCENDING)
        self.treeview.append_column(self.column_updated)

        # Annotation Id
        self.renderer_annotation = Gtk.CellRendererText()
        self.column_annotation = Gtk.TreeViewColumn('Annotation Id', self.renderer_annotation, markup=10)
        self.column_annotation.set_visible(False)
        self.column_annotation.set_expand(False)
        self.column_annotation.set_clickable(False)
        self.column_annotation.set_sort_indicator(True)
        self.treeview.append_column(self.column_annotation)

        # Timestamp
        self.renderer_timestamp = Gtk.CellRendererText()
        self.column_timestamp = Gtk.TreeViewColumn('Timestamp', self.renderer_timestamp, text=11)
        self.column_timestamp.set_visible(False)
        self.column_timestamp.set_expand(False)
        self.column_timestamp.set_clickable(False)
        self.column_timestamp.set_sort_indicator(True)
        self.column_timestamp.set_sort_column_id(11)
        self.column_timestamp.set_sort_order(Gtk.SortType.ASCENDING)
        self.treeview.append_column(self.column_timestamp)

        # Treeview properties
        self.treeview.set_can_focus(False)
        self.treeview.set_enable_tree_lines(True)
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_hover_selection(False)
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.NONE)
        self.treeview.set_enable_tree_lines(True)
        self.treeview.set_level_indentation(10)
        self.treeview.connect('button_press_event', self.right_click)

        # DOC: In order to have a Gtk.Widged with sorting and filtering
        # capabilities, you have to filter the model first, and use this
        # new model to create the sorted model. Then, attach the sorted
        # model to the treeview...

        # Treeview filtering:
        self.visible_filter = self.model.filter_new()
        self.visible_filter.set_visible_func(self.visible_function)

        # TreeView sorting
        self.sorted_model = Gtk.TreeModelSort(model=self.visible_filter)
        self.sorted_model.set_sort_func(0, self.sort_function, None)

        # Selection
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect('changed', self.row_changed)

        # Set model (filtered and sorted)
        self.sorted_model.set_sort_column_id(9, Gtk.SortType.ASCENDING)
        self.treeview.set_model(self.sorted_model)

        self.show_all()


    def sort_function(self, model, row1, row2, user_data):
        sort_column = 0

        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)

        if value1 < value2:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1


    def always_visible(self, model, itr, data):
        return False


    def visible_function(self, model, itr, data):
        entry = self.srvgui.get_widget('gtk_entry_filter_visor')
        text = self.srvutl.clean_html(entry.get_text())
        title = model.get(itr, 4)[0]
        match = text.upper() in title.upper()

        return match


    def update_total_annotations_count(self):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        lblnotescount = self.srvgui.get_widget('gtk_label_total_notes')
        total = self.srvant.get_total()
        count = len(self.visible_filter)
        lblnotescount.set_markup("<b>%d/<big>%d annotations</big></b>" % (count, total))
        msg = 'View populated with %d annotations' % count
        self.srvuif.statusbar_msg(msg)


    def get_visible_filter(self):
        return self.visible_filter


    def row_changed(self, selection):
        try:
            model, treeiter = selection.get_selected()
            if treeiter is not None:
                component = model[treeiter][5]
                if component == 'Annotation':
                    aid = model[treeiter][10]
                    is_valid = self.srvant.is_valid(aid)
                    if is_valid:
                        self.srvclb.action_annotation_edit(aid)
                else:
                    aid = None
                    self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
        except Exception as error:
            head = "Error reading annotation's contents"
            body = "<i>%s</i>\n\n" % error
            body += "As a workaround, a new file will be created"
            dialog = self.srvuif.message_dialog_error(head, body)
            self.log.debug(error)
            self.log.debug(self.get_traceback())
            dialog.run()
            dialog.destroy()
            #FIXME: create an empty file for contents


    def toggle_checkbox(self, cell, path):
        path = self.sorted_model.convert_path_to_child_path(Gtk.TreePath(path))
        self.model[path][2] = not self.model[path][2]


    def get_node(self, key, icon, checkbox, sid, title, component, category='', sntype='', priority='', updated='', aid='', timestamp=''):
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
        node.append(category)
        node.append(sntype)
        node.append(priority)
        node.append(updated)
        node.append(aid) # Extra key for annotations id (aid)
        node.append(timestamp)
        return node


    def set_bag(self, annotations):
        self.bag = annotations


    def get_bag(self):
        return self.bag


    def reload(self):
        bag = self.get_bag()
        self.populate_annotations(bag)


    def populate_annotations(self, annotations=None):
        self.column_sid.set_visible(False)
        self.column_checkbox.set_visible(False)
        self.column_category.set_visible(True)
        self.column_component.set_visible(False)
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        completion_model.clear()

        self.treeview.set_model(None)
        self.model.clear()

        if annotations is None:
            annotations = self.srvant.get_all()
        else:
            self.set_bag(annotations)

        dcats = {}
        snpids = {}
        nodes = []
        for fname in annotations:
            try:
                with open(fname, 'r') as fa:
                    try:
                        annotation = json.load(fa)
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

                                node = self.get_node(   0,
                                                        icon,
                                                        False,
                                                        str(int(sid)),
                                                        title,
                                                        annotation['Component'],
                                                        annotation['Category'],
                                                        annotation['Type'],
                                                        annotation['Priority'],
                                                        self.srvutl.fuzzy_date_from_timestamp(annotation['Timestamp']),
                                                        annotation['AID'],
                                                        annotation['Timestamp']
                                                    )
                                nodes.append(node)
                    except Exception as error:
                        self.log.error(error)
            except Exception as error:
                # Whenever an annotation is deleted, after reloading
                # the view, it fails. Then, skip it
                self.log.error("Annotation: %s", fname)
                self.log.error(error)

        for node in nodes:
            self.model.append(ppid, node)

        self.treeview.set_model(self.sorted_model)
        self.sort_by_timestamp()
        self.update_total_annotations_count()


    def show_widgets(self):
        self.srvuif.set_widget_visibility('gtk_label_total_notes', True)


    def right_click(self, treeview, event, data=None):
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.x = x = int(event.x)
            rect.y = y = int(event.y)
            pthinfo = self.treeview.get_path_at_pos(x,y)
            if pthinfo is not None:
                path,col,cellx,celly = pthinfo
                model = treeview.get_model()
                treeiter = model.get_iter(path)
                component = model[treeiter][5]
                aid = model[treeiter][10]
                toolbar = self.srvgui.get_widget('visortoolbar')
                popover = self.srvgui.add_widget('gtk_popover_visor_row', Gtk.Popover.new(treeview))
                popover.set_position(Gtk.PositionType.TOP)
                popover.set_pointing_to(rect)
                box = self.build_popover(aid, popover, component)
                if box is not None:
                    popover.add(box)
                    self.srvclb.gui_show_popover(None, popover)


    def build_popover(self, aid, popover, component):
        sid = self.srvant.get_sid(aid)

        def get_popover_button(text, icon_name):
            button = Gtk.Button()
            button.set_relief(Gtk.ReliefStyle.NONE)
            hbox = Gtk.HBox()
            icon = self.srvicm.get_new_image_icon(icon_name, 24, 24)
            lbltext = Gtk.Label()
            lbltext.set_xalign(0.0)
            lbltext.set_markup('%s' % text)
            hbox.pack_start(icon, False, False, 3)
            hbox.pack_start(lbltext, True, True, 3)
            button.add(hbox)
            return button

        if component == 'Annotation':
            box = Gtk.Box(spacing = 3, orientation="vertical")

            # Popover button "Delete annotation"
            button = get_popover_button("<b>Delete</b> annotation", 'basico-delete')
            button.show_all()
            button.connect('clicked', self.srvclb.action_annotation_delete)
            box.pack_start(button, False, False, 0)

            # Popover button "Duplicate annotation"
            if sid != '0000000000':
                # Jump to SAP Note
                button = get_popover_button("Jump to SAP Note %d" % int(sid), 'basico-jump-sapnote')
                button.show_all()
                button.connect('clicked', self.srvclb.gui_jump_to_sapnote, sid)
                box.pack_start(button, False, False, 0)
            else:
                pass
            return box


    def connect_menuview_signals(self):
        # Categories
        button = self.srvgui.get_widget('gtk_togglebutton_categories')
        button.connect('toggled', self.set_visible_categories)

        for name in ['inbox', 'drafts', 'archived']:
            button = self.srvgui.get_widget('gtk_button_category_%s' % name)
            button.connect('toggled', self.set_visible_category, name)

        # Types
        button = self.srvgui.get_widget('gtk_togglebutton_types')
        button.connect('toggled', self.set_visible_types)

        for name in ATYPES:
            button = self.srvgui.get_widget('gtk_button_type_%s' % name.lower())
            button.connect('toggled', self.set_visible_annotation_type, name)


    def set_active_categories(self):
        category = self.srvgui.get_widget('gtk_togglebutton_inbox')
        category.set_active(True)

