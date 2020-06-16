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
from html import escape
import glob
import json
from enum import IntEnum

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import Pango

from basico.core.wdg import BasicoWidget
from basico.core.env import LPATH, ATYPES
from basico.services.collections import COL_DOWNLOADED
from basico.widgets.cols import CollectionsMgtView
from basico.widgets.sapimport import ImportWidget
from basico.widgets.menuview import MenuView
from basico.widgets.visor_toolbar import VisorToolbar


class COLUMN(IntEnum):
    KEY = 0
    ICON = 1
    CHECKBOX = 2
    SID = 3
    TITLE = 4
    COMPONENT = 5
    CATEGORY = 6
    TYPE = 7
    PRIORITY = 8
    UPDATED = 9
    UPDATED_TIMESTAMP = 10


class SAPNotesVisor(BasicoWidget, Gtk.VBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.VBox.__init__(self, app)
        self.set_property('margin-left', 6)
        self.set_homogeneous(False)
        self.get_services()
        self.bag = []
        self.icons = {}
        self.icons['type'] = {}
        toolbar = self.setup_toolbar()
        panel = self.setup_panel()
        visor = self.setup_visor()
        paned = Gtk.HPaned()
        paned.add1(panel)
        paned.add2(visor)
        paned.set_position(400)
        paned.show_all()
        self.pack_start(toolbar, False, False, 0)
        self.pack_start(paned, True, True, 0)
        self.connect_signals()
        self.log.debug("SAP Notes Visor initialized")

    def connect_signals(self, *args):
        self.srvdtb.connect('database-loaded', self.update)
        self.srvdtb.connect('database-updated', self.update)

    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvuif = self.get_service("UIF")
        self.srvutl = self.get_service("Utils")
        self.srvweb = self.get_service("Driver")
        # ~ self.srvant = self.get_service('Annotation')
        # ~ self.srvatc = self.get_service('Attachment')


    def sort_by_timestamp(self):
        sorted_model = self.srvgui.get_widget('visor_sapnotes_sorted_model')
        sorted_model.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP, Gtk.SortType.ASCENDING)

    def setup_toolbar(self):
        return self.srvgui.add_widget('visor_sapnotes_toolbar', VisorToolbar(self.app))

    def setup_panel(self):
        ## Left view - SAP Notes Menu view
        box = self.srvgui.add_widget('gtk_vbox_container_menu_view', Gtk.VBox())
        box.set_property('margin-left', 6)
        box.set_property('margin-right', 3)
        box.set_property('margin-bottom', 0)
        box.set_no_show_all(True)
        box.hide()

        # View combobox button/popover
        lhbox = Gtk.HBox()
        menuviews = self.srvgui.add_widget('gtk_button_menu_views', Gtk.Button())
        menuviews.set_relief(Gtk.ReliefStyle.NONE)
        hbox = Gtk.HBox()
        label = self.srvgui.add_widget('gtk_label_current_view', Gtk.Label())
        label.set_xalign(0.0)
        image = self.srvgui.add_widget('gtk_image_current_view', Gtk.Image())
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, True, True, 3)
        menuviews.add(hbox)
        lhbox.pack_start(menuviews, True, True, 3)
        lhbox.show_all()
        box.pack_start(lhbox, False, False, 3)

        ### Popover menuviews
        popover = self.srvgui.add_widget('gtk_popover_button_menu_views', Gtk.Popover.new(menuviews))
        menuviews.connect('clicked', self.srvuif.popover_show, popover)
        box_views = Gtk.Box(spacing = 0, orientation="vertical")
        popover.add(box_views)

        box_views.pack_start(self.srvuif.create_menuview_button('collection'), False, False, 0)
        separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
        box_views.pack_start(separator, False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('component'), False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('description'), False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('bookmarks'), False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('category'), False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('chronologic'), False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('priority'), False, False, 0)
        box_views.pack_start(self.srvuif.create_menuview_button('type'), False, False, 0)

        ### Toolbar
        toolbar = Gtk.Toolbar()
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        #### Filter entry tool
        tool = Gtk.ToolItem.new()

        hbox = Gtk.HBox()
        viewfilter = self.srvgui.add_widget('gtk_entry_filter_view', Gtk.Entry())
        menuview = self.srvgui.add_widget('menuview', MenuView(self.app))
        menuview.set_vexpand(True)
        completion = self.srvgui.get_widget('gtk_entrycompletion_menuview')
        viewfilter.set_completion(completion)
        viewfilter.connect('activate', menuview.filter)

        icon = self.srvicm.get_pixbuf_icon('basico-refresh')
        viewfilter.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, icon)
        viewfilter.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, True)
        viewfilter.set_icon_tooltip_markup (Gtk.EntryIconPosition.PRIMARY, "Refresh and collapse")

        icon = self.srvicm.get_pixbuf_icon('basico-filter')
        viewfilter.set_icon_from_pixbuf(Gtk.EntryIconPosition.SECONDARY, icon)
        viewfilter.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, True)
        viewfilter.set_icon_tooltip_markup (Gtk.EntryIconPosition.SECONDARY, "Click here to expand the tree")
        viewfilter.set_placeholder_text("Filter this view...")

        def on_icon_pressed(entry, icon_pos, event):
            menuview = self.srvgui.get_widget('menuview')
            if icon_pos == Gtk.EntryIconPosition.PRIMARY:
                menuview.refresh()
            elif icon_pos == Gtk.EntryIconPosition.SECONDARY:
                menuview.menu_expand()

        viewfilter.connect("icon-press", on_icon_pressed)

        hbox.pack_start(viewfilter, True, True, 0)
        tool.add(hbox)
        tool.set_expand(True)
        toolbar.insert(tool, -1)

        box.pack_start(toolbar, False, False, 0)

        ### View treeview
        box_trv = Gtk.VBox()
        box_trv.set_property('margin-left', 6)
        box_trv.set_property('margin-right', 3)
        box_trv.set_property('margin-bottom', 0)
        scr = Gtk.ScrolledWindow()
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        viewsbox = self.srvgui.add_widget('gtk_box_container_views', Gtk.Box())
        viewsbox.pack_start(menuview, True, True, 0)
        vwp.add(viewsbox)
        scr.add(vwp)
        box_trv.pack_start(scr, True, True, 0)
        box.pack_start(box_trv, True, True, 0)
        return box

    def setup_visor(self):
        visor = Gtk.VBox()
        # ~ visor.set_property('margin-left', 3)
        visor.set_property('margin-right', 6)
        scr = Gtk.ScrolledWindow()
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        treeview = self.srvgui.add_widget('visor_sapnotes_treeview', Gtk.TreeView())
        scr.add(treeview)
        visor.pack_start(scr, True, True, 0)
        visor.show_all()

        # Setup model
        model = Gtk.TreeStore(
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
            str,        # Timestamp
        )
        self.srvgui.add_widget('gtk_model_sapnotes', model)

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

        # SAP Note key
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_key', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_key', Gtk.TreeViewColumn('Key', renderer, text=COLUMN.KEY))
        renderer.set_property('height', 32)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(False)
        treeview.append_column(column)

        # Icon
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_icon', Gtk.CellRendererPixbuf())
        column = self.srvgui.add_widget('visor_sapnotes_column_icon', Gtk.TreeViewColumn('', renderer, pixbuf=COLUMN.ICON))
        renderer.set_alignment(0.0, 0.5)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.TYPE)
        column.set_sort_order(Gtk.SortType.ASCENDING)
        treeview.append_column(column)

        # SAP Note Checkbox
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_checkbox', Gtk.CellRendererToggle())
        column = self.srvgui.add_widget('visor_sapnotes_column_checkbox', Gtk.TreeViewColumn('', renderer, active=COLUMN.CHECKBOX))
        renderer.connect("toggled", self.__clb_row_toggled)
        column = Gtk.TreeViewColumn('', renderer, active=COLUMN.CHECKBOX)
        widget = get_column_header_widget('', 'basico-check-accept')
        column.set_widget(widget)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_visible(True)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(False)
        column.set_property('spacing', 50)
        treeview.append_column(column)

        # SAP Note Id
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_sid', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_sid', Gtk.TreeViewColumn('SAP Note', renderer, markup=COLUMN.SID))
        renderer.set_property('xalign', 1.0)
        renderer.set_property('height', 36)
        renderer.set_property('background', '#F0E3E3')
        column.set_visible(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.KEY)
        column.set_sort_order(Gtk.SortType.ASCENDING)
        treeview.append_column(column)

        # SAP Note title
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_title', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_title', Gtk.TreeViewColumn('Title', renderer, markup=COLUMN.TITLE))
        renderer.set_property('background', '#FFFEEA')
        renderer.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        column = Gtk.TreeViewColumn('Title', renderer, markup=COLUMN.TITLE)
        widget = get_column_header_widget('Title', 'basico-tag')
        column.set_widget(widget)
        column.set_visible(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_expand(True)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.TITLE)
        treeview.append_column(column)

        # SAP Note Component
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_component', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_component', Gtk.TreeViewColumn('Component', renderer, markup=COLUMN.COMPONENT))
        renderer.set_property('background', '#E3E3F0')
        widget = get_column_header_widget('Component', 'basico-component')
        column.set_widget(widget)
        column.set_visible(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.COMPONENT)
        treeview.append_column(column)

        # SAP Note Category
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_category', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_category', Gtk.TreeViewColumn('Category', renderer, markup=COLUMN.CATEGORY))
        renderer.set_property('background', '#E3F1E3')
        widget = get_column_header_widget('Category', 'basico-category')
        column.set_widget(widget)
        column.set_visible(False)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.CATEGORY)
        treeview.append_column(column)

        # SAP Note Type
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_type', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_type', Gtk.TreeViewColumn('Type', renderer, markup=COLUMN.TYPE))
        renderer.set_property('background', '#e4f1f1')
        widget = get_column_header_widget('Type', 'basico-type')
        column.set_widget(widget)
        column.set_visible(False)
        column.set_expand(False)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.TYPE)
        treeview.append_column(column)

        # SAP Note Priority
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_priority', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_priority', Gtk.TreeViewColumn('Priority', renderer, markup=COLUMN.PRIORITY))
        renderer.set_property('background', '#f1e4f1')
        widget = get_column_header_widget('Priority', 'basico-priority')
        column.set_widget(widget)
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.PRIORITY)
        treeview.append_column(column)

        # SAP Note Updated
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_updated', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_updated', Gtk.TreeViewColumn('Updated', renderer, markup=COLUMN.UPDATED))
        renderer.set_property('background', '#FFE6D1')
        widget = get_column_header_widget('Updated', 'basico-chronologic')
        column.set_widget(widget)
        column.set_visible(True)
        column.set_expand(False)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_clickable(True)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP)
        column.set_sort_order(Gtk.SortType.DESCENDING)
        model.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP, Gtk.SortType.DESCENDING)
        treeview.append_column(column)

        # Timestamp updated
        renderer = self.srvgui.add_widget('visor_sapnotes_renderer_updated_timestamp', Gtk.CellRendererText())
        column = self.srvgui.add_widget('visor_sapnotes_column_updated_timestamp', Gtk.TreeViewColumn('Updated', renderer, markup=COLUMN.UPDATED_TIMESTAMP))
        column.set_visible(False)
        column.set_expand(False)
        column.set_clickable(False)
        column.set_sort_indicator(True)
        column.set_sort_column_id(COLUMN.UPDATED_TIMESTAMP)
        column.set_sort_order(Gtk.SortType.ASCENDING)
        treeview.append_column(column)

        # Treeview properties
        treeview.set_can_focus(False)
        treeview.set_enable_tree_lines(True)
        treeview.set_headers_visible(True)
        treeview.set_enable_search(True)
        treeview.set_hover_selection(False)
        treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        treeview.set_enable_tree_lines(True)
        treeview.set_level_indentation(10)
        # ~ treeview.modify_font(Pango.FontDescription('Monospace 10'))
        treeview.connect('button_press_event', self.right_click)

        # DOC: In order to have a Gtk.Widged with sorting and filtering
        # capabilities, you have to filter the model first, and use this
        # new model to create the sorted model. Then, attach the sorted
        # model to the treeview...

        # Treeview filtering
        visible_filter = self.srvgui.add_widget('visor_sapnotes_visible_filter', model.filter_new())
        visible_filter.set_visible_func(self.__clb_visible_function)
        # https://stackoverflow.com/questions/23355866/user-search-collapsed-rows-in-a-gtk-treeview

        # TreeView sorting
        sorted_model = Gtk.TreeModelSort(model=visible_filter)
        self.srvgui.add_widget('visor_sapnotes_sorted_model', sorted_model)
        sorted_model.set_sort_func(0, self.sort_function, None)

        # Selection
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        selection.connect('changed', self.row_changed)

        # Set model (filtered and sorted)
        treeview.set_model(sorted_model)

        self.show_all()
        return visor


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


    def __clb_visible_function(self, model, itr, data):
        entry = self.srvgui.get_widget('gtk_entry_filter_visor')
        text = self.srvutl.clean_html(entry.get_text())
        title = model.get(itr, COLUMN.TITLE)[0]
        component = model.get(itr, COLUMN.COMPONENT)[0]
        fields = title + ' ' + component
        match = text.upper() in fields.upper()

        return match

    def update(self, *args):
        def reload():
            self.populate()
        GLib.idle_add(reload)
        self.log.debug("SAP Notes Visor updated")

    def update_total_sapnotes_count(self):
        entry = self.srvgui.get_widget('gtk_entry_filter_visor')
        term = entry.get_text()
        menuview = self.srvgui.get_widget('menuview')
        view = menuview.get_view()
        visible_filter = self.srvgui.get_widget('visor_sapnotes_visible_filter')
        statusbar = self.srvgui.get_widget('widget_statusbar')
        lblnotescount = self.srvgui.get_widget('gtk_label_total_notes')
        total = self.srvdtb.get_total()
        count = len(visible_filter)
        lblnotescount.set_markup("<b>%d/<big>%d</big></b>" % (count, total))
        msg = "View <b>%s</b> populated with <b>%d notes</b>" % (view, count)
        if len(term) > 0:
            msg += " for term <b>%s</b>" % term
        self.log.info(msg)
        # ~ self.srvuif.statusbar_msg(msg)


    def row_changed(self, selection):
        pass
        # ~ try:
            # ~ model, treeiter = selection.get_selected()
            # ~ if treeiter is not None:
                # ~ component = model[treeiter][5]
                # ~ if component == 'Annotation':
                    # ~ aid = model[treeiter][10]
                    # ~ is_valid = self.srvant.is_valid(aid)
                    # ~ if is_valid:
                        # ~ self.srvclb.action_annotation_edit(aid)
                # ~ else:
                    # ~ aid = None
        # ~ except Exception as error:
            # ~ self.log.debug(error)


    def __clb_row_toggled(self, cell, path):
        sorted_model = self.srvgui.get_widget('visor_sapnotes_sorted_model')
        model = sorted_model.get_model()
        rpath = sorted_model.convert_path_to_child_path(Gtk.TreePath(path))
        model[rpath][COLUMN.CHECKBOX] = not model[rpath][COLUMN.CHECKBOX]


    def get_node(self, key, icon, checkbox, sid, title, component, category='', sntype='', priority='', updated='', timestamp=''):
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
        node.append(timestamp)
        return node


    def get_bag(self):
        return self.bag


    def reload(self):
        self.populate(self.bag)


    def populate(self, bag=None, cid=None):
        model = self.srvgui.get_widget('gtk_model_sapnotes')
        sorted_model = self.srvgui.get_widget('visor_sapnotes_sorted_model')
        icon_sapnote = self.srvicm.get_pixbuf_icon('basico-sapnote', 32, 32)
        icon_bookmark = self.srvicm.get_pixbuf_icon('basico-bookmarks', 32, 32)
        for atype in ATYPES:
            self.icons['type'][atype.lower()] = self.srvicm.get_pixbuf_icon('basico-annotation-type-%s' % atype.lower())
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        completion_model.clear()
        model.clear()
        if bag is None:
            # ~ self.log.debug("Bag empty. Get all SAP Notes from database")
            self.bag = self.srvdtb.get_notes()
        else:
            self.bag = bag
            # ~ self.log.debug("Displaying %d notes" % len(bag))

        for sid in self.bag:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            if metadata is not None:
                bookmark = metadata['bookmark']
                title = escape(metadata['title'])
                sid = str(int(metadata['id']))

                has_annotations = [] #self.srvant.get_by_sid(sid)
                has_attachments = [] #self.srvatc.get_by_sid(sid)
                if bookmark:
                    icon = icon_bookmark
                    title = "<b>%s</b>" % title
                    sid = "<b>%s</b>" % sid
                else:
                    if len(has_annotations) > 0 and len(has_attachments) > 0:
                        icon = self.srvicm.get_pixbuf_icon('basico-annotation-attachment', 32, 32)
                    elif len(has_annotations) > 0 and len(has_attachments) == 0:
                        icon = self.srvicm.get_pixbuf_icon('basico-annotation', 32, 32)
                    elif len(has_annotations) == 0 and len(has_attachments) > 0:
                        icon = self.srvicm.get_pixbuf_icon('basico-attachment', 32, 32)
                    else:
                        icon = icon_sapnote

                timestamp = metadata['releasedon']
                timestamp = timestamp.replace('-', '')
                timestamp = timestamp.replace(':', '')
                timestamp = timestamp.replace('T', '_')
                stype = escape(metadata['type'].lower())
                icon_name = 'basico-%s' % stype.replace(' ', '-')
                icon = self.srvicm.get_pixbuf_icon(icon_name, 36, 36)
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
                                        timestamp
                                    )
                pid = model.append(None, node)

                # Load annotations
                files = [] #self.srvant.get_by_sid(metadata['id'])
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
                                                # ~ annotation['AID'],
                                                annotation['Timestamp']
                                            )
                        model.append(pid, node)

                # Load attachments
                # ~ files = self.srvatc.get_by_sid(metadata['id'])
                # ~ for fname in files:
                    # ~ with open(fname, 'r') as ft:
                        # ~ attachment = json.load(ft)
                        # ~ icon = self.srvicm.get_pixbuf_icon('basico-attachment')
                        # ~ node = self.get_node(   0,
                                                # ~ icon,
                                                # ~ False,
                                                # ~ '',
                                                # ~ attachment['Title'],
                                                # ~ 'Attachment',
                                                # ~ '',
                                                # ~ attachment['Description'],
                                                # ~ '',
                                                # ~ self.srvutl.fuzzy_date_from_timestamp(attachment['Created']),
                                                # ~ attachment['TID'],
                                                # ~ attachment['Created']
                                            # ~ )
                        # ~ model.append(pid, node)
        treeview = self.srvgui.get_widget('visor_sapnotes_treeview')
        treeview.set_model(sorted_model)
        self.update_total_sapnotes_count()
        self.show_widgets()
        # ~ self.srvclb.gui_stack_dashboard_show()


    def show_widgets(self):
        self.srvuif.set_widget_visibility('gtk_label_total_notes', True)


    def right_click(self, treeview, event, data=None):
        treeview = self.srvgui.get_widget('visor_sapnotes_treeview')
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
                sid = model[treeiter][COLUMN.KEY]
                if sid == 0:
                    return
                sid = "0"*(10 - len(str(sid))) + str(sid)
                # ~ toolbar = self.srvgui.get_widget('visortoolbar')
                popover = self.srvgui.add_widget('gtk_popover_visor_row', Gtk.Popover.new(treeview))
                popover.set_position(Gtk.PositionType.TOP)
                popover.set_pointing_to(rect)
                box = self.build_popover(sid, popover, component)
                popover.add(box)
                self.srvuif.popover_show(None, popover)


    # ~ def clb_create_annotation(self, button, sid):
        # ~ self.srvclb.action_annotation_create_for_sapnote(sid)


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
            # ~ button.connect('clicked', self.srvclb.action_annotation_delete)
            box.pack_start(button, False, False, 0)

            # Popover button "Duplicate annotation"
            button = get_popover_button("<b>Duplicate annotation</b>", 'basico-duplicate')
            button.show_all()
            # ~ button.connect('clicked', self.srvclb.action_annotation_duplicate)
            box.pack_start(button, False, False, 0)

        else:
            # Popover button "Add an annotation"
            button = get_popover_button("<b>Add an annotation</b> to SAP Note %d" % isid, 'basico-annotation')
            button.show_all()
            # ~ button.connect('clicked', self.clb_create_annotation, sid)
            box.pack_start(button, False, False, 0)

            fbox = Gtk.VBox()
            frame = Gtk.Frame()
            frame.set_border_width(3)
            label = Gtk.Label()
            label.set_markup(' <b>Attachments</b> ')
            frame.set_label_widget(label)
            # Popover button "Add attachments"
            button = get_popover_button("<b>Add</b> new to SAP Note %d" % isid, 'basico-attachment')
            button.set_property('margin', 3)
            button.show_all()
            # ~ button.connect('clicked', self.srvclb.gui_attachment_add_to_sapnote, sid)
            fbox.pack_start(button, False, False, 0)

            # Popover button "Open SAP Note"
            button = get_popover_button("<b>Browse</b> SAP Note %d" % isid, 'basico-preview')
            button.connect('clicked', self.srvweb.browse_note, sid)
            box.pack_start(button, False, False, 0)

            # Popover button "Download SAP Note in PDF"
            button = get_popover_button("See SAP Note %d in <b>PDF</b>" % isid, 'basico-browse')
            button.connect('clicked', self.srvweb.browse_pdf, sid)
            box.pack_start(button, False, False, 0)

            # Popover button "Bookmark"
            button = get_popover_button("<b>(Un)bookmark</b> SAP Note %d" % isid, 'basico-bookmarks')
            button.connect('clicked', self.srvsap.switch_bookmark, [sid], popover)
            box.pack_start(button, False, False, 0)

            # Popover button "Copy to clipboard"
            button = get_popover_button("<b>Copy</b> SAP Note %d details <b>to clipboard</b>" % isid, 'basico-clipboard')
            button.connect('clicked', self.copy_to_clipboard, [sid], popover)
            box.pack_start(button, False, False, 0)

            # Separator
            separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
            box.pack_start(separator, True, True, 0)

            # Assing SAP Notes in current view to a category
            # Only available in Donwloaded category
            menuview = self.srvgui.get_widget('menuview')
            current_menuview = menuview.get_view()
            current_collection = menuview.get_current_collection()
            view_is_collection = current_menuview == 'collection'
            collection_is_downloaded = current_collection == COL_DOWNLOADED

            # Popover button Collection Management
            button = get_popover_button("<b>Manage collections</b> for SAP Note %d" % isid, 'basico-collection')
            box.pack_start(button, False, False, 0)
            self.popcollections = self.srvgui.add_widget('gtk_popover_button_manage_collections_single_note', Gtk.Popover.new(button))
            self.popcollections.set_position(Gtk.PositionType.RIGHT)
            button.connect('clicked', self.srvuif.popover_show, self.popcollections)
            colmgt = CollectionsMgtView(self.app, sid, overwrite=True)
            self.popcollections.add(colmgt)

            # Separator
            separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
            box.pack_start(separator, True, True, 0)


            # Popover button "Delete SAP Note"
            visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
            button = get_popover_button("<b>Delete</b> SAP Note %d" % isid, 'basico-delete')
            button.connect('clicked', visor_sapnotes.delete, [sid])
            button.set_tooltip_text("Checkbox must be activated in order to trigger the deletion")
            box.pack_start(button, False, False, 0)

        return box


    def get_filtered_bag(self):
        clean_html = self.srvutl.clean_html
        sorted_model = self.srvgui.get_widget('visor_sapnotes_sorted_model')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        selected = []

        def get_selected_sapnotes(model, path, itr):
            sid = clean_html(model.get(itr, COLUMN.SID)[0])
            if len(escape(sid)) > 0:
                selected.append(str(sid))

        sorted_model.foreach(get_selected_sapnotes)
        return selected

    def display(self):
        stack_visors = self.srvgui.get_widget('gtk_stack_visors')
        stack_visors.set_visible_child_name('visor-sapnotes')

    def filter(self, *args):
        visible_filter = self.srvgui.get_widget('visor_sapnotes_visible_filter')
        visible_filter.refilter()
        self.update_total_sapnotes_count()

    def delete(self, *args):
        try:
            bag = args[1]
        except:
            bag = self.get_filtered_bag()
        self.log.warning("You are about to delete %d notes. Sure?", len(bag))
        # ~ visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        # ~ menuview = self.srvgui.get_widget('menuview')
        answer = self.srvuif.warning_message_delete_sapnotes(None, 'Deleting SAP Notes', 'Are you sure?', bag)
        if answer is True:
            self.srvdtb.delete(bag)
            self.log.info("Deleted %d SAP Notes", len(bag))
        else:
            self.log.info("Action canceled by user. Nothing deleted!")

    def copy_to_clipboard(self, widget, lsid, popover):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = ''
        for sid in lsid:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            text += "SAP Note %10s: %s - Component: %s\n" % (sid, metadata['title'], metadata['componentkey'])
        clipboard.set_text(text, -1)
        if popover is not None:
            popover.hide()
            self.srvuif.grab_focus()
        self.log.info("%d SAP Notes copied to clipboard", len(lsid))
