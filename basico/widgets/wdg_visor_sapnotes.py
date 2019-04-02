#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_visor.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAPNoteViewVisor widgets
"""

import os
from os.path import sep as SEP
from cgi import escape
import glob
import json

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango

from basico.core.mod_wdg import BasicoWidget
from basico.core.mod_env import LPATH, ATYPES
from basico.services.srv_cols import COL_DOWNLOADED
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_import import ImportWidget
from basico.core.mod_log import get_logger


class SAPNotesVisor(BasicoWidget, Gtk.Box):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.Box.__init__(self, app)        
        self.get_services()
        self.bag = []
        self.icons = {}
        self.icons['type'] = {}
        self.setup()
        self.log.debug("SAP Notes Visor initialized")


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


    def get_treeview(self):
        return self.treeview


    def sort_by_timestamp(self):
        self.sorted_model.set_sort_column_id(11, Gtk.SortType.DESCENDING)


    def setup(self):
        scr = Gtk.ScrolledWindow()
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        self.treeview = Gtk.TreeView()
        scr.add(self.treeview)
        self.pack_start(scr, True, True, 0)

        # Setup model
        self.model = Gtk.TreeStore(
            int,        # key
            Pixbuf,     # Icon
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
        self.renderer_key.set_property('height', 32)
        self.column_key = Gtk.TreeViewColumn('Key', self.renderer_key, text=0)
        self.column_key.set_visible(False)
        self.column_key.set_expand(False)
        self.column_key.set_clickable(False)
        self.column_key.set_sort_indicator(False)
        self.treeview.append_column(self.column_key)

        # Icon
        self.renderer_icon = Gtk.CellRendererPixbuf()
        self.renderer_icon.set_alignment(0.0, 0.5)
        self.column_icon = Gtk.TreeViewColumn('Bookmark', self.renderer_icon, pixbuf=1)
        widget = get_column_header_widget('', 'basico-bookmarks')
        self.column_icon.set_widget(widget)
        self.column_icon.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_icon.set_visible(True)
        self.column_icon.set_expand(False)
        self.column_icon.set_clickable(False)
        self.column_icon.set_sort_indicator(False)
        self.treeview.append_column(self.column_icon)

        # SAP Note Checkbox
        self.renderer_checkbox = Gtk.CellRendererToggle()
        self.renderer_checkbox.connect("toggled", self.toggle_checkbox)
        self.column_checkbox = Gtk.TreeViewColumn('', self.renderer_checkbox, active=2)
        self.column_checkbox.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_checkbox.set_visible(True)
        self.column_checkbox.set_expand(False)
        self.column_checkbox.set_clickable(True)
        self.column_checkbox.set_sort_indicator(False)
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
        self.column_sid.set_sort_order(Gtk.SortType.ASCENDING)
        self.model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.treeview.append_column(self.column_sid)

        # SAP Note title
        self.renderer_title = Gtk.CellRendererText()
        self.renderer_title.set_property('background', '#FFFEEA')
        self.renderer_title.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_title = Gtk.TreeViewColumn('Title', self.renderer_title, markup=4)
        widget = get_column_header_widget('Title', 'basico-tag')
        self.column_title.set_widget(widget)
        self.column_title.set_visible(True)
        self.column_title.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
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
        self.column_component.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
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
        self.renderer_type.set_property('background', '#e4f1f1')
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
        self.column_priority = Gtk.TreeViewColumn('Priority', self.renderer_priority, markup=8)
        self.column_priority.set_visible(False)
        self.column_priority.set_expand(True)
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
        self.treeview.append_column(self.column_updated)

        # Annotation Id
        self.renderer_annotation = Gtk.CellRendererText()
        self.column_annotation = Gtk.TreeViewColumn('Annotation Id', self.renderer_annotation, markup=10)
        self.column_annotation.set_visible(False)
        self.column_annotation.set_expand(False)
        self.column_annotation.set_clickable(False)
        self.column_annotation.set_sort_indicator(False)
        self.treeview.append_column(self.column_annotation)

        # Timestamp
        self.renderer_timestamp = Gtk.CellRendererText()
        self.column_timestamp = Gtk.TreeViewColumn('Annotation Id', self.renderer_timestamp, text=11)
        self.column_timestamp.set_visible(False)
        self.column_timestamp.set_expand(False)
        self.column_timestamp.set_clickable(False)
        self.column_timestamp.set_sort_indicator(False)
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
        # ~ self.treeview.modify_font(Pango.FontDescription('Monospace 10'))
        self.treeview.connect('button_press_event', self.right_click)

        # DOC: In order to have a Gtk.Widged with sorting and filtering
        # capabilities, you have to filter the model first, and use this
        # new model to create the sorted model. Then, attach the sorted
        # model to the treeview...

        # Treeview filtering:
        self.visible_filter = self.model.filter_new()
        self.visible_filter.set_visible_func(self.visible_function)
        # https://stackoverflow.com/questions/23355866/user-search-collapsed-rows-in-a-gtk-treeview

        # TreeView sorting
        self.sorted_model = Gtk.TreeModelSort(model=self.visible_filter)
        self.sorted_model.set_sort_func(0, self.sort_function, None)

        # Selection
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect('changed', self.row_changed)

        # Set model (filtered and sorted)
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


    def update_total_sapnotes_count(self):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        lblnotescount = self.srvgui.get_widget('gtk_label_total_notes')
        total = self.srvdtb.get_total()
        count = len(self.visible_filter)
        lblnotescount.set_markup("<b>%d/<big>%d SAP Notes</big></b>" % (count, total))
        msg = 'View populated with %d SAP Notes' % count
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
            self.log.debug(error)


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


    def get_model(self):
        return self.model


    def get_sorted_model(self):
        return self.sorted_model


    def get_bag(self):
        return self.bag


    def reload(self):
        self.populate_sapnotes(self.bag)


    def populate_sapnotes(self, bag=None, cid=None):
        icon_sapnote = self.srvicm.get_pixbuf_icon('basico-sapnote', 32, 32)
        icon_bookmark = self.srvicm.get_pixbuf_icon('basico-bookmarks', 32, 32)
        for atype in ATYPES:
            self.icons['type'][atype.lower()] = self.srvicm.get_pixbuf_icon('basico-annotation-type-%s' % atype.lower())
        self.column_sid.set_visible(True)
        self.column_checkbox.set_visible(False)
        self.column_category.set_visible(False)
        self.column_component.set_visible(True)
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        completion_model.clear()
        self.model.clear()

        if bag is None:
            bag = self.bag
        else:
            self.bag = bag


        for sid in self.bag:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            if metadata is not None:
                bookmark = metadata['bookmark']
                title = escape(metadata['title'])
                sid = str(int(metadata['id']))
                if bookmark:
                    icon = icon_bookmark
                    title = "<b>%s</b>" % title
                    sid = "<b>%s</b>" % sid
                else:
                    icon = icon_sapnote

                timestamp = metadata['releasedon']
                timestamp = timestamp.replace('-', '')
                timestamp = timestamp.replace(':', '')
                timestamp = timestamp.replace('T', '_')

                node = self.get_node(   int(metadata['id']),
                                        icon,
                                        False,
                                        '<b>%s</b>' % sid,
                                        title,
                                        escape(metadata['componentkey']),
                                        escape(metadata['category']),
                                        escape(metadata['type']),
                                        escape(metadata['priority']),
                                        self.srvutl.fuzzy_date_from_timestamp(timestamp),
                                        '',
                                        timestamp
                                    )
                pid = self.model.append(None, node)

                # Load annotations
                files = self.srvant.get_by_sid(metadata['id'])
                for fname in files:
                    with open(fname, 'r') as fa:
                        annotation = json.load(fa)
                        atype = annotation['Type']
                        try:
                            icon = self.icons['type']['%s' % atype.lower()]
                        except:
                            icon = None
                        node = self.get_node(   0,
                                                icon,
                                                False,
                                                '',
                                                annotation['Title'],
                                                annotation['Component'],
                                                '',
                                                annotation['Type'],
                                                '',
                                                self.srvutl.fuzzy_date_from_timestamp(annotation['Timestamp']),
                                                annotation['AID'],
                                                annotation['Timestamp']
                                            )
                        self.model.append(pid, node)
        self.treeview.set_model(self.sorted_model)
        self.update_total_sapnotes_count()
        self.show_widgets()
        stack = self.srvgui.get_widget('gtk_stack_main')
        stack.set_visible_child_name('visor')


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
                sid = model[treeiter][0]
                sid = "0"*(10 - len(str(sid))) + str(sid)
                toolbar = self.srvgui.get_widget('visortoolbar')
                popover = self.srvgui.add_widget('gtk_popover_visor_row', Gtk.Popover.new(treeview))
                popover.set_position(Gtk.PositionType.TOP)
                popover.set_pointing_to(rect)
                box = self.build_popover(sid, popover, component)
                popover.add(box)
                self.srvclb.gui_show_popover(None, popover)


    def build_popover(self, sid, popover, component):
        box = Gtk.Box(spacing = 3, orientation="vertical")
        isid = int(sid)

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
            # Popover button "Delete annotation"
            button = get_popover_button("<b>Delete annotation</b>", 'basico-delete')
            button.show_all()
            button.connect('clicked', self.srvclb.action_annotation_delete)
            box.pack_start(button, False, False, 0)

            # Popover button "Duplicate annotation"
            button = get_popover_button("<b>Duplicate annotation</b>", 'basico-duplicate')
            button.show_all()
            button.connect('clicked', self.srvclb.action_annotation_duplicate)
            box.pack_start(button, False, False, 0)

        else:
            # Popover button "Add an annotation"
            button = get_popover_button("<b>Add an annotation</b> to SAP Note %d" % isid, 'basico-annotation')
            button.show_all()
            button.connect('clicked', self.srvclb.gui_annotation_widget_show, sid, 'create')
            box.pack_start(button, False, False, 0)

            # Popover button "Open SAP Note"
            button = get_popover_button("<b>Browse</b> SAP Note %d" % isid, 'basico-browse')
            button.connect('clicked', self.srvclb.sapnote_browse, sid)
            box.pack_start(button, False, False, 0)

            # Popover button "Download SAP Note in PDF"
            button = get_popover_button("See SAP Note %d in <b>PDF</b>" % isid, 'basico-browse')
            button.connect('clicked', self.srvclb.sapnote_download_pdf, sid)
            box.pack_start(button, False, False, 0)

            # Popover button "Bookmark"
            button = get_popover_button("<b>(Un)bookmark</b> SAP Note %d" % isid, 'basico-bookmarks')
            button.connect('clicked', self.srvclb.switch_bookmark, [sid], popover)
            box.pack_start(button, False, False, 0)

            # Popover button "Copy to clipboard"
            button = get_popover_button("<b>Copy</b> SAP Note %d details <b>to clipboard</b>" % isid, 'basico-clipboard')
            button.connect('clicked', self.srvclb.gui_copy_to_clipboard_sapnote, [sid], popover)
            box.pack_start(button, False, False, 0)

            # Separator
            separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
            box.pack_start(separator, True, True, 0)

            # Assing SAP Notes in current view to a category
            # Only available in Donwloaded category
            viewmenu = self.srvgui.get_widget('viewmenu')
            current_viewmenu = viewmenu.get_view()
            current_collection = viewmenu.get_current_collection()
            view_is_collection = current_viewmenu == 'collection'
            collection_is_downloaded = current_collection == COL_DOWNLOADED

            # Popover button Collection Management
            button = get_popover_button("<b>Manage collections</b> for SAP Note %d" % isid, 'basico-collection')
            box.pack_start(button, False, False, 0)
            self.popcollections = self.srvgui.add_widget('gtk_popover_button_manage_collections_single_note', Gtk.Popover.new(button))
            self.popcollections.set_position(Gtk.PositionType.RIGHT)
            button.connect('clicked', self.srvclb.gui_show_popover, self.popcollections)
            colmgt = CollectionsMgtView(self.app, sid, overwrite=True)
            self.popcollections.add(colmgt)

            # Separator
            separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
            box.pack_start(separator, True, True, 0)


            # Popover button "Delete SAP Note"
            button = get_popover_button("<b>Delete</b> SAP Note %d" % isid, 'basico-delete')
            button.connect('clicked', self.srvclb.sapnote_delete, sid)
            button.set_tooltip_text("Checkbox must be activated in order to trigger the deletion")
            box.pack_start(button, False, False, 0)

        return box


    def get_filtered_bag(self):
        visor = self.srvgui.get_widget('visor_sapnotes')
        model = visor.get_sorted_model()
        selected = []

        def get_selected_sapnotes(model, path, itr):
            sid = model.get(itr, 0)[0]
            aid = model.get(itr, 10)[0]
            if len(aid) == 0:
                selected.append(str(sid))

        model.foreach(get_selected_sapnotes)
        return selected
