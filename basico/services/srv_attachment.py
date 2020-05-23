#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_attach.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Attachment service
"""

import os
import json
import uuid
import glob
import shutil
from os.path import sep as SEP

from basico.core.mod_env import FILE, LPATH
from basico.core.mod_srv import Service


class Attachment(Service):
    def initialize(self):
        '''
        Setup Attachment Service
        '''
        self.get_services()


    def get_services(self):
        self.srvutl = self.get_service('Utils')


    def gen_tid(self, sid='000000000'):
        '''
        Generate new attachment id (same as for annotations)
        '''
        return "%s@T%s" % (sid, str(uuid.uuid4()))


    def create(self, path, aid):
        sid = self.get_sid(aid)
        tid = self.gen_tid(sid)
        metadata = self.srvutl.get_file_metadata(path)
        metadata['AID'] = aid
        metadata['TID'] = tid
        metadata['Source'] = path
        metadata['Created'] = self.srvutl.timestamp()
        self.log.debug("\tAID: %s", aid)
        self.log.debug("\tTID: %s", tid)
        self.log.debug("\tPath: %s", path)
        self.log.debug("\tCreated: %s", metadata['Created'])
        ATTACHMENT_FILE_METADATA = LPATH['ATTACHMENTS'] + tid + '.json'
        ATTACHMENT_FILE_CONTENT = LPATH['ATTACHMENTS'] + tid # No extension needed

        # copy attachment file to attachemnts database
        shutil.copy(path, ATTACHMENT_FILE_CONTENT)

        # Write attachment metadata
        with open(ATTACHMENT_FILE_METADATA, 'w') as fa:
            json.dump(metadata, fa)

        self.log.info("Attachment '%s' (%s) created" % (metadata['Title'], metadata['TID']))

        return tid


    def delete(self, aid):
        sid = self.get_sid(aid)
        ATTACHMENT_FILE_METADATA = LPATH['ATTACHMENTS'] + aid + '.json'
        ATTACHMENT_FILE_CONTENT = LPATH['ATTACHMENTS'] + aid
        title = self.get_title(aid)

        if os.path.exists(ATTACHMENT_FILE_METADATA):
            os.unlink(ATTACHMENT_FILE_METADATA)

        if os.path.exists(ATTACHMENT_FILE_CONTENT):
            os.unlink(ATTACHMENT_FILE_CONTENT)

        self.log.info("Attachment '%s' (%s) deleted" % (title, aid))


    def get_by_sid(self, sid):
        matches = set()
        ATTACHMENT_FILES = LPATH['ATTACHMENTS'] + '*.json'
        attachments = glob.glob(ATTACHMENT_FILES)
        for attachment in attachments:
            if sid in attachment:
                matches.add(attachment)
        # ~ self.log.debug("Attachments for SAP Note %s: %s", sid, matches)
        return matches


    def get_all(self):
        return glob.glob(LPATH['ATTACHMENTS'] + '*.json')


    def get_total(self):
        return len(self.get_all())


    def get_sid(self, aid):
        if '@' in aid:
            return aid[:aid.find('@')]
        else:
            return '0000000000'


    def get_metadata_from_tid(self, tid=None):
        if tid is not None:
            ATTACHMENT_FILE_METADATA = LPATH['ATTACHMENTS'] + tid + '.json'
            with open(ATTACHMENT_FILE_METADATA, 'r') as fa:
                attachment = json.load(fa)
            return attachment
        else:
            return None


    def get_metadata_from_file(self, filename=None):
        if filename is not None:
            if os.path.exists(filename):
                with open(filename, 'r') as fa:
                    metadata = json.load(fa)
                return metadata
            else:
                return None


    def get_metadata_value(self, tid, key):
        metadata = self.get_metadata_from_tid(tid)
        return metadata[key]


    def is_valid(self, aid):
        ATTACHMENT_FILE_METADATA = LPATH['ATTACHMENTS'] + aid + '.json'
        ATTACHMENT_FILE_CONTENT = LPATH['ATTACHMENTS'] + aid
        ATTACHMENT_FILE = LPATH['ATTACHMENTS'] + aid + '.json'
        valid = os.path.exists(ATTACHMENT_FILE_METADATA) and os.path.exist(ATTACHMENT_FILE_CONTENT)
        if valid is False:
            self.log.debug("Attachment %s is not valid or it doesn't exist yet." % aid)

        return valid


    def get_title(self, aid):
        ATTACHMENT_FILE = LPATH['ATTACHMENTS'] + aid + '.json'
        with open(ATTACHMENT_FILE, 'r') as fa:
            metadata = json.load(fa)
            return metadata['Title']


    def search_term(self, term):
        matches = set()
        attachments = self.get_all()

        for fname in attachments:
            # search only in title
            with open(fname, 'r') as fa:
                try:
                    attachment = json.load(fa)
                    text = attachment['Title']
                    if term.upper() in text.upper():
                        # ~ self.log.debug("Found '%s' in '%s'", term, text)
                        matches.add(fname)
                except Exception as error:
                    self.log.error("%s: %s", fname, error)

            # SEARCH IN ALL PROPERTIES (DISABLED)
            # ~ with open(fname, 'r') as fa:
                # ~ try:
                    # ~ attachment = json.load(fa)
                    # ~ text = ''
                    # ~ for node in attachment:
                        # ~ text += attachment[node]
                    # ~ if term.upper() in text.upper():
                        # ~ self.log.debug("Found '%s' in '%s'", term, text)
                        # ~ matches.add(fname)
                # ~ except Exception as error:
                    # ~ self.log.error("%s: %s", fname, error)

            # SEARCH IN CONTENT (DISABLED)
            # ~ fcontent = fname.replace('.json', '.adoc')
            # ~ text = open(fcontent, 'r').read()
            # ~ if term.upper() in text.upper():
                # ~ matches.add(fname)

        return matches


    def finalize(self):
        pass

