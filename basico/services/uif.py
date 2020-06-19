#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_uif.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Generic UI functions service
"""

from html import escape
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

from basico.core.srv import Service

class UIFuncs(Service):
    def get_services(self):
        self.srvgui = self.get_service('GUI')
        self.srvclb = self.get_service('Callbacks')
        self.srvicm = self.get_service('IM')
        self.srvutl = self.get_service('Utils')
        self.srvweb = self.get_service('Driver')
        self.srvuif = self # Trick

    def get_gtk_version(self):
        return Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()

    def check_gtk_version(self):
        vmajor, vminor, vmicro =  self.get_gtk_version()
        self.log.debug("GTK+ Version: %d.%d.%d" % (vmajor, vminor, vmicro))

        if vmajor == 3 and vminor >= 18:
            return True
        else:
            self.log.error("Please, install a modern version of GTK+ (>= 3.18)")
            return False

    def get_window_parent(self):
        return self.srvgui.get_window()

    def message_dialog_error(self, head, body):
        parent = self.get_window_parent()
        dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "%s" % head)
        dialog.format_secondary_markup("%s" % body)
        return dialog

    def message_dialog_info(self, head, body):
        parent = self.get_window_parent()
        dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "%s" % head)
        dialog.format_secondary_markup("%s" % body)
        return dialog

    def message_dialog_question(self, head, body):
        parent = self.get_window_parent()
        dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, head)
        dialog.format_secondary_markup("%s" % body)
        return dialog

    def create_menuview_button(self, view):
        hbox = Gtk.Box(spacing = 0, orientation="horizontal")
        icon = self.srvicm.get_pixbuf_icon('basico-%s' % view, 24, 24)
        image = Gtk.Image()
        image.set_from_pixbuf(icon)
        label = Gtk.Label("View by %s" % view)
        hbox.pack_start(image, False, False, 3)
        hbox.pack_start(label, False, False, 3)
        button = Gtk.Button()
        button.add(hbox)
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.srvgui.add_widget('gtk_button_menuview_%s' % view, button)
        self.srvgui.add_signal('gtk_button_menuview_%s' % view, 'clicked', 'self.srvclb.gui_menuview_update', view)
        return button

    def create_notebook_tab_label(self, iconname, title):
        hbox = Gtk.HBox()
        icon = self.srvicm.get_new_image_icon(iconname)
        label = Gtk.Label()
        label.set_markup(title)
        hbox.pack_start(icon, False, False, 3)
        hbox.pack_start(label, False, False, 0)
        hbox.show_all()

        return hbox

    def create_button(self, icon_name=None, icon_width=32, icon_heigth=32, title=''):
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        hbox = Gtk.HBox()
        icon = self.srvicm.get_new_image_icon(icon_name, icon_width, icon_heigth)
        label = Gtk.Label()
        label.set_markup(title)
        label.set_xalign(0.0)
        hbox.pack_start(icon, False, False, 6)
        hbox.pack_start(label, True, True, 0)
        button.add(hbox)

        return button

    def warning_message_delete_sapnotes(self, widget, question, explanation, bag):
        self.srvdtb = self.get_service('DB')
        window = self.srvgui.get_widget('gtk_app_window_main')
        icon = self.srvicm.get_new_image_icon('basico-delete', 96, 96)
        icon.show_all()
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, question)
        dialog.set_size_request(800, 600);
        content_area = dialog.get_content_area()
        vbox = Gtk.VBox()
        # ~ label = Gtk.Label()
        # ~ label.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        # ~ label.set_property('selectable', True)
        # ~ label.set_xalign(0.0)
        # ~ label.grab_focus()
        # ~ msg = '\t<b>You are about to delete %d SAP Notes:</b>' % len(bag)
        # ~ scr = Gtk.ScrolledWindow()
        # ~ scr.set_shadow_type(Gtk.ShadowType.NONE)
        # ~ scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # ~ msg += '\n\n'
        # ~ for sid in bag:
            # ~ msg += '\t%010d - %s\t\n' % (int(sid), escape(self.srvdtb.get_title(sid)))
        # ~ msg += '\n'
        # ~ label.set_markup(msg)
        # ~ scr.add(label)
        sapnotesbox = self.sapnotebox(bag)
        vbox.pack_start(sapnotesbox, True, True, 0)
        content_area.pack_start(vbox, True, True, 0)
        content_area.show_all()
        dialog.set_image(icon)
        dialog.format_secondary_text(explanation)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            answer = True
        else:
            answer = False
        dialog.destroy()

        return answer

    def set_widget_visibility(self, widget_name, visibility):
        widget = self.srvgui.get_widget(widget_name)
        if visibility:
            widget.set_no_show_all(False)
            widget.show_all()
        else:
            widget.set_no_show_all(True)
            widget.hide()

    def get_combobox_text(self, combobox, col):
        try:
            treeiter = combobox.get_active_iter()
            model = combobox.get_model()
            text = model[treeiter][col]
            return text.strip()
        except:
            return ''

    def set_combobox_active(self, combobox, value):
        model = combobox.get_model()
        for treeiter in model:
            self.log.debug (model[treeiter][0])

    def get_textview_text(self, textview):
        textbuffer = textview.get_buffer()
        istart, iend = textbuffer.get_bounds()
        return textbuffer.get_text(istart, iend, False)

    def set_textview_text(self, textview, text):
        textbuffer = textview.get_buffer()
        textbuffer.set_text(text)

    def dialog_info(self, title, message):
        window = self.srvgui.get_window()
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def grab_focus(self):
        try:
            popover = self.srvgui.get_key_value('LAST_POPOVER')
            popover.popdown()
        except:
            pass

    def action_collection_copy_to_clipboard(self, *args):
        self.srvdtb = self.get_service('DB')
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        bag = visor_sapnotes.get_filtered_bag()
        text = ''
        for sid in bag:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            text += "SAP Note %s: %s - Component: %s\n" % (str(int(sid)), metadata['title'], metadata['componentkey'])
        clipboard.set_text(text, -1)
        self.log.debug("%d SAP Notes copied to the clipboard: %s" % (len(bag), ', '.join(list(bag))))
        self.log.info("%d SAP Notes copied to the clipboard" % len(bag))

    def copy_text_to_clipboard(self, text):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        self.log.debug("Copied '%s' to clipboard", text)

    def get_toolbar_separator(self, draw=False, expand=False):
        tool = Gtk.SeparatorToolItem.new()
        tool.set_draw(draw)
        tool.set_expand(expand)
        return tool

    def tree_path_to_row(self, path):
        """
        Convert `path` to a list row integer.

        `path` can be either a :class:`Gtk.Treepath` instance or a string
        representation of it (as commonly used by various callbacks).
        """
        if path is None: return None
        if isinstance(path, Gtk.TreePath):
            return path.get_indices()[0]
        if isinstance(path, str):
            return int(path)
        raise TypeError("Bad type {} for path {}"
                        .format(repr(type(path)), repr(path)))

    def tree_row_to_path(self, row):
        """Convert list row integer to a :class:`Gtk.TreePath`."""
        if row is None: return None
        return Gtk.TreePath.new_from_string(str(row))

    def select_folder(self, folder=None):
        window = self.srvgui.get_window()
        dialog = Gtk.FileChooserDialog("Please, choose a folder", window, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = folder = dialog.get_filename()
        else:
            folder = None
        dialog.destroy()
        return folder

    def sapnotebox(self, lsid):
        box = Gtk.Box()
        box.set_property('margin', 6)
        scr = Gtk.ScrolledWindow()
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scr.set_shadow_type(Gtk.ShadowType.IN)
        treeview = Gtk.TreeView()
        scr.add(treeview)
        box.pack_start(scr, True, True, 0)

        model = Gtk.ListStore(
            str,        # sid
            str,        # title
            str,        # component
        )

        # SAP Note Id
        renderer_sid = Gtk.CellRendererText()
        renderer_sid.set_property('xalign', 1.0)
        renderer_sid.set_property('height', 36)
        # ~ renderer_sid.set_property('background', '#F0E3E3')
        column_sid = Gtk.TreeViewColumn('SAP Note', renderer_sid, markup=0)
        column_sid.set_visible(True)
        column_sid.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column_sid.set_expand(False)
        column_sid.set_clickable(True)
        column_sid.set_sort_indicator(True)
        column_sid.set_sort_column_id(0)
        column_sid.set_sort_order(Gtk.SortType.ASCENDING)
        model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        treeview.append_column(column_sid)

        # SAP Note title
        renderer_title = Gtk.CellRendererText()
        renderer_title.set_property('xalign', 0.0)
        renderer_title.set_property('height', 36)
        renderer_title.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        # ~ renderer_title.set_property('background', '#FFFEEA')
        column_title = Gtk.TreeViewColumn('Title', renderer_title, markup=1)
        column_title.set_visible(True)
        column_title.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column_title.set_expand(True)
        column_title.set_clickable(True)
        column_title.set_sort_indicator(True)
        column_title.set_sort_column_id(1)
        column_title.set_sort_order(Gtk.SortType.ASCENDING)
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        treeview.append_column(column_title)

        # SAP Note component
        renderer_component = Gtk.CellRendererText()
        renderer_component.set_property('xalign', 0.0)
        renderer_component.set_property('height', 36)
        # ~ renderer_component.set_property('background', '#F0E3E3')
        column_component = Gtk.TreeViewColumn('Component', renderer_component, markup=2)
        column_component.set_visible(True)
        column_component.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column_component.set_expand(False)
        column_component.set_clickable(True)
        column_component.set_sort_indicator(True)
        column_component.set_sort_column_id(1)
        column_component.set_sort_order(Gtk.SortType.ASCENDING)
        model.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        treeview.append_column(column_component)

        # Treeview properties
        treeview.set_can_focus(False)
        treeview.set_enable_tree_lines(True)
        treeview.set_headers_visible(True)
        treeview.set_enable_search(True)
        treeview.set_hover_selection(False)
        treeview.set_grid_lines(Gtk.TreeViewGridLines.NONE)
        treeview.set_enable_tree_lines(True)
        treeview.set_level_indentation(10)

        # TreeView sorting
        def sort_function(model, row1, row2, user_data):
            sort_column = 0

            value1 = model.get_value(row1, sort_column)
            value2 = model.get_value(row2, sort_column)

            if value1 < value2:
                return -1
            elif value1 == value2:
                return 0
            else:
                return 1

        self.sorted_model = Gtk.TreeModelSort(model=model)
        self.sorted_model.set_sort_func(0, sort_function, None)

        # Selection
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.NONE)

        # Set model (filtered and sorted)
        treeview.set_model(self.sorted_model)

        for sid in lsid:
            ssid = str(int(sid))
            title = self.srvdtb.get_title(sid)
            component = self.srvdtb.get_component(sid)
            model.append([ssid, escape(title), component])

        box.show_all()

        return box

    def popover_show(self, button, popover):
        self.srvgui.set_key_value('LAST_POPOVER', popover)
        if popover.get_visible():
            popover.popdown()
            popover.hide()
        else:
            popover.show_all()
            popover.popup()

    def popover_hide(self, popover):
        popover.hide()

    def activity(self, running):
        spinner = self.srvgui.get_widget('statusbar_spinner')
        if running:
            spinner.start()
        else:
            spinner.stop()

    def connect_signal(self, widget_name, signal, callback, data=None):
        widget = self.srvgui.get_widget(widget_name)
        if isinstance(callback, str):
            widget.connect(signal, eval(callback), data)
        else:
            widget.connect(signal, callback, data)
        self.log.debug("Signal '%s' connected for widget '%s'", signal, widget_name)

    ### DECORATORS
    def hide_popovers(func):
        """
        FIXME: Quick and dirty hack to popdown all popovers when they
        remain open.
        """
        def exec_gui_method(self, *args):
            gui = self.app.get_service('GUI')
            uif = self.app.get_service('UIF')
            for name in gui.get_widgets():
                widget = gui.get_widget(name)
                if isinstance(widget, Gtk.Popover):
                    # ~ self.log.debug("Popover %s down", name)
                    widget.popdown()
                    widget.hide()
            uif.grab_focus()
            func(self)
        return exec_gui_method

    hide_popovers = staticmethod( hide_popovers )

