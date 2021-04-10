#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_sap.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAP service
"""

import os
import html
import glob
import time
import uuid
import traceback
from shutil import which

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from gi.repository import GObject

from basico.core.srv import Service
from basico.core.env import LPATH
from basico.services.collections import COL_DOWNLOADED

# Default settings for SAP module
LOGIN_PAGE_URL = "https://accounts.sap.com"
LOGOUT_PAGE_URL = "https://accounts.sap.com/ui/logout"
ODATA_NOTE_URL = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')"
ODATA_NOTE_URL_LONGTEXT = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')?$expand=LongText,RefBy"
SAP_NOTE_URL = "https://launchpad.support.sap.com/#/notes/%s"
SAP_NOTE_URL_PDF = "https://launchpad.support.sap.com/services/pdf/notes/%s/E"
TIMEOUT = 10

stopWords = set(stopwords.words('english'))

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
    bag_download = set()

    def initialize(self):
        '''
        Setup AppLogic Service
        '''
        GObject.signal_new('sap-download-complete', SAP, GObject.SignalFlags.RUN_LAST, None, () )
        self.__fix_collections()
        self.connect_signals()

    def connect_signals(self):
        # ~ self.connect('sap-download-complete', self.download_complete)
        # ~ self.srvweb.connect('request-complete', self.request_complete)
        # ~ self.srvweb.connect('request-canceled', self.request_canceled)
        # ~ self.srvweb.connect('download-canceled-user', self.donwload_canceled)
        self.log.debug("Listening to Webdriver Service")

    def get_services(self):
        self.srvgui = self.get_service('GUI')
        self.srvstg = self.get_service('Settings')
        self.srvutl = self.get_service('Utils')
        self.srvdtb = self.get_service('DB')
        self.srvclt = self.get_service('Collections')
        # ~ self.srvweb = self.get_service('Driver')
        self.srvuif = self.get_service("UIF")

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

    # ~ def analyze_sapnote(self, rid, content):
        # ~ '''
        # ~ Get metadata details from SAP Note
        # ~ '''
        # ~ sapnote = {}
        # ~ try:
            # ~ f = self.srvutl.feedparser_parse(content)
            # ~ sid = f.entries[0].d_sapnotesnumber
            # ~ sapnote['id'] = sid
            # ~ sapnote['componentkey'] = f.entries[0].d_componentkey
            # ~ comptxt = f.entries[0].d_componenttext
            # ~ if comptxt == "Please use note 1433157 for finding the right component":
                # ~ comptxt = ""
            # ~ sapnote['componenttxt'] = comptxt
            # ~ sapnote['category'] = f.entries[0].d_category_detail['value']
            # ~ sapnote['language'] = f.entries[0].d_languagetext_detail['value']
            # ~ sapnote['title'] = f.entries[0].d_title_detail['value']
            # ~ sapnote['priority'] = f.entries[0].d_priority_detail['value']
            # ~ sapnote['releasedon'] = f.entries[0].d_releasedon
            # ~ sapnote['type'] = f.entries[0].d_type_detail['value']
            # ~ sapnote['version'] = f.entries[0].d_version_detail['value']
            # ~ sapnote['feedupdate'] = f.entries[0].updated
            # ~ sapnote['bookmark'] = False
            # ~ sapnote['collections'] = ["00000000-0000-0000-0000-000000000000"]
            # ~ self.log.debug ("[%s] SAP Note %s analyzed successfully", rid, sid)
        # ~ except Exception as error:
            # ~ self.log.warning("[%s] Content has no valid metadata. Skip.", rid)
            # ~ sapnote = []

        # ~ return sapnote

    def analyze_sapnote(self, rid, content, sid):
        '''
        Get metadata details from SAP Note by using the new url:
        ODATA_NOTE_URL_LONGTEXT

        FIXME: Favorite field convert to True or False
        FIXME: Get rest of the fields (RefBy and RefTo)
        '''

        def get_properties(html):
            ts = "<m:properties>"
            te = "</m:properties>"
            ps = html.rfind(ts) + len(ts)
            pe = html.rfind(te)
            return html[ps:pe]

        def get_property(properties, node):
            ts = "<d:%s>" % node
            te = "</d:%s>" % node
            ps = properties.find(ts)+ len(ts)
            pe = properties.find(te)
            return properties[ps:pe]

        sapnote = {}
        try:
            # ~ f = self.srvutl.feedparser_parse(content)
            properties = get_properties(content)
            sapnote['id'] = get_property(properties, 'SapNotesNumber')
            sapnote['componentkey'] = get_property(properties, 'ComponentKey')
            ct = get_property(properties, 'ComponentText')
            if ct == "Please use note 1433157 for finding the right component":
                ct = ""
            sapnote['componenttxt'] = ct
            sapnote['category'] = get_property(properties, 'Category')
            sapnote['language'] = get_property(properties, 'Language')
            sapnote['title'] = get_property(properties, 'Title')
            sapnote['priority'] = get_property(properties, 'Priority')
            sapnote['releasedon'] = get_property(properties, 'ReleasedOn')
            sapnote['feedupdate'] = sapnote['releasedon']
            sapnote['type'] = get_property(properties, 'Type')
            sapnote['version'] = get_property(properties, 'Version')
            sapnote['downloaded'] = ""
            sapnote['bookmark'] = get_property(properties, 'Favorite')

            # Get tags
            tagmark = "<d:TypeText>Other Terms</d:TypeText>"
            ts = content.find(tagmark) + len(tagmark)
            txts = content.find("<d:Text>", ts) + len("<d:Text>")
            txte = content.find("</d:Text>", ts)
            html_tags = html.unescape(content[txts:txte])
            t1 = html_tags.find("<p>") + len("<p>")
            t2 = html_tags.find("</p>")
            tags = html_tags[t1:t2].strip()
            if tags.startswith("<"):
                sapnote['tags'] = []
            else:
                tagset = set()
                for word in word_tokenize("%s %s" % (tags, sapnote['title'])):
                    if word not in stopWords and len(word) > 2 and not word.isdigit():
                        tagset.add(word)
                sapnote['tags'] = list(tagset)

            # Add SAP Note to an empty collection
            sapnote['collections'] = ["00000000-0000-0000-0000-000000000000"]

            self.log.debug ("[%s] SAP Note %s analyzed successfully", rid, sid)
        except Exception as error:
            self.log.warning("[%s] Analysis of SAP Note %s. Content has no valid metadata. Skip.", rid, sid)
            raise
            sapnote = []

        return sapnote

    def dispatch_sapnote(self, data, content):
        rid = data['url_rid']
        sid = data['url_sid']

        sapnote = self.analyze_sapnote(rid, content, sid)
        if len(sapnote) > 0:
            # ~ sid = sapnote['id']
            self.srvdtb.store(self.srvutl.format_sid(sid), content)
            self.srvdtb.add([sapnote])
        else:
            self.log.warning("[%s] Metadata analysis for SAP Note %s failed. Check manually:", rid, sid)
            self.log.warning("[%s] \t1. Make sure you have imported your SAP Passport profile in custom Fireforx profile:", rid)
            self.log.warning("[%s] \t   Edit profile: firefox --profile %s", rid, LPATH['FIREFOX_PROFILE'])
            self.log.warning("[%s] \t2. SAP Note %s is not available or doesn't exist", rid, sid)

    # ~ def request_complete(self, webdrvsrv, data):
        # ~ self.srvuif.activity(True)
        # ~ self.log.info("[%s] Data received for SAP Note %s", data['url_rid'], data['url_sid'])
        # ~ driver = webdrvsrv.get_driver()
        # ~ self.log.debug("[%s] %s - URL: %s", data['url_rid'], data['url_typ'], driver.current_url)
        # ~ content = driver.page_source
        # ~ eval("self.dispatch_%s(data, content)" % data['url_typ'])

        # ~ try:
            # ~ self.bag_download.remove(data['url_sid'])
        # ~ except KeyError:
            # ~ self.log.warning("Request already completed for SAP Note %s", data['url_sid'])
        # ~ bag_empty = len(self.bag_download) == 0
        # ~ self.log.debug("SAP Download basket: %s (Empty=%s)", len(self.bag_download), bag_empty)
        # ~ if bag_empty:
            # ~ self.emit('sap-download-complete')

    # ~ def request_canceled(self, webdrvsrv, data):
        # ~ self.srvuif.activity(True)
        # ~ self.log.error("[%s] Request canceled", data['url_rid'])
        # ~ self.bag_download.remove(data['url_sid'])
        # ~ self.bag_download = set()

    # ~ def donwload_canceled(self, *args):
        # ~ self.srvuif.activity(False)

    # ~ def download_complete(self, *args):
        # ~ self.srvuif.activity(False)
        # ~ self.log.info("SAP Notes downloaded")

    # ~ def download(self, bag):
        # ~ self.srvuif.activity(True)
        # ~ for sid in bag:
            # ~ uuid4 = str(uuid.uuid4())
            # ~ rid = uuid4[:uuid4.find('-')]
            # ~ try:
                # ~ content = self.srvdtb.get_sapnote_content(sid)
                # ~ if content is None:
                    # ~ self.bag_download.add(sid)
                    # ~ self.srvweb.request(sid, ODATA_NOTE_URL % sid, 'sapnote')
                    # ~ self.log.info("[%s] Requested SAP Note %s", rid, sid)
                    # ~ self.srvweb.request(rid, sid, ODATA_NOTE_URL_LONGTEXT % sid, 'sapnote')
                # ~ else:
                    # ~ self.log.info("SAP Note %s already in database", sid)
                    # ~ data = {}
                    # ~ data['url_rid'] = rid
                    # ~ data['url_sid'] = sid
                    # ~ self.dispatch_sapnote(data, content)
            # ~ except Exception as error:
                # ~ self.log.error(error)


    def set_bookmark(self, bag):
        sapnotes = self.srvdtb.get_notes()
        mylist = []
        for tid in bag:
            sid = "0"*(10 - len(tid)) + tid
            sapnotes[sid]['bookmark'] = True
            mylist.append(sapnotes[sid])
            self.log.info("SAP Note %s bookmarked" % sid)
        self.srvdtb.add(mylist)

    def set_no_bookmark(self, bag):
        sapnotes = self.srvdtb.get_notes()
        mylist = []
        for tid in bag:
            sid = "0"*(10 - len(tid)) + tid
            sapnotes[sid]['bookmark'] = False
            mylist.append(sapnotes[sid])
            self.log.info("SAP Note %s unbookmarked" % sid)
        self.srvdtb.add(mylist)

    def is_bookmark(self, sapnote):
        try:
            return self.sapnotes[sapnote]['bookmark']
        except:
            return False

    def switch_bookmark_current_view(self, *args):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        bag = visor_sapnotes.get_filtered_bag()
        try:
            for sid in bag:
                metadata = self.srvdtb.get_sapnote_metadata(sid)
                bookmark = metadata['bookmark']
                if bookmark:
                    self.unbookmark([sid])
                else:
                    self.bookmark([sid])
        except:
            self.log.error("Could not bookmark SAP Note %s" % sid)
            self.log.error(self.get_traceback())
        visor_sapnotes.populate(bag)
        self.log.info("%d SAP Notes (un)bookmarked", len(bag))

    def switch_bookmark(self, button, lsid):
        visor_sapnotes = self.srvgui.get_widget('visor_sapnotes')
        try:
            for sid in lsid:
                metadata = self.srvdtb.get_sapnote_metadata(sid)
                bookmark = metadata['bookmark']
                if bookmark:
                    self.unbookmark([sid])
                    self.log.info("SAP Notes unbookmarked")
                else:
                    self.bookmark([sid])
                    self.log.info("SAP Notes bookmarked")
        except:
            self.log.error("Could not bookmark SAP Note %s" % sid)
            self.log.error(self.get_traceback())
        visor_sapnotes.populate()

    def bookmark(self, lsid):
        self.srvdtb.set_bookmark(lsid)

    def unbookmark(self, lsid):
        self.srvdtb.set_no_bookmark(lsid)
