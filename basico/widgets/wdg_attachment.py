#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: wdg_attachment.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Attachment Widget
"""

import html
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GtkSource
from basico.core.mod_env import LPATH, ATYPES
from basico.core.mod_wdg import BasicoWidget


class AttachmentWidget(BasicoWidget, Gtk.VBox):
    """
    Attachment Widget
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
        # ~ self.srvant = self.get_service('Annotation')
        self.srvutl = self.get_service('Utils')


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


    def __setup_header(self):
        # Annotation Header
        container = self.srvgui.get_widget('gtk_vbox_annotation_container')
        header = Gtk.VBox()
        separator = Gtk.Separator()
        # ~ header.pack_start(separator, False, False, 0)
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

        # Url
        hbox = Gtk.HBox()

        ## url entry
        a_link = self.srvgui.add_widget('gtk_entry_annotation_link', Gtk.Entry())
        a_link.set_placeholder_text("Type a url here...")
        hbox.pack_start(a_link, True, True, 3)

        ## url button
        a_link_button = self.srvgui.add_widget('gtk_link_button_annotation_link', Gtk.LinkButton())
        a_link_button.set_relief(Gtk.ReliefStyle.NORMAL)
        a_link_button.set_label('Visit')
        hbox.pack_start(a_link_button, False, False, 3)

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
        hbox.pack_start(a_link_type, False, False, 0)
        vboxl.pack_start(hbox, False, False, 3)

        mhbox.pack_start(vboxl, True, True, 6)
        mhbox.pack_start(vboxr, False, False, 0)
        vbox.pack_start(mhbox, True, True, 3)
        self.container_body.add(vbox)


    def __setup_footer(self):
        # Buttons Accept/Cancel
        hbox = Gtk.HBox()
        accept = self.srvgui.add_widget('gtk_button_accept_annotation', Gtk.Button('Accept'))
        accept.connect('clicked', self.srvclb.action_annotation_accept, self.sid)
        accept.set_property('always-show-image', True)
        icon = self.srvicm.get_new_image_icon('basico-check-accept', 24, 24)
        accept.set_image(icon)
        cancel = self.srvgui.add_widget('gtk_button_cancel_annotation', Gtk.Button('Cancel'))
        cancel.connect('clicked', self.srvclb.action_annotation_cancel)
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


    def set_metadata_to_widget(self, aid, action):
        """
        C:237, 4: Missing method docstring (missing-docstring)
        """
        self.set_aid_to_widget(aid)
        sid = self.srvant.get_sid(aid)
        title = self.srvgui.get_widget('gtk_label_annotation_sid')
        if sid == '0000000000':
            title.set_markup('<big><b>Annotation</b></big>')
            self.srvuif.statusbar_msg("Creating new annotation")
        else:
            title.set_markup('<big><b>Annotation for SAP Note %s</b></big>' % str(int(sid)))
            self.srvuif.statusbar_msg("Creating/Editing new annotation for SAP Note %s" % str(int(sid)))

        if action == 'create':
            pass
        elif action == 'edit':
            annotation = self.srvant.get_metadata_from_aid(aid)
            if annotation is not None:
                ANNOTATION_FILE_CONTENT = LPATH['ANNOTATIONS'] + aid + '.adoc'
                a_wdg_aid = self.srvgui.get_widget('gtk_label_aid')
                a_wdg_timestamp = self.srvgui.get_widget('gtk_label_timestamp')
                a_wdg_title = self.srvgui.get_widget('gtk_entry_annotation_title')
                a_wdg_type = self.srvgui.get_widget('gtk_combobox_annotation_type')
                a_wdg_category = self.srvgui.get_widget('gtk_combobox_annotation_category')
                a_wdg_priority = self.srvgui.get_widget('gtk_combobox_annotation_priority')
                a_wdg_human_timestamp = self.srvgui.get_widget('gtk_label_human_timestamp')
                a_wdg_timestamp_created = self.srvgui.get_widget('gtk_label_timestamp_created')
                a_wdg_text = self.srvgui.get_widget('gtk_textview_annotation_text')
                a_wdg_link = self.srvgui.get_widget('gtk_entry_annotation_link')
                a_wdg_link_button = self.srvgui.get_widget('gtk_link_button_annotation_link')
                a_wdg_link_type = self.srvgui.get_widget('gtk_combobox_annotation_link_type')

                a_wdg_aid.set_text(annotation['AID'])
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
        annotation['Content'] = self.srvuif.get_textview_text(a_wdg_text)
        annotation['Link'] = a_wdg_link.get_text()
        annotation['LinkType'] = self.srvuif.get_combobox_text(a_wdg_link_type, 0)

        return annotation
