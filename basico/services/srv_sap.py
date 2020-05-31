#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_sap.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAP service
"""

import os
import time
import glob
import traceback
from shutil import which
from basico.core.mod_srv import Service
from basico.core.mod_env import LPATH
from basico.services.srv_collections import COL_DOWNLOADED

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
        self.srvweb = self.get_service('Driver')
        self.srvweb.connect('download-complete', self.download_complete)
        self.log.debug("Listening to Firefox Webdriver Service")
        self.srvuif = self.get_service("UIF")


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
            try:
                collections = sapnotes[sid]['collections']
                if COL_DOWNLOADED in collections and len(collections) > 1:
                    self.log.debug("Fixing SAP Note %s by unlinking 'Downloaded' collection.", sid)
                    n += 1
            except:
                pass
        self.log.debug("Fixed %d SAP Notes", n)



    def analyze_sapnote(self, content):
        '''
        Get metadata details from SAP Note
        '''
        sapnote = {}
        try:
            f = self.srvutl.feedparser_parse(content)
            sid = f.entries[0].d_sapnotesnumber
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
            pass
            # ~ self.log.warning("Error while analyzing. SAP metadata not found.")

        return sapnote

    def dispatch_sapnote(self, data, content):
        rid = data['url_rid']
        sid = data['url_sid']
        sapnote = self.analyze_sapnote(content)
        if len(sapnote) > 0:
            sid = sapnote['id']
            self.srvdtb.store(self.srvutl.format_sid(sid), content)
            self.srvdtb.add(sapnote)
        else:
            self.log.warning("[%s] Metadata analysis for SAP Note %s failed. Check manually:", rid, sid)
            self.log.warning("[%s] \t1. Make sure you have imported your SAP Passport profile in custom Fireforx profile:", rid)
            self.log.warning("[%s] \t   Edit profile: firefox --profile %s", rid, LPATH['FIREFOX_PROFILE'])
            self.log.warning("[%s] \t2. SAP Note %s is not available or doesn't exist", rid, sid)

    # ~ def dispatch_pdf(self, sid, content):
        # ~ self.log.debug(glob.glob(os.path.join(LPATH['CACHE_PDF'], '*')))
        # ~ filename = "%s.pdf" % self.srvutl.format_sid(sid)
        # ~ target = os.path.join(LPATH['CACHE_PDF'], filename)
        # ~ with open(target, 'w') as fpdf:
            # ~ fpdf.write(content)
        # ~ if os.path.exists(target):
            # ~ self.log.debug("PDF for SAP Note %s saved to: %s", sid, target)

    def download_complete(self, webdrvsrv, data):
        self.log.info("[%s] Request received", data['url_rid'])
        driver = webdrvsrv.get_driver()
        self.log.debug("\t[%s][%s] URL: %s", data['url_rid'], data['url_typ'], driver.current_url)
        content = driver.page_source
        eval("self.dispatch_%s(data, content)" % data['url_typ'])

    def download(self, bag):
        for sid in bag:
            try:
                self.log.info("Requested SAP Note %s" % sid)
                self.srvweb.request(sid, ODATA_NOTE_URL % sid, 'sapnote')
                # ~ FIXME: self.srvweb.request(sid, SAP_NOTE_URL_PDF % sid, 'pdf')

            except Exception as error:
                self.log.error(error)
                self.print_traceback()


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

