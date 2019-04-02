#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_menuview.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: MenuView Widget
"""

from enum import IntEnum
from html import escape
from collections import OrderedDict
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf
from dateutil import parser as dateparser
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.core.mod_wdg import BasicoWidget
from basico.services.srv_cols import COL_DOWNLOADED

class Row(IntEnum):
    ROWID = 0
    ROWNAME = 1
    ROWCOUNT = 2


class MenuView(BasicoWidget, Gtk.TreeView):
    view = 'component'
    current_status = None
    current_collection = None

    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.TreeView.__init__(self)
        self.row_type = None
        self.get_services()
        self.toggled = 0
        self.selected = set()
        self.count = 0
        self.completion = self.srvgui.add_widget('gtk_entrycompletion_viewmenu', Gtk.EntryCompletion())
        self.completion.set_match_func(self.completion_match_func)
        self.completion_model = Gtk.ListStore(str)
        self.completion.set_model(self.completion_model)
        self.completion.set_text_column(0)

        # Setup treeview and model
        Gtk.TreeView.__init__(self)
        self.model = Gtk.TreeStore(
            str,            # RowType@RowId
            str,            # RowName
            str,            # RowCount
        )
        self.set_model(self.model)

        # Setup columns
        # Row Id
        self.renderer_rowid = Gtk.CellRendererText()
        self.column_rowid = Gtk.TreeViewColumn('', self.renderer_rowid, text=Row.ROWID.value)
        self.column_rowid.set_visible(False)
        self.column_rowid.set_expand(False)
        self.column_rowid.set_clickable(False)
        self.column_rowid.set_sort_indicator(False)
        self.append_column(self.column_rowid)

        # Row Name
        self.renderer_rowname = Gtk.CellRendererText()
        self.column_rowname = Gtk.TreeViewColumn('', self.renderer_rowname, markup=Row.ROWNAME.value)
        self.column_rowname.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_rowname.set_visible(True)
        self.column_rowname.set_expand(True)
        self.column_rowname.set_clickable(True)
        self.column_rowname.set_sort_indicator(True)
        self.column_rowname.set_sort_column_id(1)
        self.column_rowname.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_rowname)

        # Row Count
        self.renderer_rowcount = Gtk.CellRendererText()
        self.renderer_rowcount.set_property('xalign', 0.5)
        self.renderer_rowcount.set_property('background', '#F0E3E3')
        self.column_rowcount = Gtk.TreeViewColumn('', self.renderer_rowcount, markup=Row.ROWCOUNT.value)
        self.column_rowcount.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_rowcount.set_visible(True)
        self.column_rowcount.set_expand(False)
        self.column_rowcount.set_clickable(False)
        self.column_rowcount.set_sort_indicator(False)
        self.column_rowcount.set_sort_column_id(2)
        self.column_rowcount.set_sort_order(Gtk.SortType.ASCENDING)
        self.append_column(self.column_rowcount)

        # TreeView common
        #~ self.set_level_indentation(6)
        self.set_can_focus(True)
        self.set_headers_visible(False)
        self.set_enable_search(True)
        self.set_hover_selection(False)
        self.set_grid_lines(Gtk.TreeViewGridLines.NONE)
        self.set_search_entry(self.srvgui.get_widget('stySearchInfo'))
        self.set_search_column(1)
        #~ self.set_row_separator_func(self.row_separator_func)

        # Selection
        self.selection = self.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        font_desc = Pango.FontDescription('Monospace 10')
        if font_desc:
            self.modify_font(font_desc)

        self.prepare()
        self.show_all()


    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvant = self.get_service('Annotation')
        self.srvuif = self.get_service('UIF')
        self.srvclt = self.get_service('Collections')
        self.srvutl = self.get_service('Utils')


    def get_node(self, rowid, rowname, rowcount='0'):
        completion = self.srvgui.get_widget('gtk_entrycompletion_viewmenu')
        completion_model = completion.get_model()
        title = self.srvutl.clean_html(rowname)
        completion_model.append([title])
        node = []
        node.append(rowid)
        node.append(rowname)
        node.append("%5s" % rowcount)

        return node


    def get_node_date_year(self, date, token_date, count='0'):
        title = "%s" % token_date
        return self.get_node('date-year@%s' % token_date, title, count)


    def get_node_date_month(self, date, token_date, count='0'):
        title = "%s" % date.strftime("%B")
        return self.get_node('date-month@%s' % token_date, title, count)


    def get_node_date_day(self, date, token_date, count='0'):
        title = "%s" % date.strftime("%d - %A")
        return self.get_node('date-day@%s' % token_date, title, count)


    def get_node_priority(self, priority, count='0'):
        if len(priority) == 0:
            title = "No priority assigned"
        else:
            title = "%s" % priority

        return self.get_node('priority@%s' % priority, title, count)


    def get_node_collection(self, collection_id, collection_name, count='0'):
        return self.get_node('collection@%s' % collection_id, collection_name, count)


    def get_node_type(self, sntype, count='0'):
        if len(sntype) == 0:
            title = "SAP Note type not found"
        else:
            title = "%s" % sntype
        return self.get_node('type@%s' % sntype, title, count)


    def get_row_id(self):
        return self.cid


    def get_row_type(self):
        return self.row_type


    def get_node_category(self, category='', count='0'):
        if len(category) == 0:
            catname = "No category assigned"
        else:
            catname = "%s" % category
        return self.get_node('category@%s' % catname, catname, count)


    def get_node_component(self, compkey, comptxt, count='0'):
        return self.get_node('componentkey@%s' % compkey, compkey, count)


    def get_node_component_desc(self, compkey, comptxt, count='0'):
        icon = self.srvicm.get_icon('basico-description', 32, 32)
        node = []
        count = len(self.srvdtb.get_notes_by_node("componentkey", compkey))
        if len(comptxt) == 0:
            component = "%s" % (compkey)
        else:
            component = "%s" % (comptxt)
        return self.get_node('componentkey@%s' % compkey, component, count)


    def completion_match_func(self, completion, key, treeiter):
        model = completion.get_model()
        text = model.get_value(treeiter, 0)
        if key.upper() in text.upper():
            return True
        return False


    def prepare(self):
        self.column_rowid.set_visible(False)
        self.column_rowname.set_visible(True)
        self.column_rowcount.set_visible(True)

        # TreeView common
        self.set_can_focus(True)
        self.set_headers_visible(False)
        self.set_enable_search(True)
        self.set_hover_selection(False)
        self.set_grid_lines(Gtk.TreeViewGridLines.NONE)
        self.set_level_indentation(0)
        signal = self.selection.connect('changed', self.row_changed)
        self.srvgui.set_key_value('menuview-selection', self.selection)
        self.srvgui.set_key_value('menuview-row-changed', signal)
        self.connect('button_press_event', self.right_click)


    def refresh(self):
        visor = self.srvgui.get_widget('visor_sapnotes')
        try:
            if self.row_type is not None:
                matches = self.srvdtb.get_notes_by_node(self.row_type, self.cid)
                visor.populate_sapnotes(matches)
        except Exception as error:
            pass


    def row_changed(self, selection):
        if self.current_status is None:
            visor = self.srvgui.get_widget('visor_sapnotes')
            self.srvclb.gui_show_visor_sapnotes()

            try:
                model, treeiter = selection.get_selected()
                row = model[treeiter][0]
                row_title = self.srvutl.clean_html(model[treeiter][1])
                self.row_type, self.cid = row.split('@')
                iter_has_child = model.iter_has_child(treeiter)
                if self.row_type == 'collection':
                    colname = self.srvclt.get_name_by_cid(self.cid)
                    self.set_current_collection(self.cid)
                    if not iter_has_child:
                        matches = self.srvdtb.get_notes_by_node(self.row_type, self.cid)
                        visor.populate_sapnotes(matches, self.cid)
                    else:
                        matches = set()
                        cols = self.srvclt.get_collections_by_row_title(row_title)
                        for col in cols:
                            for sid in self.srvdtb.get_notes_by_node(self.row_type, col):
                                matches.add(sid)
                        visor.populate_sapnotes(list(matches))
                else:
                    self.set_current_collection(None)
                    matches = self.srvdtb.get_notes_by_node(self.row_type, self.cid)
                    visor.populate_sapnotes(matches, self.cid)
                self.srvuif.statusbar_msg("View populated with %d SAP Notes" % (len(matches)))
            except Exception as error:
                pass


    def set_current_collection(self, cid=None):
        self.current_collection = cid


    def get_current_collection(self):
        return self.current_collection


    def show_popover_manage_collections(self, *args):
        button = self.srvgui.get_widget('gtk_button_popover_manage_collections')
        popcollections = self.srvgui.add_widget('gtk_popover_button_manage_collections_single_note', Gtk.Popover.new(button))
        popcollections.set_position(Gtk.PositionType.RIGHT)
        popcollections.add(CollectionsMgtView(self.app, '0000000000'))
        self.srvclb.gui_show_popover(None, popcollections)


    def show_popover_export_collections(self, *args):
        popexport = self.srvgui.get_widget('gtk_popover_menuview_export')
        self.srvclb.gui_show_popover(None, popexport)


    def build_popover_export(self, colname):
        box = Gtk.Box(spacing = 3, orientation="vertical")
        sid = '0000000000'

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

        # Popover button "export to CSV"
        button = get_popover_button("Export to <b>csv</b>", 'basico-backup-text-csv')
        self.srvgui.add_widget("gtk_button_popover_manage_collections", button)
        button.connect('clicked', self.srvclb.action_collection_export_text_csv)
        box.pack_start(button, False, False, 0)

        # Popover button "export to Excel"
        button = get_popover_button("Export to <b>Excel</b>", 'basico-backup-ms-excel')
        self.srvgui.add_widget("gtk_button_popover_manage_collections", button)
        button.connect('clicked', self.srvclb.action_collection_export_excel)
        box.pack_start(button, False, False, 0)

        # Popover button "export to Basico format"
        button = get_popover_button("Export to <b>Basico format</b>", 'basico-component')
        self.srvgui.add_widget("gtk_button_popover_manage_collections", button)
        button.connect('clicked', self.srvclb.action_collection_export_basico)
        box.pack_start(button, False, False, 0)

        return box


    def build_popover(self, colid, colname):
        box = Gtk.Box(spacing = 3, orientation="vertical")
        sid = '0000000000'

        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        count = len(visor_sapnotes.get_filtered_bag())
        if count == 0:
            count = len(visor_sapnotes.get_filtered_bag())

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

        # Popover button Manage collections
        button = get_popover_button("<b>Manage collections</b>", 'basico-category')
        self.srvgui.add_widget("gtk_button_popover_manage_collections", button)
        button.connect('clicked', self.show_popover_manage_collections)
        box.pack_start(button, False, False, 0)

        # Separator
        separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
        box.pack_start(separator, True, True, 0)

        # Popover button copy to clipboard
        button = get_popover_button("<b>Copy to clipboard</b> %d SAP Notes" % count, 'basico-clipboard')
        button.connect('clicked', self.srvclb.action_collection_copy_to_clipboard)
        box.pack_start(button, False, False, 0)

        # Popover button "Export collection"
        button = get_popover_button("<b>Export</b> %d SAP Notes" % count, 'basico-backup')
        self.srvgui.add_widget("gtk_button_popover_export_collections", button)
        button.connect('clicked', self.show_popover_export_collections)
        box.pack_start(button, False, False, 0)

        popover = self.srvgui.add_widget('gtk_popover_menuview_export', Gtk.Popover.new(button))
        popover.set_position(Gtk.PositionType.RIGHT)
        popover.add(self.build_popover_export(colname))

        # Popover button "Link SAP Notes  in view to collection(s)"
        button = get_popover_button("<b>Link to collection(s)</b> %d SAP Notes" % count, 'basico-collection')
        box.pack_start(button, False, False, 0)
        self.popviewtocat = self.srvgui.add_widget('gtk_popover_button_assign_view_to_category', Gtk.Popover.new(button))
        self.popviewtocat.set_position(Gtk.PositionType.RIGHT)
        button.connect('clicked', self.srvclb.gui_show_popover, self.popviewtocat)
        colmgt = CollectionsMgtView(self.app, 'view', overwrite=False)
        self.popviewtocat.add(colmgt)

        # Popover button "Bookmark all SAP Notes in this view"
        button = get_popover_button("<b>(Un)Bookmark</b> %d SAP Notes in this view" % count, 'basico-bookmarks')
        button.connect('clicked', self.srvclb.switch_bookmark_current_view)
        box.pack_start(button, False, False, 0)

        # Popover button "Delete all SAP Notes in this view"
        button = get_popover_button("<b>Delete</b> %d SAP Notes in this view" % count, 'basico-delete')
        button.connect('clicked', self.srvclb.sapnote_delete_view)
        box.pack_start(button, False, False, 0)

        return box


    def right_click(self, treeview, event, data=None):
        selection = treeview.get_selection()
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.x = x = int(event.x)
            rect.y = y = int(event.y)
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                selection.select_path(path) # -> Force select current path
                model = treeview.get_model()
                treeiter = model.get_iter(path)
                rid = model[treeiter][0]
                coltitle = model[treeiter][1]
                colid = model[treeiter][0]
                rtype = rid[:rid.find('@')]
                try:
                    colid = rid[rid.find('@')+1:]
                except:
                    colid = None
                popover = self.srvgui.add_widget('gtk_popover_menuview', Gtk.Popover.new(treeview))
                popover.set_position(Gtk.PositionType.RIGHT)
                popover.set_pointing_to(rect)
                popover.add(self.build_popover(colid, coltitle))
                self.srvclb.gui_show_popover(None, popover)


    def set_view(self, view=None):
        # FIXME: Get last view visited from config
        if view is None:
            view = 'chronologic'

        iconview = self.srvgui.get_widget('gtk_image_current_view')
        icon = self.srvicm.get_pixbuf_icon('basico-%s' % view, 24, 24)
        iconview.set_from_pixbuf(icon)
        iconview.show_all()
        self.view = view

        # Change label
        viewlabel = self.srvgui.get_widget('gtk_label_current_view')
        name = "<b>%s</b>" % view.capitalize()
        viewlabel.set_markup(name)
        viewlabel.set_xalign(0.0)
        viewlabel.set_justify(Gtk.Justification.LEFT)
        viewlabel.show_all()
        self.populate([])
        self.srvuif.statusbar_msg("Switching to <i>%s</i> view" % name)


    def get_view(self):
        return self.view


    def populate(self, sapnotes=[]):
        self.current_status = "working"
        self.set_headers_visible(False) # Set
        completion = self.srvgui.get_widget('gtk_entrycompletion_viewmenu')
        completion_model = completion.get_model()
        completion_model.clear()

        if len(sapnotes) == 0:
            sapnotes = self.srvdtb.get_notes()

        if self.view == 'component':
            self.populate_by_components(sapnotes)
        elif self.view == 'description':
            self.populate_by_component_descriptions(sapnotes)
        elif self.view == 'bookmarks':
            self.populate_by_bookmarks()
        elif self.view == 'projects':
            self.populate_by_projects(sapnotes)
        elif self.view == 'collections':
            self.populate_by_collections(sapnotes)
        elif self.view == 'tags':
            self.populate_by_tags(sapnotes)
        elif self.view == 'category':
            self.populate_by_category(sapnotes)
        elif self.view == 'chronologic':
            self.populate_by_chronologic(sapnotes)
        elif self.view == 'priority':
            self.populate_by_priority(sapnotes)
        elif self.view == 'type':
            self.populate_by_type(sapnotes)
        elif self.view == 'collection':
            self.populate_by_collection(sapnotes)
        elif self.view == 'annotation':
            self.populate_annotations()
        else:
            self.populate_by_components(sapnotes)

        viewfilter = self.srvgui.get_widget('gtk_entry_filter_view')
        completion = self.srvgui.get_widget('gtk_entrycompletion_viewmenu')
        completion.set_model(completion_model)
        viewfilter.set_completion(completion)
        self.srvclb.gui_show_dashboard()
        self.current_status = None


    def populate_by_bookmarks(self):
        matches = []
        sapnotes = self.srvdtb.get_notes()
        for sid in sapnotes:
            if sapnotes[sid]['bookmark']:
                matches.append(sid)
        matches.sort()

        visor = self.srvgui.get_widget('visor_sapnotes')
        visor.populate_sapnotes(matches)
        self.srvuif.statusbar_msg("View <i>%s</i> populated with %d SAP Notes" % (self.row_type, len(matches)))


    def populate_by_components(self, sapnotes, only_bookmarks=False):
        self.model.clear()
        self.treepids = {}

        if len(sapnotes) == 0:
            return

        scomp = set()
        dcomp = {}

        for sid in sapnotes:
            compkey = escape(sapnotes[sid]['componentkey'])
            comptxt = escape(sapnotes[sid]['componenttxt'])
            scomp.add(compkey)
            dcomp[compkey] = comptxt
        lcomp = list(scomp)
        lcomp.sort()

        for compkey in lcomp:
            subkeys = compkey.split('-')
            ppid = None
            for i in range(1, len(subkeys)+1):
                key = ('-').join(subkeys[0:i])
                try:
                    ppid = self.treepids[key]
                except:
                    if i == len(subkeys):
                        title = dcomp[compkey]
                    else:
                        title = ""
                    count = len(self.srvdtb.get_notes_by_node('componentkey', key))
                    node = self.get_node_component(key, title, str(count))
                    ppid = self.model.append(ppid, node)
                    self.treepids[key] = ppid


    def populate_by_priority(self, sapnotes):
        self.model.clear()
        treepids = {}

        if len(sapnotes) == 0:
            return

        scomp = set()
        dcomp = {}
        pset = set()

        for sid in sapnotes:
            try:
                priority = sapnotes[sid]['priority']
                pset.add(priority)
            except: pass

        plist = []
        plist.extend(pset)
        plist.sort()

        for priority in plist:
            count = len(self.srvdtb.get_notes_by_node('priority', priority))
            node = self.get_node_priority(priority, count)
            pid = self.model.append(None, node)
            treepids[priority] = pid


    def populate_by_type(self, sapnotes):
        self.model.clear()
        treepids = {}

        if len(sapnotes) == 0:
            return

        scomp = set()
        dcomp = {}
        pset = set()

        for sid in sapnotes:
            try:
                sntype = sapnotes[sid]['type']
                pset.add(sntype)
            except: pass

        plist = []
        plist.extend(pset)
        plist.sort()

        for sntype in plist:
            count = len(self.srvdtb.get_notes_by_node('type', sntype))
            node = self.get_node_type(sntype, count)
            pid = self.model.append(None, node)
            treepids[sntype] = pid


    def populate_by_component_descriptions(self, sapnotes, only_bookmarks=False):
        self.model.clear()
        self.treepids = {}

        if len(sapnotes) == 0:
            return

        scomp = set()
        dcomp = {}

        for sid in sapnotes:
            compkey = escape(sapnotes[sid]['componentkey'])
            comptxt = escape(sapnotes[sid]['componenttxt'])
            scomp.add(compkey)
            dcomp[compkey] = comptxt
        lcomp = list(scomp)
        lcomp.sort()

        for compkey in lcomp:
            subkeys = compkey.split('-')
            ppid = None
            for i in range(1, len(subkeys)+1):
                key = ('-').join(subkeys[0:i])
                try:
                    ppid = self.treepids[key]
                except:
                    if i == len(subkeys):
                        title = dcomp[compkey]
                    else:
                        title = ""
                    count = len(self.srvdtb.get_notes_by_node('componentkey', key))
                    node = self.get_node_component_desc(key, title, str(count))
                    ppid = self.model.append(ppid, node)
                    self.treepids[key] = ppid


    def populate_by_category(self, sapnotes):
        self.model.clear()
        treepids = {}

        if len(sapnotes) == 0:
            return

        scomp = set()
        dcomp = {}
        catset = set()

        for sid in sapnotes:
            try:
                cat = sapnotes[sid]['category']
                catset.add(cat)
            except: pass

        catlist = []
        catlist.extend(catset)
        catlist.sort()

        for cat in catlist:
            count = len(self.srvdtb.get_notes_by_node('category', cat))
            node = self.get_node_category(cat, str(count))
            pid = self.model.append(None, node)
            treepids[cat] = pid


    def populate_by_collection(self, sapnotes):
        treepids = {}
        scomp = set()
        dcomp = {}
        self.model.clear()
        
        # Add Downloaded collection
        cid = self.srvclt.get_cid_by_name('Downloaded')
        count = len(self.srvdtb.get_notes_by_node('collection', cid))
        node = self.get_node_collection(cid, "<span color='black'><b>Downloaded</b></span>", str(count))
        treepids['Downloaded'] = self.model.append(None, node)

        collections = self.srvclt.get_all()
        od = OrderedDict(sorted(collections.items(), key=lambda t: t[1]))
        if len(od) > 0:
            for cid in od:
                colname = self.srvclt.get_name_by_cid(cid)
                if cid == COL_DOWNLOADED:
                    continue

                compkey = od[cid]
                subkeys = compkey.split(' ')
                ppid = None
                for i in range(1, len(subkeys)+1):
                    key = (' ').join(subkeys[0:i])
                    try:
                        ppid = treepids[key]
                    except:
                        title = key
                        if title == compkey:
                            matches = set()
                            cols = self.srvclt.get_collections_by_row_title(title)
                            for col in cols:
                                for sid in self.srvdtb.get_notes_by_node('collection', col):
                                    matches.add(sid)
                            node = self.get_node_collection(cid, title, str(len(matches)))
                        else:

                            matches = set()
                            cols = self.srvclt.get_collections_by_row_title(title)
                            for col in cols:
                                for sid in self.srvdtb.get_notes_by_node('collection', col):
                                    matches.add(sid)
                            node = self.get_node_collection('', title, str(len(matches)))
                        ppid = self.model.append(ppid, node)
                        treepids[key] = ppid
        else:
            node = self.get_node_collection('', 'No collections available yet')
            self.model.append(None, node)


    def populate_annotations(self, annotations=None):
        visor = self.srvgui.get_widget('visor_annotations')
        visor.populate_annotations(annotations)


    def populate_by_chronologic(self, sapnotes):
        self.model.clear()
        treepids = {}

        if len(sapnotes) == 0:
            return

        years = set()
        months = set()
        days = set()
        for sid in sapnotes:
            try:
                downloaded = dateparser.parse(sapnotes[sid]['feedupdate'])
                year = "%d" % downloaded.year
                month = "%02d" % downloaded.month
                day = "%02d" % downloaded.day
                key_year = year
                key_month = year + month
                key_day = year + month + day
                years.add(key_year)
                months.add(key_month)
                days.add(key_day)
            except:
                pass
        years = list(years)
        years.sort(reverse=True)
        months = list(months)
        months.sort(reverse=True)
        days = list(days)
        days.sort(reverse=True)

        for key_year in years:
            try:
                treepids[key_year]
            except:
                adate = key_year + '0101'
                downloaded = dateparser.parse(adate)
                count = len(self.srvdtb.get_notes_by_node('date-year', key_year))
                node = self.get_node_date_year(downloaded, key_year, str(count))
                treepids[key_year] = self.model.append(None, node)

        for key_month in months:
            try:
                treepids[key_month]
            except:
                adate = key_month + '01'
                downloaded = dateparser.parse(adate)
                count = len(self.srvdtb.get_notes_by_node('date-month', key_month))
                node = self.get_node_date_month(downloaded, key_month, str(count))
                key_year = key_month[0:4]
                treepids[key_month] = self.model.append(treepids[key_year], node)

        for key_day in days:
            try:
                treepids[key_day]
            except:
                downloaded = dateparser.parse(key_day)
                count = len(self.srvdtb.get_notes_by_node('date-day', key_day))
                key_month = key_day[0:6]
                node = self.get_node_date_day(downloaded, key_day, str(count))
                treepids[key_day] = self.model.append(treepids[key_month], node)

