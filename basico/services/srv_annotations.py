#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_annot.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Annotations service
"""

import os
import json
import uuid
from html import escape
import glob
from os.path import sep as SEP

from basico.core.mod_env import FILE, LPATH
from basico.core.mod_srv import Service


class Annotation(Service):
    def initialize(self):
        '''
        Setup Annotation Service
        '''
        self.get_services()
        self.__fix_annotations()


    def get_services(self):
        self.srvutl = self.get_service('Utils')


    def __fix_annotations(self):
        """
        In Basico 0.4, new field 'created' is introduced.
        For annotations created before, created timestamp = updated timestamp.
        """

        for filename in self.get_all():
            metadata = self.get_metadata_from_file(filename)
            if len(metadata) > 0:
                try:
                    ts = metadata['Created']
                except Exception as error:
                    # Fix annotation metadata: add 'Created' field
                    metadata['Created'] = metadata['Timestamp']
                    with open(filename, 'w') as fa:
                        json.dump(metadata, fa)
                        self.log.debug("Fixed annotation with AID: %s", metadata['AID'])


    def gen_aid(self, sid='0000000000'):
        '''
        Generate new annotation id
        '''
        return "%s@%s" % (sid, str(uuid.uuid4()))


    def create(self, annotation):
        ANNOTATION_FILE_METADATA = LPATH['ANNOTATIONS'] + annotation['AID'] + '.json'
        ANNOTATION_FILE_CONTENT = LPATH['ANNOTATIONS'] + annotation['AID'] + '.adoc'
        annotation['Timestamp'] = self.srvutl.timestamp()
        annotation['Created'] = self.srvutl.timestamp()

        # Write annotation content first and delete it
        with open(ANNOTATION_FILE_CONTENT, 'w') as fc:
            fc.write(annotation['Content'])
        del annotation['Content']

        # Write annotation metadata
        with open(ANNOTATION_FILE_METADATA, 'w') as fa:
            json.dump(annotation, fa)

        title = self.get_title(annotation['AID'])
        self.log.info("Annotation '%s' (%s) created" % (title, annotation['AID']))


    def update_metadata(self, metadata):
        # Update annotation metadata
        ANNOTATION_FILE_METADATA = LPATH['ANNOTATIONS'] + metadata['AID'] + '.json'
        annotation = self.get_metadata_from_file(ANNOTATION_FILE_METADATA)
        for key in metadata:
            annotation[key] = metadata[key]
        annotation['Timestamp'] = self.srvutl.timestamp()

        # Write annotation metadata
        with open(ANNOTATION_FILE_METADATA, 'w') as fa:
            json.dump(annotation, fa)

        title = self.get_title(annotation['AID'])
        self.log.info("Annotation '%s' (%s) updated" % (title, annotation['AID']))


    def update_timestamp(self, aid):
        # Update annotation timestamp
        ANNOTATION_FILE_METADATA = LPATH['ANNOTATIONS'] + aid + '.json'
        annotation = self.get_metadata_from_file(ANNOTATION_FILE_METADATA)
        annotation['Timestamp'] = self.srvutl.timestamp()

        # Write annotation metadata
        with open(ANNOTATION_FILE_METADATA, 'w') as fa:
            json.dump(annotation, fa)

        title = self.get_title(annotation['AID'])
        self.log.info("Annotation '%s' (%s) updated" % (title, annotation['AID']))


    def update(self, annotation):
        self.log.debug(annotation)
        ANNOTATION_FILE_METADATA = LPATH['ANNOTATIONS'] + annotation['AID'] + '.json'
        ANNOTATION_FILE_CONTENT = LPATH['ANNOTATIONS'] + annotation['AID'] + '.adoc'

        annotation['Timestamp'] = self.srvutl.timestamp()
        # Write updated annotation first and delete the old one after
        with open(ANNOTATION_FILE_CONTENT, 'w') as fc:
            fc.write(annotation['Content'])
        del annotation['Content']

        # Write annotation metadata
        with open(ANNOTATION_FILE_METADATA, 'w') as fa:
            json.dump(annotation, fa)

        title = self.get_title(annotation['AID'])
        self.log.info("Annotation '%s' (%s) updated" % (title, annotation['AID']))


    def delete(self, aid):
        sid = self.get_sid(aid)
        ANNOTATION_FILE_METADATA = LPATH['ANNOTATIONS'] + aid + '.json'
        ANNOTATION_FILE_CONTENT = LPATH['ANNOTATIONS'] + aid + '.adoc'
        title = self.get_title(aid)

        if os.path.exists(ANNOTATION_FILE_METADATA):
            os.unlink(ANNOTATION_FILE_METADATA)

        if os.path.exists(ANNOTATION_FILE_CONTENT):
            os.unlink(ANNOTATION_FILE_CONTENT)

        self.log.info("Annotation '%s' (%s) deleted" % (title, aid))


    def get_by_sid(self, sid):
        ANNOTATION_FILES = LPATH['ANNOTATIONS'] + '*%s@*.json' % sid
        annotations = glob.glob(ANNOTATION_FILES)
        annotations.sort(reverse=True)

        return annotations


    def get_all(self):
        return glob.glob(LPATH['ANNOTATIONS'] + '*.json')


    def get_all_aids(self):
        aids = []
        fnames = self.get_all()
        for fname in fnames:
            aid = os.path.basename(fname)[:-5]
            aids.append(aid)
        return aids


    def get_total(self):
        return len(self.get_all())


    def get_sid(self, aid):
        if '@' in aid:
            return aid[:aid.find('@')]
        else:
            return aid # aid = sid


    def get_metadata_from_aid(self, aid=None):
        ANNOTATION_FILE_METADATA = LPATH['ANNOTATIONS'] + aid + '.json'
        if os.path.exists(ANNOTATION_FILE_METADATA):
            with open(ANNOTATION_FILE_METADATA, 'r') as fa:
                annotation = json.load(fa)
            return annotation
        else:
            return None


    def get_metadata_from_file(self, filename=None):
        metadata = []
        if filename is not None:
            with open(filename, 'r') as fa:
                try:
                    metadata = json.load(fa)
                except Exception as error:
                    self.log.debug("Annotation: %s", filename)
                    self.log.error(error)
            return metadata
        else:
            return metadata


    def get_metadata_value(self, aid, key):
        metadata = self.get_metadata_from_aid(aid)
        if metadata is not None:
            return metadata[key]
        return None


    def is_valid(self, aid):
        ANNOTATION_FILE = LPATH['ANNOTATIONS'] + aid + '.json'
        valid = os.path.exists(ANNOTATION_FILE)
        if valid is False:
            self.log.debug("Annotation %s is not valid or it doesn't exist yet." % aid)
        # ~ self.log.debug("Annotation valid? %s", valid)
        return valid


    def get_title(self, aid):
        ANNOTATION_FILE = LPATH['ANNOTATIONS'] + aid + '.json'
        try:
            with open(ANNOTATION_FILE, 'r') as fa:
                metadata = json.load(fa)
                return escape(metadata['Title'])
        except:
            return None


    def get_content_file(self, aid):
        return LPATH['ANNOTATIONS'] + aid + '.adoc'


    def search_term(self, term):
        matches = set()
        annotations = self.get_all()

        for fname in annotations:
            # search only in title
            with open(fname, 'r') as fa:
                try:
                    annotation = json.load(fa)
                    text = annotation['Title']
                    if term.upper() in text.upper():
                        # ~ self.log.debug("Found '%s' in '%s'", term, text)
                        matches.add(fname)
                except Exception as error:
                    self.log.error("%s: %s", fname, error)

            # SEARCH IN ALL PROPERTIES (DISABLED)
            # ~ with open(fname, 'r') as fa:
                # ~ try:
                    # ~ annotation = json.load(fa)
                    # ~ text = ''
                    # ~ for node in annotation:
                        # ~ text += annotation[node]
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


    def duplicate_from_template(self, aid):
        new_aid = self.gen_aid()
        fcname = self.get_content_file(aid)
        with open(fcname, 'r') as fc:
            content = fc.read()
        annotation = self.get_metadata_from_aid(aid)
        annotation['AID'] = new_aid
        annotation['Type'] = 'Note'
        annotation['Content'] = content
        self.create(annotation)

        return new_aid


    def duplicate(self, aid):
        new_aid = self.gen_aid()
        fcname = self.get_content_file(aid)
        with open(fcname, 'r') as fc:
            content = fc.read()
        annotation = self.get_metadata_from_aid(aid)
        annotation['AID'] = new_aid
        self.create(annotation)

        return new_aid



    def get_annotations_by_type(self, atype):
        selected = set()
        aids = self.get_all_aids()
        for aid in aids:
            this_type = self.get_metadata_value(aid, 'Type')
            if  this_type == atype:
                selected.add(aid)
        return selected


    def finalize(self):
        pass

