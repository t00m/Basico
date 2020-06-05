#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_annot.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Annotation Widget
"""

import os
import html
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GtkSource
from basico.core.mod_env import LPATH, ATYPES, FILE
from basico.core.mod_wdg import BasicoWidget
from basico.widgets.wdg_browser import BasicoBrowser


class AnnotationToolbar(BasicoWidget, Gtk.HBox):
    def __init__(self, app, sid='0000000000'):
        super().__init__(app, __class__.__name__)
        Gtk.Box.__init__(self)
        self.sid = sid
        self.get_services()
        self.set_homogeneous(False)
        self.setup()


    def setup(self):
        # Toolbar
        self.toolbar = Gtk.Toolbar()
        self.pack_start(self.toolbar, False, True, 0)
        self.toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.toolbar.set_property('margin-bottom', 0)

        # Annotation icon
        tool = self.srvgui.add_widget('gtk_tool_annotation_icon', Gtk.ToolItem())
        box = self.srvgui.add_widget('gtk_box_annotation_icon', Gtk.Box())
        tool.add(box)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, False)
        self.toolbar.insert(tool, -1)

        # Title
        tool = Gtk.ToolItem()
        # ~ vbox = Gtk.VBox()
        title = self.srvgui.add_widget('gtk_label_annotation_sid', Gtk.Label())
        title.set_selectable(True)
        if self.sid == '0000000000':
            title.set_markup('<small><b>Annotation</b></small>')
        else:
            title.set_markup('<small><b>Annotation for SAP Note %s</b></small>' % str(int(self.sid)))
        title.set_xalign(0.5)
        tool.add(title)
        self.toolbar.insert(tool, -1)

        # Task Category button
        tool = Gtk.ToolItem()
        a_category_model = Gtk.ListStore(Pixbuf, str)
        a_category = Gtk.ComboBox.new_with_model(a_category_model)
        a_category.set_tooltip_markup('<b>Choose a category</b>')
        self.srvgui.add_widget('gtk_combobox_annotation_category', a_category)

        renderer = Gtk.CellRendererPixbuf()
        a_category.pack_start(renderer, False)
        a_category.add_attribute(renderer, "pixbuf", 0)
        renderer = Gtk.CellRendererText()
        a_category.pack_start(renderer, True)
        a_category.add_attribute(renderer, "text", 1)

        icon = self.srvicm.get_pixbuf_icon('basico-inbox', 18, 18)
        active = self.srvgui.add_widget('annotation_category_Inbox', a_category_model.append([icon, 'Inbox']))

        icon = self.srvicm.get_pixbuf_icon('basico-drafts', 18, 18)
        self.srvgui.add_widget('annotation_category_Drafts', a_category_model.append([icon, 'Drafts']))

        icon = self.srvicm.get_pixbuf_icon('basico-archived', 18, 18)
        self.srvgui.add_widget('annotation_category_Archived', a_category_model.append([icon, 'Archived']))

        a_category.set_active_iter(active)
        hbox = Gtk.HBox()
        hbox.pack_start(a_category, False, False, 0)
        tool.add(hbox)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, False)
        self.toolbar.insert(tool, -1)

        # Annotation Type button
        tool = Gtk.ToolItem()
        a_type_model = Gtk.ListStore(Pixbuf, str)
        a_type = Gtk.ComboBox.new_with_model(a_type_model)
        a_type.set_tooltip_markup('<b>Choose a type</b>')
        self.srvgui.add_widget('gtk_combobox_annotation_type', a_type)
        renderer = Gtk.CellRendererPixbuf()
        a_type.pack_start(renderer, False)
        a_type.add_attribute(renderer, "pixbuf", 0)
        renderer = Gtk.CellRendererText()
        a_type.pack_start(renderer, True)
        a_type.add_attribute(renderer, "text", 1)
        for item in ATYPES:
            icon = self.srvicm.get_pixbuf_icon('basico-annotation-type-%s' % item.lower(), 18, 18)
            active = self.srvgui.add_widget('annotation_type_%s' % item.title(), a_type_model.append([icon, '%s' % item.title()]))
        a_type.set_active_iter(active)
        hbox = Gtk.HBox()
        hbox.pack_start(a_type, False, False, 0)
        tool.add(hbox)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, False)
        self.toolbar.insert(tool, -1)

        # Task Priority button
        tool = Gtk.ToolItem()
        a_priority_model = Gtk.ListStore(Pixbuf, str)
        a_priority = Gtk.ComboBox.new_with_model(a_priority_model)
        a_priority.set_tooltip_markup('<b>Choose a priority</b>')
        self.srvgui.add_widget('gtk_combobox_annotation_priority', a_priority)

        renderer = Gtk.CellRendererPixbuf()
        a_priority.pack_start(renderer, False)
        a_priority.add_attribute(renderer, "pixbuf", 0)

        renderer = Gtk.CellRendererText()
        a_priority.pack_start(renderer, True)
        a_priority.add_attribute(renderer, "text", 1)

        icon = self.srvicm.get_pixbuf_icon('basico-annotation-priority-high', 18, 18)
        self.srvgui.add_widget('annotation_priority_High', a_priority_model.append([icon, 'High']))

        icon = self.srvicm.get_pixbuf_icon('basico-annotation-priority-normal', 18, 18)
        active = self.srvgui.add_widget('annotation_priority_Normal', a_priority_model.append([icon, 'Normal']))

        icon = self.srvicm.get_pixbuf_icon('basico-annotation-priority-low', 18, 18)
        self.srvgui.add_widget('annotation_priority_Low', a_priority_model.append([icon, 'Low']))

        a_priority.set_active_iter(active)
        hbox = Gtk.HBox()
        hbox.pack_start(a_priority, False, False, 0)
        tool.add(hbox)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, False)
        self.toolbar.insert(tool, -1)

        # Is template?
        hbox = Gtk.HBox()
        tool = Gtk.ToolItem()
        icon = self.srvicm.get_new_image_icon('basico-annotation-type-template', 18, 18)
        switch = self.srvgui.add_widget('gtk_switch_annotation_template', Gtk.ToggleButton())
        switch.set_tooltip_markup('<b>Toggle to mark this annotation as a template</b>')
        # ~ switch.connect('state-set', callback)
        label = Gtk.Label()
        label.set_markup('<b>Template?</b>')
        hbox.pack_start(icon, False, False, 3)
        # ~ hbox.pack_start(label, False, False, 3)
        switch.add(hbox)
        tool.add(switch)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, False)
        self.toolbar.insert(tool, -1)

        # Attachment button
        tool = self.srvgui.add_widget('gtk_button_annotation_toolbar_attachment', Gtk.ToolButton())
        tool.set_tooltip_markup('<b>Attach file(s) to this annotation</b>')
        tool.set_icon_name('basico-attachment')
        # ~ popover = self.srvgui.add_widget('gtk_button_annotation_toolbar_attachment', Gtk.Popover.new(tool))
        tool.connect('clicked', self.srvclb.gui_attachment_add_to_annotation)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, True)
        self.toolbar.insert(tool, -1)

        # Timestamp created
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        a_wdg_timestamp_created = self.srvgui.add_widget('gtk_label_timestamp_created', Gtk.Label())
        a_wdg_timestamp_created.modify_font(Pango.FontDescription('Monospace 10'))
        a_wdg_timestamp_created.set_xalign(0.5)
        tool.add(a_wdg_timestamp_created)
        tool.set_no_show_all(True)
        tool.hide()
        self.toolbar.insert(tool, -1)

        # Timestamp updated
        tool = Gtk.ToolItem()
        tool.set_expand(False)
        a_wdg_human_timestamp = self.srvgui.add_widget('gtk_label_human_timestamp', Gtk.Label())
        a_wdg_human_timestamp.modify_font(Pango.FontDescription('Monospace 10'))
        a_wdg_human_timestamp.set_xalign(0.5)
        tool.add(a_wdg_human_timestamp)
        tool.set_no_show_all(True)
        tool.hide()
        self.toolbar.insert(tool, -1)

        # Annotation Stack Switcher
        tool = Gtk.ToolItem()
        tool.set_is_important(True)
        tool.set_visible_vertical(True)
        tool.set_visible_horizontal(True)
        stack_switcher = self.srvgui.add_widget('stack_switcher_annotation', Gtk.StackSwitcher())
        stack_switcher.set_property('icon-size', 3)
        stack = self.srvgui.add_widget('stack_annotation', Gtk.Stack())
        stack_switcher.set_stack(stack)
        tool.add(stack_switcher)
        self.toolbar.insert(tool, -1)

        # Separator
        tool = self.srvuif.get_toolbar_separator(False, False)
        self.toolbar.insert(tool, -1)

        # Arrow UP
        tool = self.srvgui.add_widget('gtk_button_annotation_toolbar_previous_item', Gtk.ToolButton())
        # ~ icon = self.srvicm.get_new_image_icon('basico-arrow-up')
        # ~ tool.add(icon)
        # ~ tool.set_expand(False)
        # ~ tool.set_visible_horizontal(True)
        # ~ tool.set_visible_vertical(True)
        # ~ tool.set_is_important(True)
        tool.set_tooltip_markup('<b>Previous annotation</b>')
        tool.set_icon_name('basico-arrow-up')
        tool.connect('clicked', self.srvclb.gui_annotation_previous_row)
        self.toolbar.insert(tool, -1)

        # Arrow DOWN
        tool = self.srvgui.add_widget('gtk_button_annotation_toolbar_next_item', Gtk.ToolButton())
        # ~ icon = self.srvicm.get_new_image_icon('basico-arrow-down')
        # ~ tool.add(icon)
        # ~ tool.set_visible_vertical(True)
        # ~ tool.set_visible_horizontal(True)
        # ~ tool.set_is_important(True)
        # ~ tool.set_expand(False)
        tool.set_tooltip_markup('<b>Next annotation</b>')
        tool.set_icon_name('basico-arrow-down')
        tool.connect('clicked', self.srvclb.gui_annotation_next_row)
        self.toolbar.insert(tool, -1)

        # ~ # Separator
        # ~ tool = self.srvuif.get_toolbar_separator(False, False)
        # ~ self.toolbar.insert(tool, -1)

        # Toolbar initial settings
        self.set_visible(True)
        self.set_no_show_all(False)
        self.toolbar.set_hexpand(True)


    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvclb = self.get_service('Callbacks')
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvuif = self.get_service("UIF")
        self.srvclt = self.get_service('Collections')



class AnnotationWidget(BasicoWidget, Gtk.VBox):
    """
    Annotation Widget
    """
    def __init__(self, app, sid='0000000000'):
        super().__init__(app, __class__.__name__)
        Gtk.VBox.__init__(self)
        self.app = app
        self.sid = sid
        self.get_services()
        self.__setup()


    def get_services(self):
        """Load services to be used in this class
        """
        self.srvgui = self.get_service("GUI")
        self.srvicm = self.get_service("IM")
        self.srvuif = self.get_service("UIF")
        self.srvclt = self.get_service('Collections')
        self.srvclb = self.get_service('Callbacks')
        self.srvant = self.get_service('Annotation')
        self.srvutl = self.get_service('Utils')
        self.srvacd = self.get_service('Asciidoctor')


    def __setup(self):
        # Setup Widget properties
        self.set_property('margin-left', 3)
        self.set_property('margin-right', 3)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Annotation container (body)
        self.container_body = self.srvgui.add_widget('gtk_vbox_annotation_container', Gtk.VBox())
        self.container_body.set_border_width(3)
        self.pack_start(self.container_body, True, True, 3)

        self.__setup_header()
        self.__setup_body()
        self.__setup_footer()
        self.connect("key-press-event",self.on_key_press_event)


    def on_key_press_event(self, widget, event):
        if Gdk.keyval_name(event.keyval) == 'Escape':
            # ~ self.srvclb.action_annotation_cancel()
            pass

    def __setup_header(self):
        # Annotation Header
        container = self.srvgui.get_widget('gtk_vbox_annotation_container')
        header = Gtk.VBox()

        # Editor's toolbar
        toolbar = AnnotationToolbar(self.app, self.sid)
        header.pack_start(toolbar, False, False, 0)
        hbox = Gtk.HBox()
        a_lbl_aid = Gtk.Label()
        a_lbl_aid.set_property('xalign', 1.0)
        a_lbl_aid.modify_font(Pango.FontDescription('Monospace 10'))
        a_lbl_aid.set_markup('<b>Annotation Id:</b>')
        a_aid = self.srvgui.add_widget('gtk_label_aid', Gtk.Label())
        a_aid.set_property('xalign', 1.0)
        a_aid.set_selectable(True)
        a_aid.modify_font(Pango.FontDescription('Monospace 10'))
        separator = Gtk.Separator()
        hbox.pack_start(a_lbl_aid, False, False, 0)
        hbox.pack_start(a_aid, False, False, 0)
        hbox.set_no_show_all(True)
        hbox.hide()
        # ~ header.pack_start(hbox, False, False, 0)
        # ~ header.pack_start(a_wdg_human_timestamp, True, True, 0)
        # ~ header.pack_start(separator, False, False, 3)
        header.show_all()
        container.pack_start(header, False, False, 0)


    def __setup_body(self):
        stack_switcher = self.srvgui.get_widget('stack_switcher_annotation')
        stack_annotation = self.srvgui.get_widget('stack_annotation')
        stack_annotation.connect('notify::visible-child', self.stack_changed)
        self.container_body.add(stack_annotation)

        # Add Annotation preview stack
        preview = self.widget_annotation_preview()
        stack_annotation.add_titled(preview, "preview", "Preview annotation")
        stack_annotation.child_set_property (preview, "icon-name", "basico-preview")

        # Add Annotation editor stack
        editor = self.widget_annotation_editor()
        stack_annotation.add_titled(editor, "editor", "Edit annotation")
        stack_annotation.child_set_property (editor, "icon-name", "basico-drafts")

        # Add Annotation properties stack
        # ~ properties = self.annotation_properties()
        # ~ stack_annotation.add_titled(properties, "properties", "Edit properties")
        # ~ stack_annotation.child_set_property (properties, "icon-name", "basico-tags")



    def set_visible_stack(self, stack_name='editor'):
        self.srvuif.set_widget_visibility('stack_annotation', True)
        stack = self.srvgui.get_widget('stack_annotation')
        stack.set_visible_child_name(stack_name)
        if stack_name == 'preview':
            self.preview()
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_category', False)
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_type', False)
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_priority', False)
            self.srvuif.set_widget_visibility('gtk_button_annotation_toolbar_attachment', False)
            self.srvuif.set_widget_visibility('gtk_entry_annotation_scope', False)
            self.srvuif.set_widget_visibility('gtk_switch_annotation_template', False)
            self.srvuif.set_widget_visibility('annotation_footer_buttons', False)
            self.srvuif.set_widget_visibility('gtk_label_annotation_sid', True)
        elif stack_name == 'properties':
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_category', False)
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_type', False)
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_priority', False)
            self.srvuif.set_widget_visibility('gtk_button_annotation_toolbar_attachment', False)
            self.srvuif.set_widget_visibility('gtk_entry_annotation_scope', False)
            self.srvuif.set_widget_visibility('gtk_switch_annotation_template', False)
            self.srvuif.set_widget_visibility('annotation_footer_buttons', False)
            self.srvuif.set_widget_visibility('gtk_label_annotation_sid', False)
        elif stack_name == 'editor':
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_category', True)
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_type', True)
            self.srvuif.set_widget_visibility('gtk_combobox_annotation_priority', True)
            self.srvuif.set_widget_visibility('gtk_button_annotation_toolbar_attachment', True)
            self.srvuif.set_widget_visibility('gtk_entry_annotation_scope', True)
            self.srvuif.set_widget_visibility('gtk_switch_annotation_template', True)
            self.srvuif.set_widget_visibility('annotation_footer_buttons', True)
            self.srvuif.set_widget_visibility('gtk_label_annotation_sid', False)


    def widget_annotation_preview(self):
        browser = self.srvgui.add_widget('annotation_browser', BasicoBrowser(self.app))
        return browser


    def widget_annotation_properties(self):
        properties = self.srvgui.add_widget('annotation_properties', Gtk.Label('Properties'))
        return properties


    def widget_annotation_editor(self):
        vbox = Gtk.VBox()

        # Hidden metadata
        hhbox = Gtk.HBox()

        a_timestamp = self.srvgui.add_widget('gtk_label_timestamp', Gtk.Label(self.srvutl.timestamp()))
        a_timestamp.set_sensitive(False)
        self.srvuif.set_widget_visibility('gtk_label_timestamp', False)
        hhbox.pack_start(a_timestamp, False, False, 0)
        vbox.pack_start(hhbox, False, False, 0)


        # Main hbox
        mhbox = Gtk.HBox()

        vboxl = Gtk.VBox()
        vboxl.set_vexpand(True)
        vboxr = Gtk.VBox()
        vboxr.set_vexpand(True)

        # Title
        a_title = self.srvgui.add_widget('gtk_entry_annotation_title', Gtk.Entry())
        a_title.set_placeholder_text("Type a title here...")
        a_title.modify_font(Pango.FontDescription('Monospace 10'))
        vboxl.pack_start(a_title, False, False, 0)

        # Text
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.set_shadow_type(Gtk.ShadowType.IN)
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        a_text = self.srvgui.add_widget('gtk_textview_annotation_text', GtkSource.View.new_with_buffer(GtkSource.Buffer()))
        a_text.set_wrap_mode(Gtk.WrapMode.WORD)
        a_text.modify_font(Pango.FontDescription('Monospace 10'))
        a_text.set_vexpand(True)
        a_text.set_left_margin(6)
        a_text.set_top_margin(6)
        a_text.set_right_margin(6)
        a_text.set_bottom_margin(6)
        a_text.set_show_line_marks(True)
        a_text.set_show_line_numbers(True)
        a_text.set_highlight_current_line(True)
        a_textbuffer = a_text.get_buffer()
        a_textbuffer.set_text('')
        scroller.add(a_text)
        vboxl.pack_start(scroller, True, True, 3)

        # Scope entry
        hbox_scope = Gtk.HBox()
        completion = Gtk.EntryCompletion()
        completion.set_match_func(self.completion_match_func)
        completion_model = Gtk.ListStore(str)
        completion.set_model(completion_model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_inline_selection(True)
        scope = self.srvgui.add_widget('gtk_entry_annotation_scope', Gtk.Entry())
        scope.set_completion(completion)
        scope.connect('activate', self.scope_activated)

        max_width = 0
        for title in self.srvclt.get_collections_name():
            if len(title) > max_width:
                max_width = len(title)
            completion_model.append([title])

        scope.set_width_chars(max_width)
        scope.set_placeholder_text('Scope')

        ## Separator
        separator = Gtk.SeparatorToolItem.new()
        separator.set_draw(False)
        separator.set_expand(False)

        hbox_scope.pack_start(scope, False, False, 0)
        hbox_scope.pack_start(separator, True, True, 0)


        # SAP Products entry
        hbox_product = Gtk.HBox()
        completion = Gtk.EntryCompletion()
        completion.set_match_func(self.completion_match_func)
        completion_model = Gtk.ListStore(str)
        completion.set_model(completion_model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_inline_selection(True)
        product = self.srvgui.add_widget('gtk_entry_annotation_product', Gtk.Entry())
        product.set_completion(completion)
        product.connect('activate', self.product_activated)

        lproducts = open(FILE['L_SAP_PRODUCTS'], 'r').readlines()
        max_width = 0
        for title in lproducts:
            if len(title) > max_width:
                max_width = len(title)
            completion_model.append([title.strip()])

        product.set_width_chars(max_width)
        product.set_placeholder_text('Product')

        ## Separator
        separator = Gtk.SeparatorToolItem.new()
        separator.set_draw(False)
        separator.set_expand(True)

        hbox_product.pack_start(product, False, False, 0)
        hbox_product.pack_start(separator, True, True, 0)
        vboxl.pack_start(hbox_scope, False, False, 3)
        vboxl.pack_start(hbox_product, False, False, 3)
        # ~ hbox_scope.pack_start(vbox_product, False, False, 0)
        # ~ vboxl.pack_start(hbox_scope, True, True, 3)

        # Tags entry

        # Url
        hbox_url = Gtk.HBox()

        ## url entry
        a_link = self.srvgui.add_widget('gtk_entry_annotation_link', Gtk.Entry())
        a_link.set_width_chars(80)
        a_link.set_placeholder_text("Type a url here...")
        hbox_url.pack_start(a_link, False, False, 0)

        ## url button
        a_link_button = self.srvgui.add_widget('gtk_link_button_annotation_link', Gtk.LinkButton())
        a_link_button.set_relief(Gtk.ReliefStyle.NORMAL)
        a_link_button.set_label('Visit')
        hbox_url.pack_start(a_link_button, False, False, 0)

        # url type
        a_link_type_model = Gtk.ListStore(str)
        self.srvgui.add_widget('annotation_link_type_Intranet', a_link_type_model.append(['Intranet']))
        self.srvgui.add_widget('annotation_link_type_SAP Blog', a_link_type_model.append(['SAP Blog']))
        self.srvgui.add_widget('annotation_link_type_SAP Document', a_link_type_model.append(['SAP Document']))
        self.srvgui.add_widget('annotation_link_type_SAP Help', a_link_type_model.append(['SAP Help']))
        self.srvgui.add_widget('annotation_link_type_SAP Incident', a_link_type_model.append(['SAP Incident']))
        self.srvgui.add_widget('annotation_link_type_SAP Questions and Answers', a_link_type_model.append(['SAP Questions and Answers']))
        self.srvgui.add_widget('annotation_link_type_SAP Wiki', a_link_type_model.append(['SAP Wiki']))
        active = self.srvgui.add_widget('annotation_link_type_Website', a_link_type_model.append(['Website']))
        a_link_type = Gtk.ComboBox.new_with_model(a_link_type_model)
        a_link_type.set_active_iter(active)
        self.srvgui.add_widget('gtk_combobox_annotation_link_type', a_link_type)
        renderer_text = Gtk.CellRendererText()
        a_link_type.pack_start(renderer_text, True)
        a_link_type.add_attribute(renderer_text, "text", 0)
        hbox_url.pack_start(a_link_type, False, False, 0)
        vboxl.pack_start(hbox_url, False, False, 3)

        mhbox.pack_start(vboxl, True, True, 0)
        mhbox.pack_start(vboxr, False, False, 0)
        vbox.pack_start(mhbox, True, True, 0)
        return vbox



    def __setup_footer(self):
        # Buttons Accept/Cancel
        hbox = Gtk.HBox()
        self.srvgui.add_widget('annotation_footer_buttons', hbox)
        accept = self.srvgui.add_widget('gtk_button_accept_annotation', Gtk.Button('Accept'))
        # ~ accept.connect('clicked', self.srvclb.action_annotation_accept, self.sid)
        accept.set_property('always-show-image', True)
        icon = self.srvicm.get_new_image_icon('basico-check-accept', 24, 24)
        accept.set_image(icon)
        cancel = self.srvgui.add_widget('gtk_button_cancel_annotation', Gtk.Button('Cancel'))
        # ~ cancel.connect('clicked', self.srvclb.action_annotation_cancel)
        cancel.set_property('always-show-image', True)
        icon = self.srvicm.get_new_image_icon('basico-check-cancel', 24, 24)
        cancel.set_image(icon)
        hbox.pack_start(accept, True, False, 3)
        hbox.pack_start(cancel, True, False, 3)
        self.pack_start(hbox, False, False, 3)


    def set_aid_to_widget(self, aid):
        """
        C:237, 4: Missing method docstring (missing-docstring)
        """
        a_aid = self.srvgui.get_widget('gtk_label_aid')
        a_aid.set_text(aid)


    def get_aid_from_widget(self):
        """
        C:237, 4: Missing method docstring (missing-docstring)
        """
        a_aid = self.srvgui.get_widget('gtk_label_aid')
        return a_aid.get_text()



    def set_metadata_to_widget(self, aid, action='edit'):
        """
        C:237, 4: Missing method docstring (missing-docstring)
        """
        self.set_aid_to_widget(aid)
        sid = self.srvant.get_sid(aid)
        title = self.srvgui.get_widget('gtk_label_annotation_sid')
        # ~ if sid == '0000000000':
            # ~ title.set_markup('<big><b>Annotation</b></big>')

        # ~ else:
            # ~ title.set_markup('<big><b>Annotation for SAP Note %s</b></big>' % str(int(sid)))


        if action == 'create':
            # ~ self.srvuif.statusbar_msg("Creating new annotation")
            pass
        elif action == 'edit' or action == 'preview':
            # ~ self.srvuif.statusbar_msg("Creating/Editing new annotation for SAP Note %s" % str(int(sid)))
            annotation = self.srvant.get_metadata_from_aid(aid)
            if annotation is not None:
                ANNOTATION_FILE_CONTENT = LPATH['ANNOTATIONS'] + aid + '.adoc'
                a_wdg_icon = self.srvgui.get_widget('gtk_box_annotation_icon')
                a_wdg_aid = self.srvgui.get_widget('gtk_label_aid')
                a_wdg_timestamp = self.srvgui.get_widget('gtk_label_timestamp')
                # ~ a_wdg_timestamp_created = self.srvgui.get_widget('gtk_label_timestamp_created')
                a_wdg_title = self.srvgui.get_widget('gtk_entry_annotation_title')
                a_wdg_type = self.srvgui.get_widget('gtk_combobox_annotation_type')
                a_wdg_category = self.srvgui.get_widget('gtk_combobox_annotation_category')
                a_wdg_priority = self.srvgui.get_widget('gtk_combobox_annotation_priority')
                a_wdg_scope = self.srvgui.get_widget('gtk_entry_annotation_scope')
                a_wdg_product = self.srvgui.get_widget('gtk_entry_annotation_product')
                a_wdg_human_timestamp = self.srvgui.get_widget('gtk_label_human_timestamp')
                a_wdg_timestamp_created = self.srvgui.get_widget('gtk_label_timestamp_created')
                a_wdg_text = self.srvgui.get_widget('gtk_textview_annotation_text')
                a_wdg_link = self.srvgui.get_widget('gtk_entry_annotation_link')
                a_wdg_link_button = self.srvgui.get_widget('gtk_link_button_annotation_link')
                a_wdg_link_type = self.srvgui.get_widget('gtk_combobox_annotation_link_type')

                title.set_markup("<big><b>%s - </b>%s</big>" % (annotation['Type'], annotation['Title']))
                a_wdg_aid.set_text(annotation['AID'])
                icon = self.srvicm.get_new_image_icon('basico-annotation-type-%s' % annotation['Type'].lower())
                self.srvgui.swap_widget(a_wdg_icon, icon)
                a_wdg_timestamp.set_text(annotation['Timestamp'])
                a_wdg_title.set_text(html.escape(annotation['Title']))

                a_wdg_type.set_active_iter(self.srvgui.get_widget('annotation_type_%s' % annotation['Type']))

                try:
                    a_wdg_category.set_active_iter(self.srvgui.get_widget('annotation_category_%s' % annotation['Category']))
                except:
                    a_wdg_category.set_active_iter(self.srvgui.get_widget('annotation_category_Inbox'))

                try:
                    a_wdg_priority.set_active_iter(self.srvgui.get_widget('annotation_priority_%s' % annotation['Priority']))
                except:
                    a_wdg_priority.set_active_iter(self.srvgui.get_widget('annotation_priority_Normal'))

                try:
                    a_wdg_scope.set_text(annotation['Scope'])
                except:
                    a_wdg_scope.set_text('')

                try:
                    a_wdg_product.set_text(annotation['Product'])
                except:
                    a_wdg_product.set_text('')

                self.srvuif.set_textview_text(a_wdg_text, open(ANNOTATION_FILE_CONTENT).read())
                a_wdg_link.set_text(annotation['Link'])
                a_wdg_link_button.set_uri(annotation['Link'])
                a_wdg_link_type.set_active_iter(self.srvgui.get_widget('annotation_link_type_%s' % annotation['LinkType']))
                human_timestamp = self.srvutl.get_human_date_from_timestamp(annotation['Timestamp'])
                a_wdg_human_timestamp.set_markup('<b>%s</b>' % human_timestamp)
                a_wdg_timestamp_created.set_text(annotation['Created'])


    def get_metadata_from_widget(self):
        """
        C:237, 4: Missing method docstring (missing-docstring)
        """
        annotation = {}
        a_wdg_aid = self.srvgui.get_widget('gtk_label_aid')
        a_wdg_timestamp = self.srvgui.get_widget('gtk_label_timestamp')
        a_wdg_timestamp_created = self.srvgui.get_widget('gtk_label_timestamp_created')
        a_wdg_title = self.srvgui.get_widget('gtk_entry_annotation_title')
        a_wdg_type = self.srvgui.get_widget('gtk_combobox_annotation_type')
        a_wdg_category = self.srvgui.get_widget('gtk_combobox_annotation_category')
        a_wdg_priority = self.srvgui.get_widget('gtk_combobox_annotation_priority')
        a_wdg_scope = self.srvgui.get_widget('gtk_entry_annotation_scope')
        a_wdg_product = self.srvgui.get_widget('gtk_entry_annotation_product')
        a_wdg_text = self.srvgui.get_widget('gtk_textview_annotation_text')
        a_wdg_link = self.srvgui.get_widget('gtk_entry_annotation_link')
        a_wdg_link_type = self.srvgui.get_widget('gtk_combobox_annotation_link_type')

        annotation['AID'] = a_wdg_aid.get_text()
        annotation['Timestamp'] = a_wdg_timestamp.get_text()
        annotation['Created'] = a_wdg_timestamp_created.get_text()
        annotation['Title'] = a_wdg_title.get_text()
        annotation['Component'] = 'Annotation'
        annotation['Type'] = self.srvuif.get_combobox_text(a_wdg_type, 1)
        annotation['Category'] = self.srvuif.get_combobox_text(a_wdg_category, 1)
        annotation['Priority'] = self.srvuif.get_combobox_text(a_wdg_priority, 1)
        scope = a_wdg_scope.get_text()
        annotation['Scope'] = scope.strip()
        product = a_wdg_product.get_text()
        annotation['Product'] = product.strip()
        annotation['Content'] = self.srvuif.get_textview_text(a_wdg_text)
        annotation['Link'] = a_wdg_link.get_text()
        annotation['LinkType'] = self.srvuif.get_combobox_text(a_wdg_link_type, 0)

        return annotation


    def clear(self):
        a_wdg_timestamp = self.srvgui.get_widget('gtk_label_human_timestamp')
        a_wdg_timestamp_created = self.srvgui.get_widget('gtk_label_timestamp_created')
        a_wdg_title = self.srvgui.get_widget('gtk_entry_annotation_title')
        a_wdg_type = self.srvgui.get_widget('gtk_combobox_annotation_type')
        a_wdg_text = self.srvgui.get_widget('gtk_textview_annotation_text')
        a_wdg_link = self.srvgui.get_widget('gtk_entry_annotation_link')
        a_wdg_link_button = self.srvgui.get_widget('gtk_link_button_annotation_link')
        a_wdg_link_type = self.srvgui.get_widget('gtk_combobox_annotation_link_type')
        a_wdg_scope = self.srvgui.get_widget('gtk_entry_annotation_scope')
        a_wdg_product = self.srvgui.get_widget('gtk_entry_annotation_scope')

        a_wdg_timestamp.set_text('')
        a_wdg_timestamp_created.set_text('')
        a_wdg_title.set_text('')
        a_wdg_scope.set_text('')
        a_wdg_product.set_text('')
        textbuffer = a_wdg_text.get_buffer()
        textbuffer.set_text('')
        a_wdg_link.set_text('')
        a_wdg_link_button.set_uri('')


    def stack_changed(self, stack, gparam):
        paned = self.srvgui.get_widget('gtk_hpaned')
        pos = paned.get_position()
        self.srvgui.set_key_value('current_paned_position', pos)
        paned.set_position(0)
        visible_stack_name = stack.get_visible_child_name()
        # ~ self.log.debug("Annotation Stack changed to: %s", visible_stack_name)
        self.set_visible_stack(visible_stack_name)


    def preview(self):
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        aid = visor_annotations.row_current()
        # ~ aid = self.get_aid_from_widget()
        # ~ self.log.debug("Previewing aid: %s", aid)
        if len(aid) == 0:
            return

        atype = self.srvant.get_metadata_value(aid, 'Type')
        if atype is None:
            raise
            return

        browser = self.srvgui.get_widget('annotation_browser')
        # ~ self.log.debug("Execute asciidoc for current annotation: %s", self.sid)
        try:
            if atype == 'Bookmark':
                alink = self.srvant.get_metadata_value(aid, 'Link')
                if len(alink) > 0:
                    browser.load_url(alink)
            else:
                tpath = self.srvacd.get_target_path(aid)
                if not os.path.exists(tpath):
                    target = self.srvacd.generate_preview(aid)
                else:
                    spath = self.srvacd.get_source_path(aid)
                    smtime = self.srvutl.get_file_modification_date(spath)
                    tmtime = self.srvutl.get_file_modification_date(tpath)
                    # ~ self.log.debug("%s; %s", spath, smtime)
                    # ~ self.log.debug("%s; %s", tpath, tmtime)
                    if tmtime < smtime:
                        target = self.srvacd.generate_preview(aid)
                        self.log.debug("Preview generated")
                    else:
                        target = "file://" + tpath
                        self.log.debug("Using cache for preview")
                browser.load_url(html.escape(target))
        except Exception as error:
            self.log.error(error)
            self.log.debug("Showing editor instead preview")
            stack_annotation = self.srvgui.get_widget('stack_annotation')
            self.set_visible_stack('editor')
        # ~ self.log.debug("Load preview from %s", target)


    def completion_match_func(self, completion, key, iter):
        model = completion.get_model()
        text = model.get_value(iter, 0)
        if key.upper() in text.upper():
            return True
        return False


    def scope_activated(self, entry):
        scope_text = entry.get_text()
        cid = self.srvclt.get_cid_by_name(scope_text)
        if cid is None:
            for title in self.srvclt.get_collections_name():
                if scope_text.upper() in title.upper():
                    entry.set_text(title)
        else:
            entry.set_text(scope_text)


    def product_activated(self, entry):
        pass

    def display(self):
        stack_main = self.srvgui.get_widget('gtk_stack_main')
        stack_main.set_visible_child_name('dashboard')
        stack_visors = self.srvgui.get_widget('gtk_stack_visors')
        stack_visors.set_visible_child_name('visor-annotations')




    def action_annotation_create(self):
        pass
        # ~ self.gui_annotation_widget_show('', 'create')


    # ~ def action_annotation_create_from_template(self, aid):
        # ~ new_aid = self.srvant.duplicate_from_template(aid)
        # ~ self.action_annotation_edit(new_aid)


    # ~ def action_annotation_create_for_sapnote(self, sid):
        # ~ self.gui_annotation_widget_show(sid, 'create')


    # ~ def action_annotation_edit(self, aid):
        # ~ self.gui_annotation_widget_show(aid, 'edit')


    # ~ def action_annotation_preview(self, aid):
        # ~ self.gui_annotation_widget_show(aid, 'preview')


    # ~ def action_annotation_duplicate(self, *args):
        # ~ self.log.debug("ACTION-DUPLICATE: %s" % args)


    # ~ def action_annotation_delete(self, *args):
        # ~ visor_annotations = self.srvgui.get_widget('visor_annotations')
        # ~ aids = visor_annotations.rows_toggled()
        # ~ answer = self.srvuif.warning_message_delete_annotations(None, 'Deleting annotations', 'Are you sure?', aids)
        # ~ if answer is True:
            # ~ for aid in aids:
                # ~ self.srvant.delete(aid)
            # ~ visor_annotations.populate()
            # ~ self.log.info("Annotations deleted", True)
        # ~ else:
            # ~ self.log.info("Action canceled. Nothing deleted.")

        # ~ self.srvuif.grab_focus()


    # ~ def action_annotation_accept(self, button, sid):
        # ~ widget_annotation = self.srvgui.get_widget('widget_annotation')
        # ~ visor_annotations = self.srvgui.get_widget('visor_annotations')
        # ~ visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        # ~ viewmenu = self.srvgui.get_widget('viewmenu')
        # ~ notebook = self.srvgui.get_widget('gtk_notebook_annotations_visor')
        # ~ notebook.set_current_page(0)

        # ~ aid = widget_annotation.get_aid_from_widget()
        # ~ annotation = widget_annotation.get_metadata_from_widget()

        # ~ if self.srvant.is_valid(aid):
            # ~ self.srvant.update(annotation)
            # ~ title = self.srvant.get_title(aid)
            # ~ self.log.info("Updated annotation: %s" % title)
        # ~ else:
            # ~ self.srvant.create(annotation)
            # ~ title = self.srvant.get_title(aid)
            # ~ self.log.info('New annotation created: %s' % title)
        # ~ visor_annotations.populate()
        # ~ visor_sapnotes.populate()
        # ~ widget_annotation.clear()
        # ~ self.srvuif.set_widget_visibility('visortoolbar', True)
        # ~ self.srvuif.grab_focus()


    # ~ def annotation_save(self):
        # ~ widget_annotation = self.srvgui.get_widget('widget_annotation')
        # ~ aid = widget_annotation.get_aid_from_widget()
        # ~ annotation = widget_annotation.get_metadata_from_widget()

        # ~ if self.srvant.is_valid(aid):
            # ~ self.srvant.update(annotation)
            # ~ title = self.srvant.get_title(aid)
            # ~ self.log.info("Updated annotation: %s" % title, True)


    # ~ def action_annotation_cancel(self, *args):
        # ~ statusbar = self.srvgui.get_widget('widget_statusbar')
        # ~ widget_annotation = self.srvgui.get_widget('widget_annotation')
        # ~ notebook = self.srvgui.get_widget('gtk_notebook_annotations_visor')
        # ~ notebook.set_current_page(0)
        # ~ widget_annotation.clear()
        # ~ self.srvuif.set_widget_visibility('visortoolbar', True)
        # ~ self.gui_stack_dashboard_show()
        # ~ self.srvuif.grab_focus()
