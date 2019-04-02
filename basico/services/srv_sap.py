#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_sap.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAP service
"""

import time
import traceback
from shutil import which
from basico.core.mod_srv import Service
from basico.core.mod_env import LPATH
from basico.services.srv_cols import COL_DOWNLOADED

# Default settings for SAP module
LOGIN_PAGE_URL = "https://accounts.sap.com"
LOGOUT_PAGE_URL = "https://accounts.sap.com/ui/logout"
ODATA_NOTE_URL = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')"
ODATA_NOTE_URL_LONGTEXT = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')?$expand=LongText"
SAP_NOTE_URL = "https://launchpad.support.sap.com/#/notes/%s"
SAP_NOTE_URL_PDF = "https://launchpad.support.sap.com/services/pdf/notes/%s/E"
TIMEOUT = 10

"""
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/RefBy"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/RefTo"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/CorrIns"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/Patch"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/Sp"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/SoftCom"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/Attach"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/LongText"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/Languages"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/SideCau"
<link href="TrunkSet(SapNotesNumber='0002258035',Version='4',Language='E')/SideSol"
"""


class SAP(Service):
    def initialize(self):
        '''
        Setup AppLogic Service
        '''
        self.get_services()
        self.__init_config_section()
        self.__fix_collections()


    def get_services(self):
        self.srvstg = self.get_service('Settings')
        self.srvutl = self.get_service('Utils')
        self.srvdtb = self.get_service('DB')
        self.srvclt = self.get_service('Collections')


    def __init_config_section(self):
        settings = self.srvstg.load()
        settings[self.section]
        try:
            settings[self.section]['LOGIN_PAGE_URL']
        except:
            settings[self.section]['LOGIN_PAGE_URL'] = LOGIN_PAGE_URL

        try:
            settings[self.section]['LOGOUT_PAGE_URL']
        except:
            settings[self.section]['LOGOUT_PAGE_URL'] = LOGOUT_PAGE_URL

        try:
            settings[self.section]['ODATA_NOTE_URL']
        except:
            settings[self.section]['ODATA_NOTE_URL'] = ODATA_NOTE_URL

        try:
            settings[self.section]['ODATA_NOTE_URL_LONGTEXT']
        except:
            settings[self.section]['ODATA_NOTE_URL_LONGTEXT'] = ODATA_NOTE_URL_LONGTEXT

        try:
            settings[self.section]['SAP_NOTE_URL']
        except:
            settings[self.section]['SAP_NOTE_URL'] = SAP_NOTE_URL

        try:
            settings[self.section]['SAP_NOTE_URL_PDF']
        except:
            settings[self.section]['SAP_NOTE_URL_PDF'] = SAP_NOTE_URL_PDF

        try:
            settings[self.section]['TIMEOUT']
        except:
            settings[self.section]['TIMEOUT'] = TIMEOUT

        self.srvstg.save(settings)


    def __fix_collections(self):
        self.log.debug("Fixing collections in SAP Notes")
        self.log.debug("Fix 1. Check for existence of 'collections' property")
        sapnotes = self.srvdtb.get_notes()
        n = 0
        for sid in sapnotes:
            try:
                collections = sapnotes[sid]['collections']
                if len(collections) == 0:
                    self.srvdtb.set_collections(sid, [COL_DOWNLOADED])
                    n += 1
            except KeyError:
                self.log.debug("SAP Note %s doesn't has 'collections' property. Fixing...", sid)
                self.srvdtb.set_collections(sid, [COL_DOWNLOADED])    
            except Exception as error:
                self.log.error(error)
                self.log.error(self.get_traceback())
        self.log.debug("Fixed %d SAP Notes", n)

        self.log.debug("Fix 2. Unlik 'Downloaded' collections for SAP Notes with more than one collection")
        n = 0
        for sid in sapnotes:
            collections = sapnotes[sid]['collections']
            if COL_DOWNLOADED in collections and len(collections) > 1:
                self.log.debug("Fixing SAP Note %s by unlinking 'Downloaded' collection.", sid)
                n += 1
        self.log.debug("Fixed %d SAP Notes", n)
        
        

    def analyze_sapnote(self, sid, content):
        '''
        Get metadata details from SAP Note
        '''
        try:
            f = self.srvutl.feedparser_parse(content)
            sid = f.entries[0].d_sapnotesnumber
            sapnote = {}
            sapnote['id'] = sid
            sapnote['componentkey'] = f.entries[0].d_componentkey
            comptxt = f.entries[0].d_componenttext
            if comptxt == "Please use note 1433157 for finding the right component":
                comptxt = ""
            sapnote['componenttxt'] = comptxt
            sapnote['category'] = f.entries[0].d_category_detail['value']
            sapnote['language'] = f.entries[0].d_languagetext_detail['value']
            sapnote['title'] = f.entries[0].d_title_detail['value']
            sapnote['priority'] = f.entries[0].d_priority_detail['value']
            sapnote['releasedon'] = f.entries[0].d_releasedon
            sapnote['type'] = f.entries[0].d_type_detail['value']
            sapnote['version'] = f.entries[0].d_version_detail['value']
            sapnote['feedupdate'] = f.entries[0].updated
            sapnote['bookmark'] = False
            sapnote['collections'] = ["00000000-0000-0000-0000-000000000000"]
            self.log.debug ("SAP Note %s analyzed successfully" % sid)
        except Exception as error:
            sapnote = {}
            self.log.error("Error while analyzing data for SAP Note %s" % sid)

        return sapnote


    def fetch(self, driver, sid):
        valid = False

        if not self.srvdtb.is_stored(sid):
            self.log.debug("%3d/%3d - SAP Note %s must be downloaded" % (self.notes_fetched+1, self.notes_total, sid))
            content = self.download(driver, sid)
            if len(content) > 0:
                self.log.debug("%3d/%3d - SAP Note %s fetched" % (self.notes_fetched+1, self.notes_total, sid))
            else:
                self.log.debug("%3d/%3d - SAP Note %s not feched" % (self.notes_fetched+1, self.notes_total, sid))
        else:
            self.log.debug("%3d/%3d - SAP Note %s will be analyzed again" % (self.notes_fetched+1, self.notes_total, sid))
            content = self.srvdtb.get_sapnote_content(sid)

        self.fetched()

        sapnote = self.analyze_sapnote(sid, content)
        if len(sapnote) > 0:
            self.srvdtb.add(sapnote)
            self.srvdtb.store(sid, content)
            valid = True
        return valid, sid


    def start_fetching(self, total):
        self.notes_fetched = 0
        self.notes_total = total


    def fetched(self):
        self.notes_fetched += 1


    def stop_fetching(self):
        self.notes_fetched = 0
        self.notes_total = 0


    def download(self, driver, sapnote=None):
        try:
            webdriver = self.get_service('Driver')
            ODATA_NOTE_URL = self.srvstg.get('SAP', 'ODATA_NOTE_URL')
            timeout = self.srvstg.get('SAP', 'TIMEOUT')
            self.log.debug("Downloading SAP Note %s" % sapnote)
            browser = webdriver.load(driver, ODATA_NOTE_URL % sapnote)
            time.sleep(timeout)
            content = browser.page_source
            fsn = LPATH['CACHE_XML'] + sapnote + '.xml'
            with open(fsn, 'w') as fxml:
                fxml.write(content)
        except Exception as error:
            self.log.error(error)
            content = ''

        return content


    def set_bookmark(self, bag):
        sapnotes = self.srvdtb.get_notes()
        mylist = []
        for tid in bag:
            sid = "0"*(10 - len(tid)) + tid
            sapnotes[sid]['bookmark'] = True
            mylist.append(sapnotes[sid])
            self.log.info("SAP Note %s bookmarked" % sid)
        self.srvdtb.add_list(mylist)


    def set_no_bookmark(self, bag):
        sapnotes = self.srvdtb.get_notes()
        mylist = []
        for tid in bag:
            sid = "0"*(10 - len(tid)) + tid
            sapnotes[sid]['bookmark'] = False
            mylist.append(sapnotes[sid])
            self.log.info("SAP Note %s unbookmarked" % sid)
        self.srvdtb.add_list(mylist)


    def is_bookmark(self, sapnote):
        try:
            return self.sapnotes[sapnote]['bookmark']
        except:
            return False

