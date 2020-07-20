#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_cols.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Collections service
"""

import os
import json
import uuid

from basico.core.env import FILE
from basico.core.srv import Service

COL_DOWNLOADED = "00000000-0000-0000-0000-000000000000"

HEADER = ['id', 'title']

class Collections(Service):
    def initialize(self):
        '''
        Setup Collections Service
        '''
        self.clts = {}
        self.load_collections()

        # Always check if 'Downloaded' collection exists
        if not self.exists(COL_DOWNLOADED):
            self.log.warning("Default collection <i>Download</i> not found")
            self.create('Downloaded', COL_DOWNLOADED)
            self.log.info("Created collection <i>Download</i>")

    def get_services(self):
        self.srvgui = self.get_service("GUI")
        self.srvuif = self.get_service("UIF")
        self.srvicm = self.get_service('IM')
        self.srvdtb = self.get_service('DB')


    def exists(self, cid):
        try:
            self.clts[cid]
            return True
        except:
            return False


    def load_collections(self):
        try:
            with open(FILE['DBCOLS'], 'r') as ft:
                self.clts = json.load(ft)
                self.log.info("Collections database found")
                self.log.debug("Collections Database found at: %s with %d collections", FILE['DBCOLS'], len(self.clts))
        except Exception as error:
            self.log.warning("Collections database not found.")
            self.save()
            self.log.info("Created a new Collections database.")


    def save(self, collections={}):
        if len(collections) == 0:
            collections = self.clts
        with open(FILE['DBCOLS'], 'w') as ft:
            json.dump(collections, ft)
            self.log.debug ("Saved %d collections" % (len(collections)))


    def get_all(self):
        return self.clts


    def get_collections_by_row_title(self, row_title):
        cids = []
        for cid in self.clts:
            col_name = self.get_name_by_cid(cid)
            if row_title in col_name:
                cids.append(cid)
        return cids


    def get_collections_name(self):
        names = []
        for tid in self.clts:
            names.append(self.clts[tid])
        names.sort()

        return names


    def get_collections_id(self):
        tids = []
        for tid in self.clts:
            tids.append(tid)
        return tids


    def create(self, name, cid=None, batch=False):
        if len(name) == 0:
            msg = "Trying to create a collection without name is not allowed"
            self.log.debug(msg)
            return (False, msg)

        name_exists = name in self.get_collections_name()
        if name_exists:
            cid = self.get_cid_by_name(name)
            self.log.warning("Collection '%s' already exists in the database with cid: %s" % (name, cid))
            return (False, "Collection '%s' already exists in the database" % name)
        else:
            if cid is None:
                cid = str(uuid.uuid4())
                cid_exists = cid in self.get_collections_id()
                if cid_exists:
                    self.log.error("Collision? :) Let's try again with another id...")
                    self.create(name)

            self.clts[cid] = name
            self.log.debug("Created collection: '%s'", name)
            self.log.debug("Created collection: '%s' with cid: '%s'",name, cid)
            if batch is False:
                self.save()
            return (True, "Created collection: %s" % name)


    def delete(self, cid):
        # Do not allow to delete this 'system' collection
        name = self.get_name_by_cid(cid)
        if cid == COL_DOWNLOADED:
            self.log.warning("You can't delete this collection: <i>%s</i>", name)
            return

        try:
            sapnotes = self.srvdtb.get_notes_by_node('collection', cid)
            if len(sapnotes) > 0:
                return False
            else:
                del(self.clts[cid])
                self.log.info("<b>Collection <i>%s</i> deleted</b>", name)
                self.save()
                return True
        except KeyError:
            self.log.error("<b>You can't delete a non existent collection...</b>")
        except Exception as error:
            self.log.error("<b>Error deleting collection: <i>%s</i></b>" % self.get_traceback())


    def get_name_by_cid(self, cid):
        try:
            return self.clts[cid]
        except KeyError:
            return None


    def get_cid_by_name(self, name):
        database = self.get_all()
        for col in database:
            if database[col] == name:
                return col

        return None


    def rename(self, cid, target):
        # check if collections name are the same
        source = self.get_name_by_cid(cid)
        if source == target:
            self.log.warning("Rename not possible: same name.")
            return

        # check if the new name already exists in database
        acid = self.get_cid_by_name(target)
        if acid is not None:
            self.log.warning("Rename not possible: there is already another collection with this name.")
            return

        # Finally, rename the collection and save it.
        self.clts[cid] = target
        self.log.info("Collection <i>%s</i> renamed to <i>%s</i>", source, target)
        self.log.debug("Collection '%s' renamed from '%s' to '%s'", cid, source, target)
        self.save()
