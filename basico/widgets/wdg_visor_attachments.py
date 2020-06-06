#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_visor_attachments.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Attachments Visor
"""

import os
from os.path import sep as SEP
from html import escape
import glob
import json
import html
import shutil
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


# ~ total, used, free = shutil.disk_usage('/home/t00m/.basico/opt/webdrivers/geckodriver')
# ~ ft = float(ceil(total/(1024*1024*1024)))
# ~ ff = float(ceil(free/(1024*1024*1024)))
# ~ pf = (ft-ff)*100/ft

# ~ ft = int(ceil(total/(1024*1024*1024)))
# ~ ff = int(ceil(free/(1024*1024*1024)))
# ~ pf = (ft-ff)*100/ft

class AttachmentsVisor(BasicoWidget, Gtk.VBox):
    def __init__(self, app):
        super().__init__(app, __class__.__name__)
        Gtk.HBox.__init__(self, app)
        self.set_homogeneous(False)
        self.bag = []
        self.get_services()
        self.setup_visor()
        self.icons = {}
        self.icons['type'] = {}
        for atype in ATYPES:
            self.icons['type'][atype.lower()] = self.srvicm.get_pixbuf_icon('basico-attachment-type-%s' % atype.lower())
        self.log.debug("Attachments Visor initialized")
        self.populate()


    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvuif = self.get_service("UIF")
        self.srvutl = self.get_service("Utils")
        self.srvatc = self.get_service('Attachment')
        self.srvant = self.get_service('Annotation')


    def get_treeview(self):
        return self.treeview


    def sort_by_timestamp(self):
        self.sorted_model.set_sort_column_id(7, Gtk.SortType.DESCENDING)


    def setup_visor(self):
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        self.treeview = Gtk.TreeView()
        scr.add(self.treeview)
        scr.set_hexpand(True)
        self.pack_start(scr, True, True, 0)

        hbox = Gtk.HBox()
        pgb = self.srvgui.add_widget('gtk_progressbar_diskusage', Gtk.ProgressBar())
        fraction = self.srvutl.get_disk_usage_fraction(LPATH['DB'])
        text = self.srvutl.get_disk_usage_human(LPATH['DB'])
        pgb.set_fraction(fraction)
        pgb.set_text(text)
        pgb.set_show_text(True)
        hbox.pack_start(pgb, True, True, 0)
        self.pack_start(hbox, False, False, 0)

        # Setup model
        self.model = Gtk.TreeStore(
            str,        # TID (Attachment ID)
            Pixbuf,     # Icon
            str,        # SAP Note
            str,        # Document Type
            str,        # Title
            str,        # Description
            str,        # Added
            str,        # Added (timestamp)
            str,        # Size
            int,        # Size (int)
            str,        # Mimetype
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

        # TID (Attachment ID)
        self.renderer_key = Gtk.CellRendererText()
        self.column_key = Gtk.TreeViewColumn('TID', self.renderer_key, text=0)
        self.column_key.set_visible(False)
        self.column_key.set_expand(False)
        # ~ self.column_key.set_clickable(False)
        # ~ self.column_key.set_sort_indicator(False)
        self.treeview.append_column(self.column_key)

        # Icon
        self.renderer_icon = Gtk.CellRendererPixbuf()
        self.renderer_icon.set_alignment(0.0, 0.5)
        self.column_icon = Gtk.TreeViewColumn('', self.renderer_icon, pixbuf=1)
        # ~ widget = get_column_header_widget('', 'basico-attachment')
        # ~ self.column_icon.set_widget(widget)
        self.column_icon.set_visible(True)
        self.column_icon.set_expand(False)
        self.column_icon.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_icon.set_expand(False)
        self.column_icon.set_clickable(True)
        self.column_icon.set_sort_indicator(True)
        self.column_icon.set_sort_column_id(10)
        self.treeview.append_column(self.column_icon)

        # Document Type
        self.renderer_doctype = Gtk.CellRendererText()
        self.renderer_doctype.set_property('background', '#FFEEAF')
        self.column_doctype = Gtk.TreeViewColumn('Document type', self.renderer_doctype, markup=2)
        self.column_doctype.set_visible(False)
        self.column_doctype.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_doctype.set_expand(False)
        self.column_doctype.set_clickable(True)
        self.column_doctype.set_sort_indicator(True)
        self.column_doctype.set_sort_column_id(2)
        self.treeview.append_column(self.column_doctype)

        # Description
        self.renderer_description = Gtk.CellRendererText()
        self.renderer_description.set_property('background', '#E3E3F0')
        self.column_description = Gtk.TreeViewColumn('Description', self.renderer_description, markup=3)
        # ~ widget = get_column_header_widget('Description', 'basico-component')
        # ~ self.column_description.set_widget(widget)
        self.column_description.set_visible(True)
        self.column_description.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_description.set_expand(False)
        self.column_description.set_clickable(True)
        self.column_description.set_sort_indicator(True)
        self.column_description.set_sort_column_id(3)
        self.treeview.append_column(self.column_description)

        # Attachment Title
        self.renderer_title = Gtk.CellRendererText()
        self.renderer_title.set_property('background', '#FFFEEA')
        self.renderer_title.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        self.column_title = Gtk.TreeViewColumn('Title', self.renderer_title, markup=4)
        # ~ widget = get_column_header_widget('Title', 'basico-tag')
        # ~ self.column_title.set_widget(widget)
        self.column_title.set_visible(True)
        self.column_title.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_title.set_expand(True)
        self.column_title.set_clickable(True)
        self.column_title.set_sort_indicator(True)
        self.column_title.set_sort_column_id(4)
        self.treeview.append_column(self.column_title)

        # SAP Note Id
        self.renderer_sid = Gtk.CellRendererText()
        self.renderer_sid.set_property('xalign', 1.0)
        self.renderer_sid.set_property('height', 36)
        self.renderer_sid.set_property('background', '#F0E3E3')
        self.column_sid = Gtk.TreeViewColumn('SAP Note', self.renderer_sid, markup=5)
        # ~ widget = get_column_header_widget('SAP Note', 'basico-sid')
        # ~ self.column_sid.set_widget(widget)
        self.column_sid.set_visible(True)
        self.column_sid.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_sid.set_expand(False)
        self.column_sid.set_clickable(True)
        self.column_sid.set_sort_indicator(True)
        self.column_sid.set_sort_column_id(5)
        self.treeview.append_column(self.column_sid)

        # Added
        self.renderer_added = Gtk.CellRendererText()
        self.renderer_added.set_property('background', '#E3F1E3')
        self.column_added = Gtk.TreeViewColumn('Added', self.renderer_added, markup=6)
        # ~ widget = get_column_header_widget('Added', 'basico-category')
        # ~ self.column_added.set_widget(widget)
        self.column_added.set_visible(True)
        self.column_added.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column_added.set_expand(False)
        self.column_added.set_clickable(True)
        self.column_added.set_sort_indicator(True)
        self.column_added.set_sort_column_id(7)
        self.treeview.append_column(self.column_added)

        # Added (timestamp)
        self.renderer_addedts = Gtk.CellRendererText()
        self.column_addedts = Gtk.TreeViewColumn('Added', self.renderer_addedts, text=7)
        self.column_addedts.set_visible(False)
        self.treeview.append_column(self.column_addedts)

        # Size
        self.renderer_size = Gtk.CellRendererText()
        self.renderer_size.set_property('background', '#e4f1f1')
        self.column_size = Gtk.TreeViewColumn('Size', self.renderer_size, markup=8)
        self.column_size.set_visible(True)
        self.column_size.set_expand(False)
        self.column_size.set_clickable(True)
        self.column_size.set_sort_indicator(True)
        self.column_size.set_sort_column_id(9)
        self.treeview.append_column(self.column_size)

        # Size (int)
        self.renderer_sizeint = Gtk.CellRendererText()
        self.renderer_sizeint.set_property('background', '#FFE6D1')
        self.column_sizeint = Gtk.TreeViewColumn('SizeInt', self.renderer_sizeint, text=9)
        self.column_sizeint.set_visible(False)
        self.column_sizeint.set_clickable(True)
        self.column_sizeint.set_sort_indicator(True)
        self.column_sizeint.set_sort_column_id(9)
        self.treeview.append_column(self.column_sizeint)

        # Mimetype
        self.renderer_annotation = Gtk.CellRendererText()
        self.column_annotation = Gtk.TreeViewColumn('Mimetype', self.renderer_annotation, markup=10)
        self.column_annotation.set_visible(False)
        self.treeview.append_column(self.column_annotation)

        # Treeview properties
        self.treeview.set_can_focus(False)
        self.treeview.set_enable_tree_lines(True)
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_hover_selection(False)
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        self.treeview.set_enable_tree_lines(True)
        self.treeview.set_level_indentation(10)
        self.treeview.connect('button_press_event', self.row_right_click)

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
        # ~ self.selection.connect('changed', self.row_changed)

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


    def update_total_attachments_count(self):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        lblnotescount = self.srvgui.get_widget('gtk_label_total_notes')
        total = self.srvatc.get_total()
        count = len(self.visible_filter)
        lblnotescount.set_markup("<b>%d/<big>%d attachments</big></b>" % (count, total))
        msg = 'View populated with %d attachments' % count
        # ~ self.srvuif.statusbar_msg(msg)


    def get_visible_filter(self):
        return self.visible_filter


    # ~ def row_changed(self, selection):
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
                    # ~ self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
        # ~ except Exception as error:
            # ~ head = "Error reading annotation's contents"
            # ~ body = "<i>%s</i>\n\n" % error
            # ~ body += "As a workaround, a new file will be created"
            # ~ dialog = self.srvuif.message_dialog_error(head, body)
            # ~ self.log.debug(error)
            # ~ self.log.debug(self.get_traceback())
            # ~ dialog.run()
            # ~ dialog.destroy()
            # ~ #FIXME: create an empty file for contents


    def toggle_checkbox(self, cell, path):
        path = self.sorted_model.convert_path_to_child_path(Gtk.TreePath(path))
        self.model[path][2] = not self.model[path][2]


    def get_node(self, key, icon, sid, title, description, added, timestamp, size, sizeint, mimetype, doctype):
        # Add completion entries
        # ~ completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        # ~ completion_model = completion.get_model()
        # ~ title = self.srvutl.clean_html(title)
        # ~ completion_model.append([title])

        node = []
        node.append(key)
        node.append(icon)
        node.append(sid)
        node.append(title)
        node.append(description)
        node.append(added)
        node.append(timestamp)
        node.append(size)
        node.append(sizeint)
        node.append(mimetype)
        node.append(doctype)
        return node


    def set_bag(self, attachments):
        self.bag = attachments


    def get_bag(self):
        return self.bag


    def reload(self):
        bag = self.get_bag()
        self.populate(bag)


    def populate(self, attachments=None):
        # ~ completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        # ~ completion_model = completion.get_model()
        # ~ completion_model.clear()

        self.treeview.set_model(None)
        self.model.clear()

        if attachments is None:
            attachments = self.srvatc.get_all()
        else:
            self.set_bag(attachments)

        dcats = {}
        snpids = {}
        nodes = []
        for fname in attachments:
            try:
                with open(fname, 'r') as fa:
                    try:
                        metadata = json.load(fa)
                        sid = self.srvatc.get_sid(metadata['TID'])
                        sid = str(int(sid))
                        if sid == '0':
                            sid = ''
                        node = self.get_node(   metadata['TID'],
                                                self.srvicm.find_mime_type_pixbuf(metadata['Mimetype'], 36, 36),
                                                metadata['Doctype'],
                                                metadata['Description'],
                                                metadata['Title'],
                                                sid,
                                                self.srvutl.fuzzy_date_from_timestamp(metadata['Created']),
                                                metadata['Created'],
                                                str(self.srvutl.get_human_sizes(int(metadata['Size']))),
                                                int(metadata['Size']),
                                                metadata['Mimetype'],
                                            )
                        nodes.append(node)
                    except Exception as error:
                        self.log.error(error)
                        self.log.error(self.get_traceback())
            except Exception as error:
                # Whenever an annotation is deleted, after reloading
                # the view, it fails. Then, skip it
                self.log.error("Attachment: %s", fname)
                self.log.error(error)

        for node in nodes:
            self.model.append(None, node)

        self.treeview.set_model(self.sorted_model)
        self.sort_by_timestamp()
        self.update_total_attachments_count()
        # ~ self.log.debug("Visor updated")

    def show_widgets(self):
        self.srvuif.set_widget_visibility('gtk_label_total_notes', True)


    def row_right_click(self, treeview, event, data=None):
        if event.button == 3:
            rect = Gdk.Rectangle()
            rect.x = x = int(event.x)
            rect.y = y = int(event.y)
            pthinfo = self.treeview.get_path_at_pos(x,y)
            if pthinfo is not None:
                path,col,cellx,celly = pthinfo
                model = treeview.get_model()
                treeiter = model.get_iter(path)
                tid = model[treeiter][0]
                # ~ toolbar = self.srvgui.get_widget('visortoolbar')
                popover = self.srvgui.add_widget('gtk_popover_visor_row', Gtk.Popover.new(treeview))
                popover.set_position(Gtk.PositionType.TOP)
                popover.set_pointing_to(rect)
                box = self.build_popover(tid, popover)
                if box is not None:
                    popover.add(box)
                    self.srvuif.popover_show(None, popover)


    def build_popover(self, tid, popover):
        sid = self.srvatc.get_sid(tid)
        aid = self.srvatc.get_metadata_value(tid, 'AID')
        self.log.debug("%s -> %s", tid, sid)

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

        box = Gtk.Box(spacing = 3, orientation="vertical")

        # ~ # Popover button "Delete annotation"
        # ~ button = get_popover_button("<b>Delete</b> annotation", 'basico-delete')
        # ~ button.show_all()
        # ~ button.connect('clicked', self.srvclb.action_annotation_delete)
        # ~ box.pack_start(button, False, False, 0)

        # Copy identifier to clipboard
        button = get_popover_button("<b>Copy identifier</b> to clipboard", 'basico-copy-paste')
        button.show_all()
        # ~ button.connect('clicked', self.srvclb.copy_text_to_clipboard, tid)
        box.pack_start(button, False, False, 0)

        # ~ if sid != '0000000000':
            # ~ # Jump to SAP Note
            # ~ button = get_popover_button("Jump to <b>SAP Note %d</b>" % int(sid), 'basico-jump-sapnote')
            # ~ button.show_all()
            # ~ button.connect('clicked', self.srvclb.gui_jump_to_sapnote, sid)
            # ~ box.pack_start(button, False, False, 0)

        if self.srvant.is_valid(aid):
           # Jump to Annotation
            # ~ aid_file = LPATH['ANNOTATIONS'] + aid + '.json'
            # ~ button = get_popover_button("Jump to <b>Annotation</b>", 'basico-jump-sapnote')
            # ~ button.show_all()
            # ~ button.connect('clicked', self.srvclb.gui_jump_to_annotation, aid_file)
            # ~ box.pack_start(button, False, False, 0)

        # Separator
        separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
        box.pack_start(separator, True, True, 0)

        # Download to PC
        button = get_popover_button("<b>Download attachment</b> to PC", 'basico-backup')
        button.show_all()
        button.connect('clicked', self.download, tid)
        box.pack_start(button, False, False, 0)

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


    def download(self, widget, tid):
        filename = self.srvatc.get_metadata_value(tid, 'Title')
        target_folder = self.srvuif.select_folder()
        if target_folder is not None:
            source = LPATH['ATTACHMENTS'] + tid
            target = os.path.join(target_folder, filename)
            shutil.copy(source, target)
            msg = "Attachment downloaded to %s" % (target)
            self.log.debug(msg)
            # ~ self.srvuif.statusbar_msg(msg)

