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
from concurrent.futures import ThreadPoolExecutor as Executor

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from basico.core.mod_srv import Service
from basico.core.mod_env import FILE, LPATH, ATYPES, APP
from basico.widgets.wdg_visor_sapnotes import SAPNotesVisor
from basico.widgets.wdg_visor_toolbar import VisorToolbar
from basico.widgets.wdg_cols import CollectionsMgtView
from basico.widgets.wdg_settingsview import SettingsView

# PROPKEYS = CSV headers. SAP Note metadata
PROPKEYS = ['id', 'title', 'type', 'componentkey',
            'componenttxt', 'category', 'priority', 'releasedon',
            'language', 'version']

# Extend PROPKEYS with custom basico metadata
PROPKEYS.extend (['Bookmark'])

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
        self.srvant = self.get_service('Annotation')
        self.srvbnr = self.get_service('BNR')
        self.srvclt = self.get_service('Collections')


    def gui_visor_switch_page(self, notebook, page, page_num):
        # 0|1|(2) -> SAP Notes Visor | Annotations Visor | (Help)
        self.srvgui.set_key_value('current_visor_tab', page_num)
        notebook_viewmenu = self.srvgui.get_widget('gtk_notebook_menuview')
        paned = self.srvgui.get_widget('gtk_hpaned')

        if page_num == 0:
            self.srvuif.set_widget_visibility('gtk_button_menu_views', True)
            self.srvuif.set_widget_visibility('gtk_label_total_notes', True)
            visor = self.srvgui.get_widget('visor_sapnotes')
            visible_filter = visor.get_visible_filter()
            visor.update_total_sapnotes_count()
            paned.set_position(400)
            notebook_viewmenu.set_current_page(0)
        elif page_num == 1:
            self.srvuif.set_widget_visibility('gtk_button_menu_views', False)
            self.srvuif.set_widget_visibility('gtk_label_total_notes', True)
            visor = self.srvgui.get_widget('visor_annotations')
            visor.populate_annotations()
            paned.set_position(200)
            notebook_viewmenu.set_current_page(1)


    def gui_show_visor_sapnotes(self):
        notebook = self.srvgui.get_widget('gtk_notebook_visor')
        notebook.set_current_page(0)


    def gui_show_visor_annotations(self):
        notebook = self.srvgui.get_widget('gtk_notebook_visor')
        notebook.set_current_page(1)


    def action_search(self, entry):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        term = entry.get_text()
        page = self.srvgui.get_key_value('current_visor_tab')
        completion = self.srvgui.get_widget('gtk_entrycompletion_visor')
        completion_model = completion.get_model()
        completion_model.clear()

        if page == 0:
            bag = self.srvdtb.search(term)
            visor_sapnotes.populate_sapnotes(bag)
            ebuffer = entry.get_buffer()
            ebuffer.delete_text(0, -1)
            msg = "Found %d SAP Notes for term '%s'" % (len(bag), term)
            self.log.info(msg)
            self.srvuif.statusbar_msg(msg)
        elif page == 1:
            annotations = self.srvant.search_term(term)
            visor_annotations.populate_annotations(annotations)
            msg = "Found %d annotations for term '%s'" % (len(annotations), term)
            self.log.info(msg)
            self.srvuif.statusbar_msg(msg)



    def sapnote_browse(self, button, sid):
        self.log.info("Browsing SAP Note %d" % int(sid))
        SAP_NOTE_URL = self.srvstg.get('SAP', 'SAP_NOTE_URL')
        url = SAP_NOTE_URL % sid
        self.srvutl.browse(url)


    def sapnote_download_pdf(self, button, sid):
        self.log.info("Browsing PDF for SAP Note %d" % int(sid))
        SAP_NOTE_URL_PDF = self.srvstg.get('SAP', 'SAP_NOTE_URL_PDF')
        url = SAP_NOTE_URL_PDF % sid
        self.srvutl.browse(url)


    def sapnote_delete(self, button, sid):
        visor = self.srvgui.get_widget('visor_sapnotes')
        viewmenu = self.srvgui.get_widget('viewmenu')

        answer = self.srvuif.warning_message_delete_sapnotes(button, 'Deleting SAP Notes', 'Are you sure?', [sid])
        if answer is True:
            self.srvdtb.delete(sid)
            self.srvuif.statusbar_msg("SAP Note %s deleted" % sid, True)
            visor.reload()
        else:
            self.log.info("SAP Note %s not deletd", sid)


    def sapnote_delete_view(self, button):
        visor = self.srvgui.get_widget('visor_sapnotes')
        viewmenu = self.srvgui.get_widget('viewmenu')

        bag = visor.get_filtered_bag()
        answer = self.srvuif.warning_message_delete_sapnotes(button, 'Deleting SAP Notes', 'Are you sure?', bag)
        if answer is True:
            for sid in bag:
                self.srvdtb.delete(sid)
            visor.reload()
            msg = "Deleted %d SAP Notes" % len(bag)
            self.log.info(msg)
            self.srvuif.statusbar_msg(msg, True)
        else:
            msg = "None of the %d SAP Notes has been deleted" % len(bag)
            self.log.info(msg)
            self.srvuif.statusbar_msg(msg, True)
        visor.reload()
        viewmenu.populate()

    def gui_hide_popover(self, popover):
        popover.hide()


    def gui_database_backup(self, *args):
        window = self.srvgui.get_window()
        question = "Backup database"
        message = "\nShould this backup include all your annotations?"
        wdialog = self.srvuif.message_dialog_question(question, message)
        res_bck_annot = wdialog.run()
        wdialog.destroy()

        dialog = Gtk.FileChooserDialog("Please choose target folder and backup name (without extension)", window,
            Gtk.FileChooserAction.SAVE,
            ("Cancel", Gtk.ResponseType.CANCEL,
            "Select", Gtk.ResponseType.OK))
        TIMESTAMP = self.srvutl.timestamp()
        TARGET_FILE = 'basico-%s' % TIMESTAMP
        dialog.set_filename(LPATH['BACKUP'])
        dialog.set_current_folder_uri(LPATH['BACKUP'])
        dialog.set_current_name(TARGET_FILE)
        dialog.set_default_size(800, 400)
        res_bck_file = dialog.run()
        self.log.debug("Backup file: %s", dialog.get_filename())
        
        if res_bck_file == Gtk.ResponseType.OK:
            backup_filename = dialog.get_filename()
            if res_bck_annot == Gtk.ResponseType.YES:
                bckname = self.srvbnr.backup(backup_filename, backup_annotations=True)
                msg = "Database with annotations backed up successfully to: %s" % bckname
                dialog.destroy()
            else:
                bckname = self.srvbnr.backup(backup_filename, backup_annotations=False)
                msg = "Database without annotations backed up successfully to: %s" % bckname
            self.log.info(msg)
            self.srvuif.statusbar_msg(msg, True)
            self.srvuif.copy_text_to_clipboard(bckname)
        
        else:
            self.srvuif.statusbar_msg("Backup aborted by user", True)
            self.log.info("Backup aborted")
        self.srvuif.grab_focus()


    def gui_database_restore(self, *args):
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        window = self.srvgui.get_window()
        dialog = Gtk.FileChooserDialog("Please choose a backup file", window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_current_folder(LPATH['BACKUP'])
        filter_zip = Gtk.FileFilter()
        filter_zip.set_name("Basico backup files")
        filter_zip.add_pattern("*.bco")
        dialog.add_filter(filter_zip)
        response = dialog.run()
        backup = dialog.get_filename()
        self.log.info("You are about to restore this file: %s" % backup)
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            res = self.srvbnr.test(backup)
            if res is None:
                dialog = self.srvuif.message_dialog_info("Backup file corrupted?", "It wasn't possible to read all data from this file")
                dialog.run()
                self.srvuif.statusbar_msg("Backup file corrupted. It wasn't possible to read all data from this file", True)
                self.log.info("Backup file corrupted?")
            else:
                # Ask if the process should force an overwrite in target database
                question = "Should the import process overwrite data?"
                message = "All metadata for SAP Notes will be overwrited and annotations with the same identifier will be overwriten"
                wdialog = self.srvuif.message_dialog_question(question, message)
                response = wdialog.run()
                wdialog.destroy()
                if response == Gtk.ResponseType.YES:
                    overwrite = True
                else:
                    overwrite = False


                # Ask for final confirmation
                sncount, ancount, clcount = res
                question = "Restoring backup %s" % os.path.basename(backup)
                message = "\n%s contains:\n\n<b>%6d SAP Notes</b>\n<b>%6d collections</b>\n<b>%6d annotations</b>\n\n" % (os.path.basename(backup), sncount, clcount, ancount)
                message += "Do you still want to restore this backup?\n"
                wdialog = self.srvuif.message_dialog_question(question, message)
                response = wdialog.run()
                wdialog.destroy()
                if response == Gtk.ResponseType.YES:
                    self.srvbnr.restore_from_backup(backup, overwrite)
                    self.srvdtb.load_notes()
                    self.srvclt.load_collections()
                    visor_annotations.populate_annotations()
                    self.gui_refresh_view()
                    self.gui_show_visor_sapnotes()
                    self.srvuif.statusbar_msg("Backup restored successfully", True)
                    self.log.info("Backup restored successfully")
                elif response == Gtk.ResponseType.NO:
                    self.srvuif.statusbar_msg("Restore aborted by user", True)
                    self.log.info("Restore aborted")
        elif response == Gtk.ResponseType.CANCEL:
            self.srvuif.statusbar_msg("Restore aborted by user", True)
            self.log.info("Restore aborted")

        dialog.destroy()
        self.srvuif.grab_focus()


    def gui_show_about(self, *args):
        notebook_menuview = self.srvgui.get_widget('gtk_notebook_menuview')
        about = self.srvgui.get_widget('widget_about')
        stack = self.srvgui.get_widget('gtk_stack_main')

        stack.set_visible_child_name('about')
        self.gui_hide_popover(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        self.srvuif.set_widget_visibility('gtk_label_total_notes', False)
        self.srvuif.set_widget_visibility('gtk_button_dashboard', True)

        notebook_menuview.hide()
        self.gui_annotation_widget_hide()
        about.grab_focus()


    def gui_show_log(self, *args):
        notebook_menuview = self.srvgui.get_widget('gtk_notebook_menuview')
        logviewer = self.srvgui.get_widget('widget_logviewer')
        stack = self.srvgui.get_widget('gtk_stack_main')

        logviewer.update()
        self.gui_hide_popover(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        stack.set_visible_child_name('log')
        self.srvuif.set_widget_visibility('gtk_button_dashboard', True)

        notebook_menuview.hide()
        self.gui_annotation_widget_hide()
        logviewer.grab_focus()
        self.srvuif.statusbar_msg("Displaying application log")


    def gui_show_settings(self, button):
        notebook_menuview = self.srvgui.get_widget('gtk_notebook_menuview')
        stack = self.srvgui.get_widget('gtk_stack_main')
        view_settings = self.srvgui.get_widget('widget_settings')

        stack.set_visible_child_name('settings')
        view_settings.update()
        self.gui_hide_popover(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        self.srvuif.set_widget_visibility('gtk_label_total_notes', False)
        self.srvuif.set_widget_visibility('gtk_button_dashboard', True)

        notebook_menuview.hide()
        self.gui_annotation_widget_hide()
        view_settings.grab_focus()
        self.srvuif.statusbar_msg("Displaying application settings")


    def gui_show_dashboard(self, *args):
        stack = self.srvgui.get_widget('gtk_stack_main')
        notebook_menuview = self.srvgui.get_widget('gtk_notebook_menuview')
        viewmenu = self.srvgui.get_widget('viewmenu')
        current_view = viewmenu.get_view()

        notebook_menuview.show_all()
        stack.set_visible_child_name('visor')
        self.gui_hide_popover(self.srvgui.get_widget('gtk_popover_button_menu_system'))
        self.srvuif.set_widget_visibility('gtk_button_dashboard', False)

        if current_view == 'annotation':
            self.srvuif.set_widget_visibility('gtk_label_total_notes', True)
        else:
            self.srvuif.set_widget_visibility('gtk_label_total_notes', True)
        self.srvuif.statusbar_msg("Displaying application dashboard")


    def gui_toggle_help_visor(self, *args):
        button = self.srvgui.get_widget('gtk_togglebutton_help')
        notebook = self.srvgui.get_widget('gtk_notebook_visor')

        if button.get_active():
            self.srvuif.set_widget_visibility('gtk_notebook_help_page', True)
            notebook.set_current_page(2)
        else:
            self.srvuif.set_widget_visibility('gtk_notebook_help_page', False)
            notebook.set_current_page(0)
        self.srvuif.statusbar_msg("Displaying application help")


    def gui_lauch_help_visor(self, *args):
        self.srvutl.browse("file://%s" % FILE['HELP_INDEX'])


    def gui_annotation_widget_show(self, widget, sid='0000000000', action='create'):
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        widget = self.srvgui.get_widget('gtk_entry_annotation_title')

        if action == 'create':
            self.gui_annotation_widget_clear()
            aid = self.srvant.gen_aid(sid)
        elif action == 'edit':
            aid = sid

        widget_annotation.set_metadata_to_widget(aid, action)

        self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', True)
        widget.grab_focus()


    def gui_show_popover(self, button, popover):
        if popover.get_visible():
            popover.hide()
        else:
            popover.show_all()


    def switch_bookmark_current_view(self, *args):
        visor = self.srvgui.get_widget('visor_sapnotes')
        bag = visor.get_filtered_bag()
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
        visor.populate_sapnotes(bag)
        msg = "%d SAP Notes (un)bookmarked" % len(bag)
        self.log.info(msg)
        self.srvuif.statusbar_msg(msg, True)


    def switch_bookmark(self, button, lsid, popover):
        visor = self.srvgui.get_widget('visor_sapnotes')
        try:
            for sid in lsid:
                metadata = self.srvdtb.get_sapnote_metadata(sid)
                bookmark = metadata['bookmark']
                if bookmark:
                    self.sapnote_unbookmark([sid])
                    self.srvuif.statusbar_msg("SAP Notes unbookmarked")
                else:
                    self.sapnote_bookmark([sid])
                    self.srvuif.statusbar_msg("SAP Notes bookmarked")
            popover.hide()
        except:
            self.log.error("Could not bookmark SAP Note %s" % sid)
            self.log.error(self.get_traceback())
        visor.populate_sapnotes()


    def sapnote_bookmark(self, lsid):
        self.srvdtb.set_bookmark(lsid)


    def sapnote_unbookmark(self, lsid):
        self.srvdtb.set_no_bookmark(lsid)


    def sapnote_import_from_launchpad(self, *args):
        db = self.get_service('DB')
        webdriver = self.get_service('Driver')
        textview = self.srvgui.get_widget('gtk_textview_download_launchpad')
        visor = self.srvgui.get_widget('visor_sapnotes')

        bag = []
        all_notes = []
        sapnotes = []

        dlbuffer = textview.get_buffer()
        istart, iend = dlbuffer.get_bounds()
        text = dlbuffer.get_text(istart, iend, False)
        lines = text.replace(' ', ',')
        lines = lines.replace('\n', ',')
        for sid in lines.split(','):
            sid = sid.strip()
            if len(sid) > 0:
                sapnotes.append(sid)
        for sid in sapnotes:
            is_valid = self.srvdtb.is_valid(sid)
            is_saved = self.srvdtb.get_sapnote_metadata(sid)
            if is_valid and not is_saved:
                bag.append(sid)
            if is_valid:
                all_notes.append(sid)
        lbag = list(bag)
        lbag.sort()

        if len(bag)> 0:
            driver = webdriver.open()

        winroot = self.srvgui.get_widget('gtk_app_window_main')
        msg = "%d SAP Notes to be downloaded: %s" % (len(bag), ', '.join(list(bag)))
        self.log.info(msg)

        result = {}

        self.srvsap.start_fetching(len(bag))
        dlbag = []

        # FIXME: max_workers = 1 = Threads disabled
        # Indeed, I think this is the best option right now.
        with Executor(max_workers=1) as exe:
            jobs = []
            for sapnote in lbag:
                job = exe.submit(self.srvsap.fetch, driver, sapnote)
                jobs.append(job)

            for job in jobs:
                rc, sapnote = job.result()
                msg = "\tRC SAP Note %s: %s" % (sapnote, rc)
                self.log.info(msg)
                result[sapnote] = rc
                if rc:
                    sid = "0"*(10 - len(sapnote)) + sapnote
                    dlbag.append(sid)
                time.sleep(0.2)

        dlbuffer.set_text('')
        popover = self.srvgui.get_widget('gtk_popover_toolbutton_import')
        self.gui_hide_popover(popover)
        if len(bag) > 0:
            webdriver.close(driver)

        self.srvsap.stop_fetching()
        db.save_notes()
        db.build_stats()
        self.log.info("Download completed.")
        self.srvuif.statusbar_msg("Download completed", True)
        visor.populate_sapnotes(all_notes)
        self.gui_show_visor_sapnotes()
        return result


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


    def gui_filter_visor(self, entry):
        page = self.srvgui.get_key_value('current_visor_tab')
        if page == 0:
            visor = self.srvgui.get_widget('visor_sapnotes')
            visible_filter = visor.get_visible_filter()
            visible_filter.refilter()
            visor.update_total_sapnotes_count()
        elif page == 1:
            visor = self.srvgui.get_widget('visor_annotations')
            visor.populate_annotations()
            visible_filter = visor.get_visible_filter()
            visible_filter.refilter()
            visor.update_total_annotations_count()


    def gui_refresh_view(self, button=None, view=None):
        window = self.srvgui.get_widget('gtk_app_window_main')
        viewmenu = self.srvgui.get_widget('viewmenu')
        if view is None:
            view = viewmenu.get_view()

        if view is not None:
            viewlabel = self.srvgui.get_widget('gtk_label_current_view')
            name = "<b>%-10s</b>" % view.capitalize()
            viewlabel.set_markup(name)
        viewmenu.set_view(view)
        popover = self.srvgui.get_widget('gtk_popover_button_menu_views')
        popover.hide()
        self.gui_show_visor_sapnotes()


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


    def action_annotation_edit(self, aid):
        self.gui_annotation_widget_show(None, aid, 'edit')


    def action_annotation_duplicate(self, *args):
        self.log.debug("ACTION-DUPLICATE: %s" % args)


    def action_annotation_delete(self, *args):
        visor = self.srvgui.get_widget('visor_annotations')
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        aid = widget_annotation.get_aid_from_widget()

        answer = self.srvuif.warning_message_delete_annotations(None, 'Deleting annotations', 'Are you sure?', [aid])
        if answer is True:
            title = self.srvant.get_title(aid)
            self.srvant.delete(aid)
            self.gui_annotation_widget_clear()
            self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
            visor.populate_annotations()
            self.srvuif.statusbar_msg("Annotation <i>'%s'</i> deleted" % title, True)
        else:
            self.log.info("Annotation %s hasn't been deleted" % title)
            self.srvuif.statusbar_msg("Action canceled. Nothing deleted.", True)

        self.srvuif.grab_focus()


    def action_annotation_accept(self, button, sid):
        widget_annotation = self.srvgui.get_widget('widget_annotation')
        visor_annotations = self.srvgui.get_widget('visor_annotations')
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        viewmenu = self.srvgui.get_widget('viewmenu')

        aid = widget_annotation.get_aid_from_widget()
        annotation = widget_annotation.get_metadata_from_widget()

        if self.srvant.is_valid(aid):
            self.srvant.update(annotation)
            title = self.srvant.get_title(aid)
            self.srvuif.statusbar_msg("Updated annotation: %s" % title, True)
        else:
            self.srvant.create(annotation)
            title = self.srvant.get_title(aid)
            self.srvuif.statusbar_msg('New annotation created: %s' % title, True)
        visor_annotations.populate_annotations()
        visor_sapnotes.populate_sapnotes()
        self.gui_annotation_widget_clear()
        self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
        self.srvuif.grab_focus()


    def action_annotation_cancel(self, *args):
        statusbar = self.srvgui.get_widget('widget_statusbar')
        self.gui_annotation_widget_clear()
        self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)
        self.log.debug('Annotation canceled')
        self.srvuif.statusbar_msg("Annotation canceled")
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
            self.srvuif.statusbar_msg("%d SAP Notes exported to CSV format: %s" % (len(bag), export_path), True)
            self.srvuif.copy_text_to_clipboard(export_path)
        else:
            self.log.info("Export canceled by user")
            self.srvuif.statusbar_msg("Export canceled by user", True)
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
                self.srvuif.statusbar_msg("%d SAP Notes exported to MS Excel format: %s" % (len(bag), export_path), True)
                self.srvuif.copy_text_to_clipboard(export_path)
            else:
                self.log.error(self.get_traceback())
        else:
            self.log.info("Export canceled by user")
            self.srvuif.statusbar_msg("Export canceled by user", True)
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
            self.srvuif.statusbar_msg("%d SAP Notes exported to Basico %s format: %s" % (len(bag), APP['version'], target), True)
            self.srvuif.copy_text_to_clipboard(export_path)
        else:
            self.log.info("Export canceled by user")
            self.srvuif.statusbar_msg("Export canceled by user", True)
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
        self.srvuif.statusbar_msg(msg, True)


    def gui_annotation_widget_clear(self):
        a_wdg_timestamp = self.srvgui.get_widget('gtk_label_human_timestamp')
        a_wdg_title = self.srvgui.get_widget('gtk_entry_annotation_title')
        a_wdg_type = self.srvgui.get_widget('gtk_combobox_annotation_type')
        a_wdg_text = self.srvgui.get_widget('gtk_textview_annotation_text')
        a_wdg_link = self.srvgui.get_widget('gtk_entry_annotation_link')
        a_wdg_link_button = self.srvgui.get_widget('gtk_link_button_annotation_link')
        a_wdg_link_type = self.srvgui.get_widget('gtk_combobox_annotation_link_type')

        a_wdg_timestamp.set_text('')
        a_wdg_title.set_text('')
        textbuffer = a_wdg_text.get_buffer()
        textbuffer.set_text('')
        a_wdg_link.set_text('')
        a_wdg_link_button.set_uri('')
        self.gui_annotation_widget_hide()


    def gui_annotation_widget_hide(self):
        self.srvuif.set_widget_visibility('gtk_vbox_container_annotations', False)


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
        visor_sapnotes.populate_sapnotes([sid])
        self.gui_show_visor_sapnotes()
        self.srvuif.grab_focus()
        msg = "Jumping to SAP Note %s" % sid
        self.log.info(msg)
        self.srvuif.statusbar_msg(msg)


    def gui_link_to_sapnote(self, *args):
        pass

    def gui_switch_selection_atypes(self, switch, state):
        label = self.srvgui.get_widget('gtk_label_switch_select_atypes')
        switched = switch.get_active()
        switch.set_state(switched)
        if switched is True:
            label.set_text ("All selected")

        else:
            label.set_text("None selected")

        for name in ATYPES:
            button = self.srvgui.get_widget('gtk_button_type_%s' % name.lower())
            button.set_state(switched)
            button.set_active(switched)


    def gui_sapnotes_select_all_none(self, witch, state):
        visor = self.srvgui.get_widget('visor_sapnotes')
        model = visor.get_model()

        def get_selected_sapnotes(model, path, itr):
            component = model.get(itr, 5)
            if component != 'Annotation':
                model.set(itr, 2, state)

        model.foreach(get_selected_sapnotes)
