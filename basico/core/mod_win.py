#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_win.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Gtk.ApplicationWindow implementation
"""

import os
import sys
import stat
import time
import platform

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from basico.core.mod_srv import Service
from basico.core.mod_env import APP, FILE, ATYPES
from basico.widgets.wdg_menuview import MenuView
from basico.widgets.wdg_visor_sapnotes import SAPNotesVisor
from basico.widgets.wdg_visor_annotations import AnnotationsVisor
from basico.widgets.wdg_visor_toolbar import VisorToolbar
from basico.widgets.wdg_about import About
from basico.widgets.wdg_settingsview import SettingsView
from basico.widgets.wdg_logviewer import LogViewer
from basico.widgets.wdg_annot import AnnotationWidget
from basico.widgets.wdg_statusbar import Statusbar
from basico.core.mod_log import get_logger


class GtkAppWindow(Gtk.ApplicationWindow, Service):
    def __init__(self, uiapp):
        self.setup_controller(uiapp)
        self.get_logger(__class__.__name__)
        self.get_services()
        self.srvgui.add_widget('uiapp', uiapp)
        self.app = self.srvgui.get_app()
        self.setup_window(uiapp)
        self.setup_widgets()
        self.run()


    def get_services(self):
        self.srvbnr = self.controller.get_service("BNR")
        self.srvgui = self.controller.get_service("GUI")
        self.srvdtb = self.controller.get_service("DB")
        self.srvuif = self.controller.get_service("UIF")
        self.srvicm = self.controller.get_service('IM')
        self.srvclb = self.controller.get_service('Callbacks')
        self.srvant = self.controller.get_service('Annotation')


    def setup_controller(self, uiapp):
        self.controller = uiapp.get_controller()


    def setup_window(self, uiapp):
        Gtk.Window.__init__(self, title=APP['name'], application=uiapp)
        icon = self.srvicm.get_icon('basico-component', 48, 48)
        self.set_icon(icon)
        # FIXME
        # From docs: Don’t use this function. It sets the X xlib.Window
        # System “class” and “name” hints for a window.
        # But I have to do it or it doesn't shows the right title. ???
        self.set_wmclass (APP['name'], APP['name'])
        self.set_role(APP['name'])
        self.set_default_size(1024, 728)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.maximize ()
        self.setup_headerbar()
        self.show_all()


    def setup_headerbar(self):
        hb = self.srvgui.add_widget('gtk_headerbar_container', Gtk.HeaderBar())
        hb.set_show_close_button(True)
        hb.props.title = "Basico"
        hb.props.subtitle = "SAP Notes Manager for SAP Consultants"
        lhbox = self.setup_headerbar_left(hb)
        hb.pack_start(lhbox)
        rhbox = self.setup_headerbar_right(hb)

        hb.pack_end(rhbox)
        self.set_titlebar(hb)
        hb.show_all()


    def setup_headerbar_left(self, hb):
        # ~ '''Left headerbar side not used by now'''
        lhbox = Gtk.HBox()

        ### Dashboard / Visor
        hbox = Gtk.HBox()
        icon = self.srvicm.get_pixbuf_icon('basico-dashboard', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label()
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = self.srvgui.add_widget('gtk_button_dashboard', Gtk.Button())
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        lhbox.pack_start(button, False, False, 0)
        button.connect('clicked', self.srvclb.gui_show_dashboard)

        return lhbox


    def setup_headerbar_right(self, hb):
        rhbox = Gtk.HBox()

        ## Help togglebutton
        # ~ if self.srvuif.webkit_support():
            # ~ button = self.srvgui.add_widget('gtk_togglebutton_help', Gtk.ToggleButton())
            # ~ icon = self.srvicm.get_pixbuf_icon('basico-help', 24, 24)
            # ~ image = Gtk.Image()
            # ~ image.set_from_pixbuf(icon)
            # ~ button.set_image(image)
            # ~ button.set_relief(Gtk.ReliefStyle.NONE)
            # ~ button.connect('toggled', self.srvclb.gui_toggle_help_visor)
        # ~ else:
            # ~ button = self.srvgui.add_widget('gtk_button_help', Gtk.Button())
            # ~ icon = self.srvicm.get_pixbuf_icon('basico-help', 24, 24)
            # ~ image = Gtk.Image()
            # ~ image.set_from_pixbuf(icon)
            # ~ button.set_image(image)
            # ~ button.set_relief(Gtk.ReliefStyle.NONE)
            # ~ button.connect('clicked', self.srvclb.gui_lauch_help_visor)

        # ~ rhbox.pack_end(button, False, False, 0)

        ## System Menu
        button = Gtk.Button()
        icon = self.srvicm.get_pixbuf_icon('basico-menu-system', 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NONE)
        popover = Gtk.Popover.new(button)
        self.srvgui.add_widget('gtk_popover_button_menu_system', popover)
        button.connect('clicked', self.srvclb.gui_show_popover, popover)
        rhbox.pack_end(button, False, False, 0)

        # Popover body
        box = Gtk.Box(spacing = 0, orientation="vertical")
        popover.add(box)

        ### About
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-about', 48, 48)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("About")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('clicked', self.srvclb.gui_show_about)
        box.pack_end(button, False, False, 0)

        # ~ ### Help
        # ~ hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        # ~ icon = self.srvicm.get_pixbuf_icon('basico-help', 48, 48)
        # ~ image = Gtk.Image()
        # ~ image.set_from_pixbuf(icon)
        # ~ label = Gtk.Label("Help")
        # ~ hbox.pack_start(image, False, False, 3)
        # ~ hbox.pack_start(label, False, False, 3)
        # ~ button = Gtk.Button()
        # ~ button.add(hbox)
        # ~ button.set_relief(Gtk.ReliefStyle.NONE)
        # ~ button.connect('clicked', self.srvclb.gui_show_help)
        # ~ box.pack_end(button, False, False, 0)

        ### Log viewer
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-logviewer', 48, 48)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("Event viewer")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('clicked', self.srvclb.gui_show_log)
        box.pack_end(button, False, False, 0)

        ### Settings
        # ~ hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        # ~ icon = self.srvicm.get_pixbuf_icon('basico-settings', 48, 48)
        # ~ image = Gtk.Image()
        # ~ image.set_from_pixbuf(icon)
        # ~ label = Gtk.Label("Settings")
        # ~ hbox.pack_start(image, False, False, 3)
        # ~ hbox.pack_start(label, False, False, 3)
        # ~ button = Gtk.Button()
        # ~ button.add(hbox)
        # ~ button.set_relief(Gtk.ReliefStyle.NONE)
        # ~ button.connect('clicked', self.srvclb.gui_show_settings)
        # ~ box.pack_start(button, False, False, 0)

        ### Backup
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-backup-restore', 48, 48)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("Backup/Restore")
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        box.pack_start(button, False, False, 0)

        box_bnr = Gtk.VBox()
        popover_bnr = Gtk.Popover.new(button)
        popover_bnr.set_position(Gtk.PositionType.LEFT)
        popover_bnr.add(box_bnr)
        self.srvgui.add_widget('gtk_popover_button_menu_system', popover_bnr)
        button.connect('clicked', self.srvclb.gui_show_popover, popover_bnr)

        hbox_backup = Gtk.VBox()
        button_backup = self.srvuif.create_button('basico-backup', 48, 48, '<b>Backup database</b> ')
        button_backup.connect('clicked', self.srvclb.gui_database_backup)
        box_bnr.pack_start(button_backup, False, False, 0)
        button_restore = self.srvuif.create_button('basico-restore', 48, 48, '<b>Restore from backup</b>')
        button_restore.connect('clicked', self.srvclb.gui_database_restore)
        # ~ button_cache = self.srvuif.create_button('basico-restore', 48, 48, '<b>Restore from cache</b>')
        # ~ button_cache.connect('clicked', self.srvbnr.restore_from_cache)
        
        box_bnr.pack_start(button_restore, False, False, 0)
        # ~ box_bnr.pack_start(button_cache, False, False, 0)

        return rhbox


    def setup_widgets(self):
        # Mainbox
        mainbox = self.srvgui.add_widget('gtk_vbox_container_main', Gtk.VBox())
        mainbox.set_hexpand(True)
        paned = self.srvgui.add_widget('gtk_hpaned', Gtk.HPaned())
        paned.set_property('margin-bottom', 6)
        paned.set_wide_handle(False)
        paned.set_position(300)

        # (Build first menuview)
        notebook_menuview = self.srvgui.add_widget('gtk_notebook_menuview', Gtk.Notebook())
        notebook_menuview.set_show_border(False)
        notebook_menuview.set_show_tabs(False)
        notebook_menuview.set_hexpand(True)

        menuview_sapnotes_page = self.setup_tab_menuview_sapnotes()
        menuview_sapnotes_page.set_hexpand(True)
        tab_widget = self.srvuif.create_notebook_tab_label('basico-sapnote', '<b>SAP Notes</b>')
        notebook_menuview.append_page(menuview_sapnotes_page, tab_widget)

        menuview_annotation_page = self.setup_tab_menuview_annotations()
        menuview_annotation_page.set_hexpand(True)
        tab_widget = self.srvuif.create_notebook_tab_label('basico-annotation', '<b>Annotations</b>')
        notebook_menuview.append_page(menuview_annotation_page, tab_widget)


        # Paned
        ## Right pane
        box = Gtk.VBox()
        box.set_hexpand(True)
        stack_main = self.srvgui.add_widget('gtk_stack_main', Gtk.Stack())
        stack_main.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack_main.set_transition_duration(250)
        box.pack_start(stack_main, True, True, 0)

        ### Visor stack
        stack_child = self.setup_stack_visor()
        stack_main.add_titled(stack_child, "visor", "SAP Notes Visor")

        ### About stack
        stack_child = self.setup_stack_about()
        stack_main.add_titled(stack_child, "about", "About Basico")

        ### Log stack
        stack_child = self.setup_stack_log()
        stack_main.add_titled(stack_child, "log", "Event Viewer")

        ### Settings stack
        stack_child = self.setup_stack_settings()
        stack_main.add_titled(stack_child, "settings", "Basico Settings")

        ## left pane
        paned.add1(notebook_menuview)
        notebook_menuview.show_all()

        ## Annotations
        boxannotations = self.srvgui.add_widget('gtk_vbox_container_annotations', Gtk.VBox())

        stack_annot = self.srvgui.add_widget('gtk_stack_annotation', Gtk.Stack())
        stack_annot.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack_annot.set_transition_duration(2500)

        stack_child = self.setup_stack_annotation()
        stack_annot.add_titled(stack_child, "comment", "New comment")
        stack_annot.child_set_property (stack_child, "icon-name", "basico-comments")

        self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
        boxannotations.add(stack_annot)


        box.pack_start(boxannotations, True, True, 6)
        paned.add2(box)
        mainbox.pack_start(paned, True, True, 0)

        # Statusbar
        statusbar = self.srvgui.add_widget('widget_statusbar', Statusbar(self.controller))
        mainbox.pack_start(statusbar, False, False, 0)

        # Menu Views
        vbox = Gtk.VBox()
        viewsbox = self.srvgui.get_widget('gtk_box_container_views')
        viewmenu = self.srvgui.add_widget('viewmenu', MenuView(self.controller))
        viewmenu.set_hexpand(True)
        viewmenu.set_vexpand(True)
        vbox.pack_start(viewmenu, True, True, 0)
        self.srvgui.swap_widget(viewsbox, vbox)

        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_annotations.connect_menuview_signals()
        visor_annotations.set_active_categories()
        self.add(mainbox)
        self.show_all()


    def setup_stack_visor(self):
        box = Gtk.VBox()
        box.set_hexpand(True)

        ### Toolbar
        boxtoolbar = self.srvgui.add_widget('gtk_hbox_container_toolbar', Gtk.HBox())
        box.pack_start(boxtoolbar, False, False, 0)
        visortoolbar = self.srvgui.add_widget('visortoolbar', VisorToolbar(self.controller))
        self.srvgui.swap_widget(boxtoolbar, visortoolbar)

        ### Visor
        notebook = self.srvgui.add_widget('gtk_notebook_visor', Gtk.Notebook())
        notebook.connect('switch-page', self.srvclb.gui_visor_switch_page)
        notebook.set_show_border(False)
        notebook.set_hexpand(True)

        visor_sapnotes_page = self.setup_tab_sapnote_visor()
        visor_sapnotes_page.set_hexpand(True)
        tab_widget = self.srvuif.create_notebook_tab_label('basico-sapnote', '<b>SAP Notes</b>')
        notebook.append_page(visor_sapnotes_page, tab_widget)

        visor_annotations_page = self.setup_tab_annotations_visor()
        visor_annotations_page.set_hexpand(True)
        tab_widget = self.srvuif.create_notebook_tab_label('basico-annotation', '<b>Annotations</b>')
        notebook.append_page(visor_annotations_page, tab_widget)

        # ~ if self.srvuif.webkit_support():
            # ~ visor_help_page = self.srvgui.add_widget('gtk_notebook_help_page', self.setup_tab_help_visor())
            # ~ visor_help_page.set_hexpand(True)
            # ~ tab_widget = self.srvuif.create_notebook_tab_label('basico-help', '<b>Help</b>')
            # ~ notebook.append_page(visor_help_page, tab_widget)
            # ~ self.srvuif.set_widget_visibility('gtk_notebook_help_page', False)
            # ~ notebook.child_set_property(visor_help_page, "tab-expand", True)
            # ~ notebook.child_set_property(visor_help_page, "tab-fill", False)


        notebook.child_set_property(visor_sapnotes_page, "tab-expand", True)
        notebook.child_set_property(visor_sapnotes_page, "tab-fill", False)
        notebook.child_set_property(visor_annotations_page, "tab-expand", True)
        notebook.child_set_property(visor_annotations_page, "tab-fill", False)


        box.pack_start(notebook, True, True, 0)

        return box

    # ~ def setup_tab_help_visor(self):
        # ~ from basico.widgets.wdg_browser import BasicoBrowser
        # ~ box = Gtk.VBox()
        # ~ box.set_hexpand(True)

        # ~ ### Help Visor
        # ~ browser = BasicoBrowser()
        # ~ self.controller.debug(FILE['HELP_INDEX'])
        # ~ browser.load_url("file://%s" % FILE['HELP_INDEX'])
        # ~ box.pack_start(browser, True, True, 0)
        # ~ box.show_all()
        # ~ return box


    def setup_tab_sapnote_visor(self):
        box = Gtk.VBox()
        box.set_hexpand(True)

        ### Visor
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        visor = self.srvgui.add_widget('visor_sapnotes', SAPNotesVisor(self.controller))
        visor.set_hexpand(True)
        visor.set_vexpand(True)
        vwp.add(visor)
        scr.add(vwp)
        box.pack_start(scr, True, True, 0)
        visor.show_all()
        box.show_all()
        return box


    def setup_tab_annotations_visor(self):
        box = Gtk.VBox()
        box.set_hexpand(True)

        ### Visor
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        visor = self.srvgui.add_widget('visor_annotations', AnnotationsVisor(self.controller))
        visor.set_hexpand(True)
        visor.set_vexpand(True)
        vwp.add(visor)
        scr.add(vwp)
        box.pack_start(scr, True, True, 0)
        visor.show_all()
        box.show_all()
        return box


    def setup_tab_menuview_sapnotes(self):
        ## Left view - SAP Notes Menu view
        box = self.srvgui.add_widget('gtk_vbox_container_menu_view', Gtk.VBox())
        box.set_property('margin-left', 0)
        box.set_property('margin-right', 0)
        box.set_property('margin-bottom', 0)

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
        menuviews.connect('clicked', self.srvclb.gui_show_popover, popover)
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
        completion = self.srvgui.get_widget('gtk_entrycompletion_viewmenu')
        viewfilter.set_completion(completion)
        viewfilter.connect('activate', self.srvclb.gui_viewmenu_filter)

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
            if icon_pos == Gtk.EntryIconPosition.PRIMARY:
                viewmenu = self.srvgui.get_widget('viewmenu')
                viewmenu.refresh()
            elif icon_pos == Gtk.EntryIconPosition.SECONDARY:
                self.srvclb.expand_menuview()

        viewfilter.connect("icon-press", on_icon_pressed)

        hbox.pack_start(viewfilter, True, True, 0)
        tool.add(hbox)
        tool.set_expand(True)
        toolbar.insert(tool, -1)

        box.pack_start(toolbar, False, False, 0)

        ### View treeview
        box_trv = Gtk.VBox()
        box_trv.set_property('margin-left', 3)
        box_trv.set_property('margin-right', 3)
        box_trv.set_property('margin-bottom', 0)
        scr = Gtk.ScrolledWindow()
        scr.set_hexpand(True)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        vwp = Gtk.Viewport()
        vwp.set_hexpand(True)
        viewsbox = self.srvgui.add_widget('gtk_box_container_views', Gtk.Box())
        viewsbox.set_hexpand(True)
        vwp.add(viewsbox)
        scr.add(vwp)
        box_trv.pack_start(scr, True, True, 0)

        box.pack_start(box_trv, True, True, 0)

        return box


    def setup_tab_menuview_annotations(self):
        vbox_main = Gtk.VBox()
        vbox_main.set_hexpand(False)
        vbox_main.set_property('margin-top', 6)
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

        # Categories
        button = self.srvgui.add_widget('gtk_togglebutton_categories', Gtk.ToggleButton())
        button.set_relief(Gtk.ReliefStyle.NONE)
        icon = self.srvicm.get_image_icon('basico-category', 48, 48)
        label = Gtk.Label('')
        label.set_markup('<big><b>Categories</b></big>')
        hbox_cat = Gtk.HBox()
        hbox_cat.set_hexpand(True)
        hbox_cat.pack_start(icon, False, False, 3)
        hbox_cat.pack_start(label, False, False, 3)
        button.add(hbox_cat)
        vbox_main.pack_start(button, False, False, 0)

        revealer = self.srvgui.add_widget('gtk_revealer_annotations_categories', Gtk.Revealer())
        vbox_revealer = Gtk.VBox()
        vbox_revealer.set_hexpand(False)

        for name in ['inbox', 'drafts', 'archived']:
            button = create_panel_elem_button('basico-%s' % name.lower(), name)
            self.srvgui.add_widget('gtk_button_category_%s' % name, button)
            vbox_revealer.pack_start(button, False, False, 2)

        revealer.add(vbox_revealer)
        vbox_main.pack_start(revealer, False, False, 6)

        separator = Gtk.Separator()
        vbox_main.pack_start(separator, False, False, 6)
        
        # Types
        button = self.srvgui.add_widget('gtk_togglebutton_types', Gtk.ToggleButton())
        button.set_relief(Gtk.ReliefStyle.NONE)
        icon = self.srvicm.get_image_icon('basico-type', 48, 48)
        label = Gtk.Label('')
        label.set_markup('<big><b>Types</b></big>')
        hbox_type = Gtk.HBox()



        hbox_type.pack_start(icon, False, False, 3)
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
        switch.connect('state-set', self.srvclb.gui_switch_selection_atypes)
        label = self.srvgui.add_widget('gtk_label_switch_select_atypes', Gtk.Label("All selected"))
        hbox_sel.pack_start(label, True, True, 0)
        hbox_sel.pack_start(switch, False, False, 6)
        vbox_revealer.pack_start(hbox_sel, False, False, 6)

        for name in ATYPES:
            button = create_panel_elem_button('basico-annotation-type-%s' % name.lower(), name.lower())
            self.srvgui.add_widget('gtk_button_type_%s' % name.lower(), button)
            button.set_active(True)
            vbox_revealer.pack_start(button, False, False, 2)

        revealer.add(vbox_revealer)
        vbox_main.pack_start(revealer, False, False, 6)

        return vbox_main


    def setup_stack_about(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        about = self.srvgui.add_widget('widget_about', About(self.controller))
        box.pack_start(about, True, True, 0)
        box.show_all()
        return box


    def setup_stack_settings(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        settings = self.srvgui.add_widget('widget_settings', SettingsView(self.controller))
        box.pack_start(settings, True, True, 0)
        box.show_all()
        return box


    def setup_stack_log(self):
        box = Gtk.VBox()
        box.set_hexpand(True)
        logviewer = self.srvgui.add_widget('widget_logviewer', LogViewer(self.controller))
        box.pack_start(logviewer, True, True, 0)
        box.show_all()
        return box


    def setup_stack_annotation(self):
        return self.srvgui.add_widget('widget_annotation', AnnotationWidget(self.controller))


    def run(self):
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        viewmenu = self.srvgui.get_widget('viewmenu')
        viewmenu.set_view('collection')
        self.srvclb.gui_show_visor_annotations()
        annotations = self.srvant.search_term('')
        visor_annotations.populate_annotations(annotations)
        self.srvclb.gui_viewmenu_select_first_entry()
