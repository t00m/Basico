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

from basico.core.mod_srv import Service

class UIFuncs(Service):
    def initialize(self):
        self.get_services()


    def get_services(self):
        self.srvgui = self.get_service('GUI')
        self.srvclb = self.get_service('Callbacks')
        self.srvicm = self.get_service('IM')
        self.srvdtb = self.get_service('DB')
        self.srvant = self.get_service('Annotation')
        self.srvutl = self.get_service('Utils')
        self.srvntf = self.get_service('Notify')


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


    def statusbar_msg(self, message, important=False): 
        statusbar = self.srvgui.get_widget('widget_statusbar')
        htimestamp = self.srvutl.get_human_date_from_timestamp()
        msg = htimestamp + '\t-\t' + message
        if statusbar is not None:
            # Maybe the widget hasn't been created yet
            statusbar.message(msg)        
        if important:
            self.srvntf.show(htimestamp, message)


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
        button.connect('clicked', self.srvclb.gui_refresh_view, '%s' % view)

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


    def warning_message_delete_annotations(self, widget, question, explanation, bag):
        window = self.srvgui.get_widget('gtk_app_window_main')
        icon = self.srvicm.get_new_image_icon('basico-delete', 96, 96)
        icon.show_all()
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, question)
        dialog.set_size_request(600, 380);
        content_area = dialog.get_content_area()
        vbox = Gtk.VBox()
        label = Gtk.Label()
        label.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        label.set_property('selectable', True)
        label.set_xalign(0.0)
        label.grab_focus()
        msg = '\t<b>This is the list of annotations to be deleted:</b>'
        vbox.pack_start(label, False, False, 0)
        scr = Gtk.ScrolledWindow()
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        msg += '\n\n'
        for aid in bag:
            msg += '\t%s\t\n' % self.srvant.get_title(aid)
        msg += '\n'
        label.set_markup(msg)

        vbox.pack_start(scr, True, True, 0)
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


    def warning_message_delete_sapnotes(self, widget, question, explanation, bag):
        window = self.srvgui.get_widget('gtk_app_window_main')
        icon = self.srvicm.get_new_image_icon('basico-delete', 96, 96)
        icon.show_all()
        dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, question)
        dialog.set_size_request(800, 600);
        content_area = dialog.get_content_area()
        vbox = Gtk.VBox()
        label = Gtk.Label()
        label.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)
        label.set_property('selectable', True)
        label.set_xalign(0.0)
        label.grab_focus()
        msg = '\t<b>You are about to delete %d SAP Notes:</b>' % len(bag)
        scr = Gtk.ScrolledWindow()
        scr.set_shadow_type(Gtk.ShadowType.NONE)
        scr.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        msg += '\n\n'
        for sid in bag:
            msg += '\t%010d - %s\t\n' % (int(sid), escape(self.srvdtb.get_title(sid)))
        msg += '\n'
        label.set_markup(msg)
        scr.add(label)
        vbox.pack_start(scr, True, True, 0)
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
        treeiter = combobox.get_active_iter()
        model = combobox.get_model()
        return model[treeiter][col]


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
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        visor_annotations = self.srvgui.get_widget('visor_annotations')

        visor_sapnotes.grab_focus()
        visor_annotations.grab_focus()


    def action_collection_copy_to_clipboard(self, button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        bag = visor_sapnotes.get_filtered_bag()
        text = ''
        for sid in bag:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            text += "SAP Note %s: %s - Component: %s\n" % (str(int(sid)), metadata['title'], metadata['componentkey'])
        clipboard.set_text(text, -1)

        msg = "%d SAP Notes copied to the clipboard" % (len(bag))
        self.srvuif.statusbar_msg(msg)
        self.log.debug(msg)


    def copy_text_to_clipboard(self, text):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)

