#!/usr/bin/python
"""
# -*- coding: utf-8 -*-
# File: wdg_cols.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Collections Managemnet Widget
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from basico.core.mod_wdg import BasicoWidget
from basico.services.srv_cols import COL_DOWNLOADED


class CollectionsMgtView(BasicoWidget, Gtk.VBox):
    __gtype_name__ = 'CollectionsMgtView'
    """
    Missing class docstring (missing-docstring)
    """
    def __init__(self, app, sid, overwrite=False): 
        super().__init__(app, __class__.__name__)
        Gtk.VBox.__init__(self)
        self.sid = sid     
        self.current_cid = None
        self.overwrite = overwrite
        self.log.debug("CollectionsMgtView widget overwrite mode is %s", overwrite)
        self.get_services()
        self.setup()
        self.update()


    def get_services(self):
        """
        Load services to be used in this class
        """
        self.srvgui = self.get_service("GUI")
        self.srvicm = self.get_service("IM")
        self.srvuif = self.get_service("UIF")
        self.srvclt = self.get_service('Collections')
        self.srvdtb = self.get_service('DB')


    def setup(self):
        """
        Missing method docstring (missing-docstring)
        """
        # Setup Widget properties
        self.set_size_request(400, 680)
        self.set_property('margin', 3)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # CollectionMgt Header
        header = Gtk.VBox()
        hbox = Gtk.HBox()
        icon = self.srvicm.get_new_image_icon('basico-collection')
        title = Gtk.Label()
        if self.sid == '0000000000':
            title.set_markup('<big><b>Manage collections</b></big>')
        elif self.sid == 'view':
            title.set_markup('<big><b>Manage collections for this view</b></big>') 
        else:
            title.set_markup('<big><b>Collections for SAP Note %s</b></big>' % str(int(self.sid)))
        title.set_xalign(0.0)
        hbox.pack_start(icon, False, False, 6)
        hbox.pack_start(title, True, True, 0)
        separator = Gtk.Separator()
        header.pack_start(hbox, False, False, 0)
        header.pack_start(separator, False, False, 3)
        self.pack_start(header, False, False, 3)

        # Entry Widget /  Delete entry button
        hbox = Gtk.HBox()
        self.entry = self.srvgui.add_widget('gtk_entry_collection_new', Gtk.Entry())
        self.entry.connect('changed', self.on_entry_changed)
        self.entry.connect('activate', self.update)
        delete = self.srvuif.create_button('basico-delete', 24, 24, '')
        delete.connect('clicked', self.delete)
        hbox.pack_start(self.entry, True, True, 6)
        hbox.pack_start(delete, False, False, 0)
        self.pack_start(hbox, False, False, 0)

        # Collection Treeview
        scr = Gtk.ScrolledWindow()
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        viewport = Gtk.Viewport()
        self.treeview = self.setup_treeview()
        viewport.add(self.treeview)
        scr.add(viewport)
        self.pack_start(scr, True, True, 6)

        if self.sid != '0000000000':
            # Footer
            separator = Gtk.Separator()
            self.pack_start(separator, False, False, 0)

            ## Buttons
            footer = Gtk.HBox()
            accept = self.srvuif.create_button('basico-check-ok', 24, 24, '<b>Apply changes</b>')
            accept.connect('clicked', self.accept)
            footer.pack_start(accept, True, False, 0)
            self.pack_start(footer, False, False, 3)


    def setup_treeview(self):
        """
        Missing method docstring (missing-docstring)
        """
        # Setup model
        treeview = Gtk.TreeView()
        self.model = Gtk.ListStore(
            str,        # key
            int,        # checkbox
            str,        # title
        )

        # Setup columns
        # Collection key
        self.renderer_key = Gtk.CellRendererText()
        self.column_key = Gtk.TreeViewColumn('Key', self.renderer_key, text=0)
        self.column_key.set_visible(False)
        self.column_key.set_expand(False)
        self.column_key.set_clickable(False)
        self.column_key.set_sort_indicator(False)
        treeview.append_column(self.column_key)

        # Collection Checkbox
        self.renderer_checkbox = Gtk.CellRendererToggle()
        self.renderer_checkbox.connect("toggled", self.toggle_checkbox)
        self.column_checkbox = Gtk.TreeViewColumn('Selected', self.renderer_checkbox, active=1)
        self.column_checkbox.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        if self.sid == '0000000000':
            self.column_checkbox.set_visible(False)
        else:
            self.column_checkbox.set_visible(True)
        self.column_checkbox.set_expand(False)
        self.column_checkbox.set_clickable(True)
        self.column_checkbox.set_sort_indicator(False)
        treeview.append_column(self.column_checkbox)

        # Collection title
        self.renderer_title = Gtk.CellRendererText()
        self.renderer_title.connect('edited', self.edit_title)
        self.renderer_title.set_property("editable", True)
        self.column_title = Gtk.TreeViewColumn('Collection', self.renderer_title, markup=2)
        self.column_title.set_visible(True)
        self.column_title.set_expand(True)
        self.column_title.set_clickable(True)
        self.column_title.set_sort_indicator(True)
        self.model.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        treeview.append_column(self.column_title)

        # TreeView common
        self.sorted_model = Gtk.TreeModelSort(model=self.model)
        self.sorted_model.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        treeview.set_model(self.sorted_model)

        treeview.set_can_focus(False)
        treeview.set_headers_visible(True)
        treeview.set_enable_search(True)
        treeview.set_hover_selection(False)
        treeview.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        # ~ self.treeview.modify_font(Pango.FontDescription('Monospace 10'))

        # Selection
        self.selection = treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.trv_signal_changed = self.selection.connect('changed', self.row_changed)

        # Filter
        # ~ self.visible_filter = self.model.filter_new()
        # ~ self.visible_filter.set_visible_func(self.visible_function)
        # ~ treeview.set_model(self.visible_filter)

        treeview.set_model(self.sorted_model)

        self.show_all()

        return treeview


    def toggle_checkbox(self, cell, path):
        """
        Missing method docstring (missing-docstring)
        """
        self.model[path][1] = not self.model[path][1]


    def accept(self, button):
        """
        Missing method docstring (missing-docstring)
        """
        selected = []

        def get_linked_collections(model, path, itr):
            """
            Missing method docstring (missing-docstring)
            """
            cid = model.get(itr, 0)[0]
            if cid != COL_DOWNLOADED:
                linked = model.get(itr, 1)[0]
                if linked:
                    selected.append(cid)
                    self.log.debug("Collection to be linked: %s (%s)", self.srvclt.get_name_by_cid(cid), cid)

        self.model.foreach(get_linked_collections)
        
        if len(selected) == 0:
            selected.append(COL_DOWNLOADED)

        try:
            int(self.sid)
            self.srvdtb.set_collections(self.sid, selected, self.overwrite)
            self.srvuif.statusbar_msg("Selected collection linked to SAP Note %s" % str(int(self.sid)), True)
        except:
            visor = self.srvgui.get_widget('visor_sapnotes')
            bag = visor.get_filtered_bag()
            for sid in bag:
                self.srvdtb.set_collections(sid, selected, self.overwrite)
            self.srvuif.statusbar_msg("Selected collections linked to all SAP Note in this view", True)
                
        visor = self.srvgui.get_widget('visor_sapnotes')
        visor.populate_sapnotes()
        viewmenu = self.srvgui.get_widget('viewmenu')
        viewmenu.populate()
        viewmenu.grab_focus()
        


    def row_changed(self, selection):
        """
        Missing method docstring (missing-docstring)
        """
        model, treeiter = selection.get_selected() #_rows()

        try:
            self.current_cid = model[treeiter][0]
            title = model[treeiter][2]
            self.entry.set_text(title)
        except TypeError:
            pass
        except Exception as error:
            self.log.error("ERROR: collections->row_changed->error: %s" % error)
            raise


    def update(self, entry=None):
        """
        Missing method docstring (missing-docstring)
        """
        linked = self.srvdtb.get_collections(self.sid)

        if entry is not None and isinstance(entry, Gtk.Entry):
            name = entry.get_text()
            res, msg = self.srvclt.create(name)            
            self.srvuif.statusbar_msg(msg, True)
            
        self.model.clear()
        collections = self.srvclt.get_all()
        if len(collections) > 0:
            for cid in collections:
                name = collections[cid]
                if cid in linked:
                    self.model.append([cid, 1, name])
                else:
                    self.model.append([cid, 0, name])
            self.current_cid = None

        self.srvuif.statusbar_msg("Collections updated")
        

    def delete(self, button):
        """
        Missing method docstring (missing-docstring)
        """
        name = self.srvclt.get_name_by_cid(self.current_cid)

        deleted = self.srvclt.delete(self.current_cid)
        if deleted:
            self.update()
            viewmenu = self.srvgui.get_widget('viewmenu')
            viewmenu.populate()
            msg = "Collection '%s' deleted" % name
            self.log.info(msg)
            self.srvuif.statusbar_msg(msg, True)
        else:
            if self.current_cid is not None:
                title = "Collection '%s' not deleted" % name
                message = "Make sure there are not SAP Notes linked to this collection"
                self.srvuif.dialog_info(title, message)


    def filter(self, *args):
        """
        Missing method docstring (missing-docstring)
        """
        self.visible_filter.refilter()


    def visible_function(self, model, itr, data):
        """
        Missing method docstring (missing-docstring)
        """
        entry = self.srvgui.get_widget('gtk_entry_collection_new')
        text = entry.get_text()
        title = model.get(itr, 2)[0]
        match = text.upper() in title.upper()
        return match


    def on_entry_changed(self, *args):
        entry = self.srvgui.get_widget('gtk_entry_collection_new')
        filter = entry.get_text()
        selection = self.treeview.get_selection()


        def gui_iterate_over_data(model, path, itr):
            title = self.sorted_model.get(itr, 2)[0]
            if len(filter) > 0:
                if filter.upper() in title.upper():
                    self.treeview.scroll_to_cell(path, self.column_title, True, 0.0, 0.0)
                    self.treeview.set_cursor_on_cell(path, self.column_title, self.renderer_title, False)
                else:
                    return

        GObject.signal_handler_block(self.selection, self.trv_signal_changed)
        self.sorted_model.foreach(gui_iterate_over_data)
        GObject.signal_handler_unblock(self.selection, self.trv_signal_changed)


    def edit_title(self, widget, path, target):
        model = self.treeview.get_model()
        treeiter = model.get_iter(path)
        cid = model[treeiter][0]
        if cid == COL_DOWNLOADED:
            self.srvuif.statusbar_msg("You can't rename this collection")
            return
            
        name_old = self.srvclt.get_name_by_cid(cid)
        iter_has_child = model.iter_has_child(treeiter)

        if not iter_has_child:
            if len(target) > 0:
                self.srvclt.rename(cid, target)
                self.update()
                msg = "Collection '%s' renamed to '%s'" % (name_old, target)
                self.log.info(msg)
                self.srvuif.statusbar_msg(msg)
