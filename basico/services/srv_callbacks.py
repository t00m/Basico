#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_cb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: UI and related callbacks service
"""

import os
import json
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from basico.core.mod_srv import Service
from basico.core.mod_log import event_log, queue_log
from basico.core.mod_env import FILE, LPATH, ATYPES, APP
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_settingsview import SettingsView

MAX_WORKERS = 1 # Number of simultaneous connections

# def naming rule: <service>_<widget>_<action>

class Callback(Service):
    def initialize(self):
        self.get_services()

    def get_services(self):
        self.srvstg = self.get_service('Settings')
        self.srvdtb = self.get_service('DB')
        self.srvgui = self.get_service('GUI')
        self.srvuif = self.get_service("UIF")
        self.srvsap = self.get_service('SAP')
        self.srvicm = self.get_service('IM')
        self.srvutl = self.get_service('Utils')
        # ~ self.srvant = self.get_service('Annotation')
        # ~ self.srvbnr = self.get_service('BNR')
        self.srvclt = self.get_service('Collections')
        # ~ self.srvatc = self.get_service('Attachment')
        self.srvweb = self.get_service('Driver')


    def gui_popover_hide(self, popover):
        popover.hide()


    def gui_database_backup(self, *args):
        return

        # ~ window = self.srvgui.get_window()
        # ~ question = "Backup database"
        # ~ message = "\nShould this backup include all your annotations?"
        # ~ wdialog = self.srvuif.message_dialog_question(question, message)
        # ~ res_bck_annot = wdialog.run()
        # ~ wdialog.destroy()

        # ~ dialog = Gtk.FileChooserDialog("Please choose target folder and backup name (without extension)", window,
            # ~ Gtk.FileChooserAction.SAVE,
            # ~ ("Cancel", Gtk.ResponseType.CANCEL,
            # ~ "Select", Gtk.ResponseType.OK))
        # ~ TIMESTAMP = self.srvutl.timestamp()
        # ~ TARGET_FILE = 'basico-%s' % TIMESTAMP
        # ~ dialog.set_filename(LPATH['BACKUP'])
        # ~ dialog.set_current_folder_uri(LPATH['BACKUP'])
        # ~ dialog.set_current_name(TARGET_FILE)
        # ~ dialog.set_default_size(800, 400)
        # ~ res_bck_file = dialog.run()
        # ~ self.log.debug("Backup file: %s", dialog.get_filename())

        # ~ if res_bck_file == Gtk.ResponseType.OK:
            # ~ backup_filename = dialog.get_filename()
            # ~ if res_bck_annot == Gtk.ResponseType.YES:
                # ~ bckname = self.srvbnr.backup(backup_filename, backup_annotations=True)
                # ~ msg = "Database with annotations backed up successfully to: %s" % bckname
                # ~ dialog.destroy()
            # ~ else:
                # ~ bckname = self.srvbnr.backup(backup_filename, backup_annotations=False)
                # ~ msg = "Database without annotations backed up successfully to: %s" % bckname
            # ~ self.log.info(msg)
            # ~ self.srvuif.statusbar_msg(msg, True)
            # ~ self.srvuif.copy_text_to_clipboard(bckname)

        # ~ else:
            # ~ self.srvuif.statusbar_msg("Backup aborted by user", True)
            # ~ self.log.info("Backup aborted")
        # ~ self.srvuif.grab_focus()


    def gui_database_restore(self, *args):
        return
        # ~ visor_annotations = self.srvgui.get_widget('visor_annotations')
        # ~ window = self.srvgui.get_window()
        # ~ dialog = Gtk.FileChooserDialog("Please choose a backup file", window,
            # ~ Gtk.FileChooserAction.OPEN,
            # ~ (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            # ~ Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        # ~ dialog.set_current_folder(LPATH['BACKUP'])
        # ~ filter_zip = Gtk.FileFilter()
        # ~ filter_zip.set_name("Basico backup files")
        # ~ filter_zip.add_pattern("*.bco")
        # ~ dialog.add_filter(filter_zip)
        # ~ response = dialog.run()
        # ~ backup = dialog.get_filename()
        # ~ self.log.info("You are about to restore this file: %s" % backup)
        # ~ dialog.destroy()

        # ~ if response == Gtk.ResponseType.OK:
            # ~ res = self.srvbnr.test(backup)
            # ~ if res is None:
                # ~ dialog = self.srvuif.message_dialog_info("Backup file corrupted?", "It wasn't possible to read all data from this file")
                # ~ dialog.run()
                # ~ self.srvuif.statusbar_msg("Backup file corrupted. It wasn't possible to read all data from this file", True)
                # ~ self.log.info("Backup file corrupted?")
            # ~ else:
                # ~ # Ask if the process should force an overwrite in target database
                # ~ question = "Should the import process overwrite data?"
                # ~ message = "All metadata for SAP Notes will be overwrited and annotations with the same identifier will be overwriten"
                # ~ wdialog = self.srvuif.message_dialog_question(question, message)
                # ~ response = wdialog.run()
                # ~ wdialog.destroy()
                # ~ if response == Gtk.ResponseType.YES:
                    # ~ overwrite = True
                # ~ else:
                    # ~ overwrite = False


                # ~ # Ask for final confirmation
                # ~ sncount, ancount, clcount = res
                # ~ question = "Restoring backup %s" % os.path.basename(backup)
                # ~ message = "\n%s contains:\n\n<b>%6d SAP Notes</b>\n<b>%6d collections</b>\n<b>%6d annotations</b>\n\n" % (os.path.basename(backup), sncount, clcount, ancount)
                # ~ message += "Do you still want to restore this backup?\n"
                # ~ wdialog = self.srvuif.message_dialog_question(question, message)
                # ~ response = wdialog.run()
                # ~ wdialog.destroy()
                # ~ if response == Gtk.ResponseType.YES:
                    # ~ self.srvbnr.restore_from_backup(backup, overwrite)
                    # ~ self.srvdtb.load_notes()
                    # ~ self.srvclt.load_collections()
                    # ~ visor_annotations.populate()
                    # ~ self.gui_refresh_view()
                    # ~ self.gui_visor_sapnotes_show()
                    # ~ self.srvuif.statusbar_msg("Backup restored successfully", True)
                    # ~ self.log.info("Backup restored successfully")
                # ~ elif response == Gtk.ResponseType.NO:
                    # ~ self.srvuif.statusbar_msg("Restore aborted by user", True)
                    # ~ self.log.info("Restore aborted")
        # ~ elif response == Gtk.ResponseType.CANCEL:
            # ~ self.srvuif.statusbar_msg("Restore aborted by user", True)
            # ~ self.log.info("Restore aborted")

        # ~ dialog.destroy()
        # ~ self.srvuif.grab_focus()


    def gui_show_about(self, *args):
        return
        # ~ about = self.srvgui.get_widget('widget_about')
        # ~ stack = self.srvgui.get_widget('gtk_stack_main')
        # ~ stack.set_visible_child_name('about')
        # ~ self.gui_popover_hide(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        # ~ self.srvuif.set_widget_visibility('gtk_label_total_notes', False)
        # ~ # self.srvuif.set_widget_visibility('gtk_button_dashboard', True)
        # ~ self.srvuif.grab_focus()


    def gui_show_log(self, *args):
        return
        # ~ logviewer = self.srvgui.get_widget('widget_logviewer')
        # ~ stack = self.srvgui.get_widget('gtk_stack_main')
        # ~ logviewer.update()
        # ~ self.gui_popover_hide(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        # ~ stack.set_visible_child_name('log')
        # ~ #self.srvuif.set_widget_visibility('gtk_button_dashboard', True)
        # ~ self.srvuif.statusbar_msg("Displaying application log")
        # ~ self.srvuif.grab_focus()


    # ~ def gui_show_settings(self, button):
        # ~ notebook_menuview = self.srvgui.get_widget('gtk_notebook_menuview')
        # ~ stack = self.srvgui.get_widget('gtk_stack_main')
        # ~ view_settings = self.srvgui.get_widget('widget_settings')
        # ~ stack.set_visible_child_name('settings')
        # ~ view_settings.update()
        # ~ self.gui_popover_hide(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        # ~ self.srvuif.set_widget_visibility('gtk_label_total_notes', False)
        # ~ # self.srvuif.set_widget_visibility('gtk_button_dashboard', True)
        # ~ notebook_menuview.hide()
        # ~ view_settings.grab_focus()
        # ~ self.srvuif.statusbar_msg("Displaying application settings")


    def gui_stack_dashboard_show(self, *args):
        stack = self.srvgui.get_widget('gtk_stack_main')
        # ~ notebook_menuview = self.srvgui.get_widget('gtk_notebook_menuview')
        viewmenu = self.srvgui.get_widget('viewmenu')
        current_view = viewmenu.get_view()

        # ~ notebook_menuview.show_all()
        stack.set_visible_child_name('dashboard')
        self.gui_popover_hide(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        # ~ self.srvuif.set_widget_visibility('gtk_button_dashboard', False)

        if current_view == 'annotation':
            self.srvuif.set_widget_visibility('gtk_label_total_notes', True)
        else:
            self.srvuif.set_widget_visibility('gtk_label_total_notes', True)
        # ~ self.srvuif.statusbar_msg("Displaying application dashboard")


    def gui_toggle_help_visor(self, *args):
        button = self.srvgui.get_widget('gtk_togglebutton_help')
        notebook = self.srvgui.get_widget('gtk_notebook_visor')

        if button.get_active():
            self.srvuif.set_widget_visibility('gtk_notebook_help_page', True)
            notebook.set_current_page(2)
        else:
            self.srvuif.set_widget_visibility('gtk_notebook_help_page', False)
            notebook.set_current_page(0)
        # ~ self.srvuif.statusbar_msg("Displaying application help")


    def gui_lauch_help_visor(self, *args):
        self.srvutl.browse("file://%s" % FILE['HELP_INDEX'])


    def gui_annotation_widget_show(self, aid, action='create'):
        notebook = self.srvgui.get_widget('gtk_notebook_annotations_visor')
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        stack_main = self.srvgui.get_widget('gtk_stack_main')
        widget = self.srvgui.get_widget('gtk_label_timestamp_created')
        stack_visors = self.srvgui.get_widget('gtk_stack_visors')

        stack_visors.set_visible_child_name("visor-annotations")
        notebook.set_current_page(1)
        self.srvuif.set_widget_visibility('visortoolbar', False)

        if action == 'create':
            widget_annotation.clear()
            if aid == '':
                aid = self.srvant.gen_aid()
            else:
                sid = aid
                aid = self.srvant.gen_aid(sid)
            widget_annotation.set_visible_stack('editor')
        elif action == 'edit':
            widget_annotation.set_visible_stack('editor')
        elif action == 'preview':
            widget_annotation.set_visible_stack('preview')

        self.log.debug("Action: %s annotation with Id: %s", action, aid)

        widget_annotation.set_metadata_to_widget(aid, action)
        # ~ stack_main.set_visible_child_name('annotations')

        self.srvuif.grab_focus()


    def gui_show_popover(self, button, popover):
        self.srvgui.set_key_value('LAST_POPOVER', popover)
        if popover.get_visible():
            popover.popdown()
            popover.hide()
        else:
            popover.show_all()
            popover.popup()


    def switch_bookmark_current_view(self, *args):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        bag = visor_sapnotes.get_filtered_bag()
        try:
            for sid in bag:
                metadata = self.srvdtb.get_sapnote_metadata(sid)
                bookmark = metadata['bookmark']
                if bookmark:
                    self.sapnote_unbookmark([sid])
                else:
                    self.sapnote_bookmark([sid])
        except:
            self.log.error("Could not bookmark SAP Note %s" % sid)
            self.log.error(self.get_traceback())
        visor_sapnotes.populate(bag)
        msg = "%d SAP Notes (un)bookmarked" % len(bag)
        self.log.info(msg)
        # ~ self.srvuif.statusbar_msg(msg, True)


    def switch_bookmark(self, button, lsid, popover):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        try:
            for sid in lsid:
                metadata = self.srvdtb.get_sapnote_metadata(sid)
                bookmark = metadata['bookmark']
                if bookmark:
                    self.sapnote_unbookmark([sid])
                    # ~ self.srvuif.statusbar_msg("SAP Notes unbookmarked")
                else:
                    self.sapnote_bookmark([sid])
                    # ~ self.srvuif.statusbar_msg("SAP Notes bookmarked")
            popover.hide()
        except:
            self.log.error("Could not bookmark SAP Note %s" % sid)
            self.log.error(self.get_traceback())
        visor_sapnotes.populate()


    def sapnote_bookmark(self, lsid):
        self.srvdtb.set_bookmark(lsid)


    def sapnote_unbookmark(self, lsid):
        self.srvdtb.set_no_bookmark(lsid)


    def sapnote_import_from_launchpad(self, *args):
        db = self.get_service('DB')
        winroot = self.srvgui.get_widget('gtk_app_window_main')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        textview = self.srvgui.get_widget('gtk_textview_download_launchpad')
        dlbuffer = textview.get_buffer()
        istart, iend = dlbuffer.get_bounds()
        text = dlbuffer.get_text(istart, iend, False)

        bag = []
        all_notes = []
        sapnotes = set()
        lines = text.replace(' ', ',')
        lines = lines.replace('\n', ',')
        for sid in lines.split(','):
            sid = sid.strip()
            if len(sid) > 0:
                sapnotes.add(sid)
        for sid in sapnotes:
            is_valid = self.srvdtb.is_valid(sid)
            # ~ is_saved = self.srvdtb.get_sapnote_metadata(sid)
            if is_valid: # and not is_saved:
                bag.append(sid)
            # ~ if is_valid:
                all_notes.append(sid)
        lbag = list(bag)
        lbag.sort()

        if len(lbag) == 0:
            return

        self.log.debug("Number of SAP Notes to be downloaded: %d", len(lbag))
        self.srvsap.download(lbag)

        # ~ self.srvsap.start_fetching(len(bag))

        # ~ result = {}
        # ~ dlbag = []
        # ~ with Executor(max_workers=MAX_WORKERS) as exe:
            # ~ jobs = []
            # ~ for sid in lbag:
                # ~ job = exe.submit(self.srvsap.download, sid)
                # ~ jobs.append(job)

            # ~ for job in jobs:
                # ~ rc, sid = job.result()
                # ~ result[sid] = rc
                # ~ if rc:
                    # ~ dlbag.append(self.srvutl.format_sid(sid))
                # ~ time.sleep(0.2)

        dlbuffer.set_text('')
        # ~ self.srvsap.stop_fetching()
        db.build_stats()
        visor_sapnotes.populate(all_notes)
        visor_sapnotes.display()
        # ~ return result


    def expand_menuview(self):
        viewmenu = self.srvgui.get_widget('viewmenu')
        viewmenu.expand_all()


    def gui_viewmenu_filter(self, *args):
        entry = self.srvgui.get_widget('gtk_entry_filter_view')
        filter = entry.get_text()
        viewmenu = self.srvgui.get_widget('viewmenu')
        selection = viewmenu.get_selection()

        def gui_iterate_over_data(model, path, itr):
            rowkey = model.get(itr, 0)[0]
            rowtype, rowval = rowkey.split('@')
            dsc = model.get(itr, 1)[0]
            contents = model.get(itr, 1)[0]
            cleanstr = contents.replace('<b>', '')
            cleanstr = cleanstr.replace('</b>', '')
            model.set(itr, 1, '%s' % cleanstr)
            viewmenu.collapse_row(path)

            if len(filter) > 0:
                if filter.upper() in rowval.upper() or filter.upper() in dsc.upper():
                    viewmenu.expand_to_path (path)
                    selection.select_path(path)
                    model.set(itr, 1, '<b>%s</b>' % contents)
            else:
                return

        model = viewmenu.get_model()
        model.foreach(gui_iterate_over_data)


    def gui_viewmenu_select_first_entry(self):
        viewmenu = self.srvgui.get_widget('viewmenu')
        selection = viewmenu.get_selection()
        selection.select_path("0")


    def gui_refresh_view(self, button=None, view=None):
        window = self.srvgui.get_widget('gtk_app_window_main')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        viewmenu = self.srvgui.get_widget('viewmenu')
        if view is None:
            view = viewmenu.get_view()

        if view is not None:
            viewlabel = self.srvgui.get_widget('gtk_label_current_view')
            name = "<b>%-10s</b>" % view.capitalize()
            viewlabel.set_markup(name)

        popover = self.srvgui.get_widget('gtk_popover_button_menu_views')
        popover.hide()
        viewmenu.set_view(view)
        visor_sapnotes.display()


    def gui_toggle_menu_view(self, obj):
        paned = self.srvgui.get_widget('gtk_vbox_container_menu_view')
        button = self.srvgui.get_widget('gtk_toogletoolbutton_menu_view')
        if isinstance(obj, Gtk.ToggleToolButton):
            if button.get_active():
                paned.show_all()
            else:
                paned.hide()
        elif isinstance(obj, bool):
            if obj == True:
                button.set_active(True)
            else:
                button.set_active(False)


    def gui_toggle_fullscreen(self, button):
        icon_container = self.srvgui.get_widget('gtk_box_container_icon_fullscreen')
        icon_fullscreen = self.srvicm.get_new_image_icon('basico-fullscreen', 24, 24)
        icon_unfullscreen = self.srvicm.get_new_image_icon('basico-unfullscreen', 24, 24)
        active = button.get_active()
        window = self.srvgui.get_window()
        if active:
            self.srvgui.swap_widget(icon_container, icon_unfullscreen)
            window.fullscreen()
        else:
            self.srvgui.swap_widget(icon_container, icon_fullscreen)
            window.unfullscreen()


    def action_annotation_create(self):
        pass
        # ~ self.gui_annotation_widget_show('', 'create')


    def action_annotation_create_from_template(self, aid):
        new_aid = self.srvant.duplicate_from_template(aid)
        self.action_annotation_edit(new_aid)


    def action_annotation_create_for_sapnote(self, sid):
        self.gui_annotation_widget_show(sid, 'create')


    def action_annotation_edit(self, aid):
        self.gui_annotation_widget_show(aid, 'edit')


    def action_annotation_preview(self, aid):
        self.gui_annotation_widget_show(aid, 'preview')


    def action_annotation_duplicate(self, *args):
        self.log.debug("ACTION-DUPLICATE: %s" % args)


    def action_annotation_delete(self, *args):
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        aids = visor_annotations.rows_toggled()
        answer = self.srvuif.warning_message_delete_annotations(None, 'Deleting annotations', 'Are you sure?', aids)
        if answer is True:
            for aid in aids:
                self.srvant.delete(aid)
            visor_annotations.populate()
            # ~ self.srvuif.statusbar_msg("Annotations deleted", True)
        else:
            self.log.info("Annotations hasn't been deleted")
            # ~ self.srvuif.statusbar_msg("Action canceled. Nothing deleted.", True)

        self.srvuif.grab_focus()


    def action_annotation_accept(self, button, sid):
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        viewmenu = self.srvgui.get_widget('viewmenu')
        notebook = self.srvgui.get_widget('gtk_notebook_annotations_visor')
        notebook.set_current_page(0)

        aid = widget_annotation.get_aid_from_widget()
        annotation = widget_annotation.get_metadata_from_widget()

        if self.srvant.is_valid(aid):
            self.srvant.update(annotation)
            title = self.srvant.get_title(aid)
            # ~ self.srvuif.statusbar_msg("Updated annotation: %s" % title, True)
        else:
            self.srvant.create(annotation)
            title = self.srvant.get_title(aid)
            # ~ self.srvuif.statusbar_msg('New annotation created: %s' % title, True)
        visor_annotations.populate()
        visor_sapnotes.populate()
        widget_annotation.clear()
        self.srvuif.set_widget_visibility('visortoolbar', True)
        self.srvuif.grab_focus()


    def annotation_save(self):
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        aid = widget_annotation.get_aid_from_widget()
        annotation = widget_annotation.get_metadata_from_widget()

        if self.srvant.is_valid(aid):
            self.srvant.update(annotation)
            title = self.srvant.get_title(aid)
            # ~ self.srvuif.statusbar_msg("Updated annotation: %s" % title, True)


    def action_annotation_cancel(self, *args):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        notebook = self.srvgui.get_widget('gtk_notebook_annotations_visor')
        notebook.set_current_page(0)

        widget_annotation.clear()
        self.srvuif.set_widget_visibility('visortoolbar', True)
        # ~ page = self.srvgui.get_key_value('current_visor_tab')
        # ~ notebook = self.srvgui.get_widget('gtk_notebook_visor')
        # ~ notebook.set_current_page(page)
        # ~ self.log.debug('Annotation canceled')
        # ~ self.srvuif.statusbar_msg("Annotation canceled")
        self.gui_stack_dashboard_show()
        self.srvuif.grab_focus()


    def get_sapnotes_from_current_view(self, colname=None):
        viewmenu = self.srvgui.get_widget('viewmenu')
        view = viewmenu.get_view()
        rowtype = viewmenu.get_row_type()
        rowid = viewmenu.get_row_id()

        if view == 'collection':
            cols = self.srvclt.get_collections_by_row_title(colname)
            bag = []
            for colid in cols:
                bag.extend(self.srvdtb.get_notes_by_node('collection', colid))
        else:
            bag = self.srvdtb.get_notes_by_node(rowtype, rowid)

        return bag


    def action_collection_export_text_csv(self, *args):
        rootwin = self.srvgui.get_window()
        timestamp = self.srvutl.timestamp()
        filename = "%s%s.csv" % (LPATH['EXPORT'], timestamp)
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        bag = visor_sapnotes.get_filtered_bag()

        dialog = Gtk.FileChooserDialog("Save file", rootwin,
            Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_filename(filename)
        dialog.set_current_name(os.path.basename(filename))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            export_path = dialog.get_filename()
            res = self.srvbnr.export_to_text_csv(bag, export_path)
            self.log.info("%d SAP Notes exported to CSV format: %s", len(bag), export_path)
            # ~ self.srvuif.statusbar_msg("%d SAP Notes exported to CSV format: %s" % (len(bag), export_path), True)
            self.srvuif.copy_text_to_clipboard(export_path)
        else:
            self.log.info("Export canceled by user")
            # ~ self.srvuif.statusbar_msg("Export canceled by user", True)
        dialog.destroy()


    def action_collection_export_excel(self, *args):
        rootwin = self.srvgui.get_window()
        timestamp = self.srvutl.timestamp()
        filename = "%s%s.xlsx" % (LPATH['EXPORT'], timestamp)
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        bag = visor_sapnotes.get_filtered_bag()

        dialog = Gtk.FileChooserDialog("Save file", rootwin,
            Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_filename(filename)
        dialog.set_current_name(os.path.basename(filename))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            export_path = dialog.get_filename()
            res = self.srvbnr.export_to_excel(bag, export_path)
            if res:
                self.log.info("Selected SAP Notes exported to MS Excel format (xlsx): %s" % export_path)
                # ~ self.srvuif.statusbar_msg("%d SAP Notes exported to MS Excel format: %s" % (len(bag), export_path), True)
                self.srvuif.copy_text_to_clipboard(export_path)
            else:
                self.log.error(self.get_traceback())
        else:
            self.log.info("Export canceled by user")
            # ~ self.srvuif.statusbar_msg("Export canceled by user", True)
        dialog.destroy()


    def action_collection_export_basico(self, *args):
        rootwin = self.srvgui.get_window()
        timestamp = self.srvutl.timestamp()
        filename = "%s%s.bco" % (LPATH['EXPORT'], timestamp)
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        bag = visor_sapnotes.get_filtered_bag()

        dialog = Gtk.FileChooserDialog("Save file", rootwin,
            Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_filename(filename)
        dialog.set_current_name(os.path.basename(filename))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            export_path = dialog.get_filename()
            target = self.srvbnr.export_to_basico(bag, export_path)
            self.log.info("%d SAP Notes exported to Basico %s format: %s", len(bag), APP['version'], target)
            # ~ self.srvuif.statusbar_msg("%d SAP Notes exported to Basico %s format: %s" % (len(bag), APP['version'], target), True)
            self.srvuif.copy_text_to_clipboard(export_path)
        else:
            self.log.info("Export canceled by user")
            # ~ self.srvuif.statusbar_msg("Export canceled by user", True)
        dialog.destroy()


    def action_collection_copy_to_clipboard(self, button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        bag = visor_sapnotes.get_filtered_bag()
        text = ''
        for sid in bag:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            text += "SAP Note %s: %s - Component: %s\n" % (str(int(sid)), metadata['title'], metadata['componentkey'])
        clipboard.set_text(text, -1)

        msg = "%d SAP Notes copied to the clipboard: %s" % (len(bag), ', '.join(list(bag)))
        self.log.info(msg)
        msg = "%d SAP Notes copied to the clipboard" % len(bag)
        # ~ self.srvuif.statusbar_msg(msg, True)


    def gui_annotation_previous_row(self, *args):
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_annotations.row_previous()


    def gui_annotation_next_row(self, *args):
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_annotations.row_next()

    def gui_copy_to_clipboard_sapnote(self, widget, lsid, popover):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = ''
        for sid in lsid:
            metadata = self.srvdtb.get_sapnote_metadata(sid)
            text += "SAP Note %10s: %s - Component: %s\n" % (sid, metadata['title'], metadata['componentkey'])
        clipboard.set_text(text, -1)
        if popover is not None:
            popover.hide()
            self.srvuif.grab_focus()


    def gui_jump_to_sapnote(self, widget, sid):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        visor_sapnotes.populate([sid])
        visor_sapnotes.display()
        self.srvuif.grab_focus()
        msg = "Jumping to SAP Note %s" % sid
        self.log.info(msg)
        # ~ self.srvuif.statusbar_msg(msg)


    def gui_jump_to_annotation(self, widget, aid):
        paned = self.srvgui.get_widget('gtk_hpaned')
        notebook = self.srvgui.get_widget('gtk_notebook_visor')
        notebook_viewmenu = self.srvgui.get_widget('gtk_notebook_menuview')
        notebook_viewmenu.set_current_page(1)
        signal = self.srvgui.get_signal('gtk_notebook_visor', 'switch-page')
        GObject.signal_handler_block(notebook, signal)
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_annotations.populate([aid])
        visor_annotations.display()
        self.srvuif.grab_focus()
        msg = "Jumping to annotation %s" % aid
        self.log.info(msg)
        # ~ self.srvuif.statusbar_msg(msg)
        GObject.signal_handler_unblock(notebook, signal)
        paned.set_position(400)


    def gui_link_to_sapnote(self, *args):
        pass


    def gui_sapnotes_select_all_none(self, witch, state):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        model = visor_sapnotes.get_model()

        def get_selected_sapnotes(model, path, itr):
            component = model.get(itr, 5)
            if component != 'Annotation':
                model.set(itr, 2, state)

        model.foreach(get_selected_sapnotes)


    # ~ def gui_maximize_annotation_window(self, *args):
        # ~ vpaned = self.srvgui.get_widget('gtk_vpaned_visor')
        # ~ stack_main = self.srvgui.get_widget('gtk_stack_main')
        # ~ toggle_button = self.srvgui.get_widget('gtk_togglebutton_maximize_annotation_widget')
        # ~ if toggle_button.get_active():
            # ~ stack_main.hide()
            # ~ vpaned.set_position(0)
        # ~ else:
            # ~ stack_main.show_all()
            # ~ vpaned.set_position(450)


    def gui_attachment_add_to_sapnote(self, button, sid):
        visor_attachemnts = self.srvgui.get_widget('visor_attachments')
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        # Create annotation
        aid = self.srvant.gen_aid(sid)
        annotation = {}
        annotation["AID"] = aid
        annotation["Title"] = "Attachments added for SAP Note %s" % str(int(sid))
        annotation["Component"] = "Annotation"
        annotation["Type"] = "Note"
        annotation["Category"] = "Inbox"
        annotation["Priority"] = "Low"
        annotation["Link"] = ""
        annotation["LinkType"] = "Website"
        annotation["Origin"] = "Service-Attachment"

        # Get attachments from filechooser dialog
        attachments = self.gui_attachment_show_filechooser()

        # Add them to Basico database
        if attachments is not None:
            content = '== Attachments\n\n'
            for attachment in attachments:
                # only allow files (avoid directories)
                if os.path.isfile(attachment):
                    content += "* %s\n" % attachment
                    tid = self.srvatc.create(attachment, aid)
                    annotation["TID"] = tid
                    # ~ self.log.debug(annotation)
                annotation["Content"] = content
                self.srvant.create(annotation)
            visor_attachemnts.populate()
            visor_annotations.populate()
            visor_sapnotes.populate()
        else:
            self.log.warning("No files selected to attach")


    def gui_attachment_add_to_annotation(self, button):
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        visor_attachemnts = self.srvgui.get_widget('visor_attachments')
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        aid = widget_annotation.get_aid_from_widget()

        # Create annotation
        sid = self.srvant.get_sid(aid)
        new_aid = self.srvant.gen_aid(sid)
        annotation = {}
        annotation["AID"] = new_aid
        annotation["Title"] = "Attachments added for annotation: %s" % self.srvant.get_title(aid)
        annotation["Component"] = "Annotation"
        annotation["Type"] = "Note"
        annotation["Category"] = "Inbox"
        annotation["Priority"] = "Low"
        annotation["Link"] = ""
        annotation["LinkType"] = "Website"
        annotation["Origin"] = "Service-Attachment"

        # Get attachments from filechooser dialog
        attachments = self.gui_attachment_show_filechooser()

        # Add them to Basico database
        if attachments is not None:
            content = '== Attachments\n\n'
            for attachment in attachments:
                # only allow files (avoid directories)
                if os.path.isfile(attachment):
                    content += "* %s\n" % attachment
                    tid = self.srvatc.create(attachment, aid)
                    annotation["TID"] = tid
                    # ~ self.log.debug(annotation)
                annotation["Content"] = content
                self.srvant.create(annotation)
                self.srvant.update_timestamp(aid)
            visor_attachemnts.populate()
            visor_annotations.populate()
        else:
            self.log.warning("No files selected to attach")


    def gui_attachment_add(self, *args):
        pass
        # ~ visor_attachemnts = self.srvgui.get_widget('visor_attachments')
        # ~ visor_annotations = self.srvgui.get_widget('visor_annotations')
        # ~ visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')

        # ~ # Create annotation
        # ~ aid = self.srvant.gen_aid('0000000000')
        # ~ annotation = {}
        # ~ annotation["AID"] = aid
        # ~ annotation["Title"] = "Attachments added"
        # ~ annotation["Component"] = "Annotation"
        # ~ annotation["Type"] = "Note"
        # ~ annotation["Category"] = "Inbox"
        # ~ annotation["Priority"] = "Low"
        # ~ annotation["Link"] = ""
        # ~ annotation["LinkType"] = "Website"
        # ~ annotation["Origin"] = "Service-Attachment"

        # ~ # Get attachments from filechooser dialog
        # ~ attachments = self.gui_attachment_show_filechooser()

        # ~ # Add them to Basico database
        # ~ if attachments is not None:
            # ~ content = '== Attachments\n\n'
            # ~ for attachment in attachments:
                # ~ # only allow files (avoid directories)
                # ~ if os.path.isfile(attachment):
                    # ~ content += "* %s\n" % attachment
                    # ~ tid = self.srvatc.create(attachment, aid)
                    # ~ annotation["TID"] = tid
                    # ~ # self.log.debug(annotation)
                # ~ annotation["Content"] = content
                # ~ self.srvant.create(annotation)
            # ~ visor_attachemnts.populate()
            # ~ visor_annotations.populate()
        # ~ else:
            # ~ self.log.warning("No files selected to attach")


    def gui_attachment_show_filechooser(self):
        filenames = None
        parentwin = self.srvgui.get_window()
        dialog = Gtk.FileChooserDialog(title="Open file(s) ...",
                                       parent=parentwin,
                                       action=Gtk.FileChooserAction.OPEN,
                                       buttons=("_Cancel",
                                                Gtk.ResponseType.CANCEL,
                                        "_Open", Gtk.ResponseType.ACCEPT))
        dialog.set_select_multiple(True)
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            filenames = dialog.get_filenames()
            i = 0
            while i < len(filenames):
                filename = filenames[i]
                self.log.debug("%s was selected", filename)
                i += 1
        dialog.destroy()
        return filenames

    def copy_text_to_clipboard(self, widget, text):
        self.srvuif.copy_text_to_clipboard(text)
        self.srvuif.grab_focus()

    def update_statusbar(self, *args):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        alive = statusbar is not None
        while alive:
            record = queue_log.get()
            time.sleep(0.2)
            statusbar.message(record)
            queue_log.task_done()
        time.sleep(0.5)
