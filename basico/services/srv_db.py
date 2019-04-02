#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_db.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Database service
"""

import os
from os.path import basename
import json
import glob
from html import escape

from basico.core.mod_env import LPATH, FILE
from basico.core.mod_srv import Service
from basico.services.srv_cols import COL_DOWNLOADED

SEP = os.path.sep

class Database(Service):
    def initialize(self):
        '''
        Setup AppLogic Service
        '''
        self.sapnotes = {}
        self.stats = {}
        self.stats['maincomp'] = {}
        self.stats['cats'] = {}
        self.stats['component'] = set()
        self.stats['category'] = set()
        self.stats['priority'] = set()
        self.stats['type'] = set()
        self.stats['version'] = set()
        self.__init_config_section()
        self.get_services()
        self.load_notes()


    def __init_config_section(self):
        settings = self.srvstg.load()
        settings[self.section]
        try:
            settings[self.section]['DBSAP']
        except:
            settings[self.section]['DBSAP'] = FILE['DBSAP']
        self.srvstg.save(settings)
        

    def get_services(self):
        self.srvclt = self.get_service('Collections')

    def store(self, sapnote, html):
        FSAPNOTE = LPATH['CACHE_XML'] + sapnote + '.xml'

        try:
            f = open(FSAPNOTE, 'w')
            f.write(html)
            f.close()
            self.log.debug("SAP Note %s in XML format stored in %s" % (sapnote, FSAPNOTE))
        except Exception as error:
            self.log.error(error)


    def get_sapnote_content(self, sid):
        FSAPNOTE = LPATH['CACHE_XML'] + sid + '.xml'
        content = open(FSAPNOTE, 'r').read()
        return content


    def is_saved(self, sid):
        metadata = self.get_sapnote_metadata(sid)
        if metadata is None:
            return False
        else:
            return True


    def is_valid(self, sid):
        valid = True
        for ch in sid:
            if not ch.isdigit():
                return False
        return valid


    def is_stored(self, sid):
        fsapnote = LPATH['CACHE_XML'] + sid + '.xml'
        stored = os.path.exists(fsapnote)

        return stored


    def build_stats(self, bag=None):
        if bag is None:
            bag = self.sapnotes
        self.dstats = {}
        self.compstats = {}
        allcollections = set()

        for sid in bag:
            try:
                collections = self.sapnotes[sid]['collections']
                for collection in collections:
                    allcollections.add(collection)
            except: pass

            #COMMENT Components
            compkey = self.sapnotes[sid]['componentkey']
            comptxt = self.sapnotes[sid]['componenttxt']
            component = escape("%s (%s)" % (compkey, comptxt))
            sep = compkey.find('-')
            if sep > 0:
                maincomp = compkey[0:sep]
            else:
                maincomp = compkey

            #COMMENT Categories
            category = escape(self.sapnotes[sid]['category'])
            try:
                cont = self.stats['cats'][category]
                self.stats['cats'][category] = cont + 1
            except:
                self.stats['cats'][category] = 1

            #COMMENT Build all (sub)keys from given component key
            #COMMENT useful for display stats with pygal
            compkeys = compkey.split('-')
            total = len(compkeys)
            key = ''
            i = 0
            for subkey in compkeys:
                key = key + '-' + subkey
                if key[:1] == '-':
                    key = key[1:]

                # update stats
                try:
                    count = self.compstats[key]
                    self.compstats[key] = count + 1
                except Exception as error:
                    self.compstats[key] = 1

            try:
                cont = self.stats['maincomp'][maincomp]
                self.stats['maincomp'][maincomp] = cont + 1
            except:
                self.stats['maincomp'][maincomp] = 1

            category = escape(self.sapnotes[sid]['category'])
            priority = escape(self.sapnotes[sid]['priority'])
            ntype = escape(self.sapnotes[sid]['type'])
            version = escape(self.sapnotes[sid]['version'])
            releaseon = escape(self.sapnotes[sid]['releasedon'])
            self.stats['component'].add(component)
            self.stats['category'].add(category)
            self.stats['priority'].add(priority)
            self.stats['type'].add(ntype)
            self.stats['version'].add(version)
            #FIXME self.stats['releaseon'].add(releasedon)
            #FIXME self.stats[''].add(version)


    def add(self, sapnote, overwrite=False, batch=False):
        sid = sapnote['id']

        if self.exists(sid):
            if overwrite:
                self.sapnotes[sid] = sapnote
                self.log.info("SAP Note %s added to database (Overwrite is %s)", sid, overwrite)
                if batch is False:
                    self.save_notes()
                return True
            else:
                self.log.info("SAP Note %s already exists in database (Overwrite is %s)", sid, overwrite)
                return False
        else:
            self.sapnotes[sid] = sapnote
            self.log.info("SAP Note %s added to database (Overwrite is %s)", sid, overwrite)
            if batch is False:
                self.save_notes()
            return True


    def add_list(self, sapnotes, overwrite=False):
        self.log.info("Add %d SAP Notes to database (Overwrite is %s)", len(sapnotes), overwrite)
        n = 0
        for sid in sapnotes:
            if overwrite:
                if self.add(sapnotes[sid], overwrite, batch=True):
                    n += 1
        self.save_notes()
        return n
        

    def get_notes(self):
        '''
        Return all sapnotes
        '''
        return self.sapnotes


    def get_notes_by_node(self, key, value):
        '''
        Return a set of sapnotes which matches with an specific key/value
        '''
        bag = set()
        sapnotes = self.get_notes()
        for sapnote in sapnotes:
            if key.startswith('component') or \
               key in ['category', 'priority', 'type']:
                if sapnotes[sapnote][key].startswith(value):
                    bag.add(sapnote)
            elif key == 'collection':
                try:
                    collections = sapnotes[sapnote]['collections']
                    if value == 'None':
                        if len(collections) == 0:
                            bag.add(sapnote)
                    else:
                        if value in collections:
                            bag.add(sapnote)
                except:
                    pass
            elif key in ['date-year', 'date-month', 'date-day']:
                if len(value) == 6:
                    value = value[0:4] + '-' + value[4:6]
                elif len(value) == 8:
                    value = value[0:4] + '-' + value[4:6] + '-' + value[6:8]

                if sapnotes[sapnote]['feedupdate'].startswith(value):
                    bag.add(sapnote)
            else:
                pass

        return bag


    def get_total(self):
        '''
        Return total sapnotes
        '''
        return len(self.sapnotes)


    def load_notes(self):
        '''
        If notes.json exists, load notes
        '''
        try:
            with open(FILE['DBSAP'], 'r') as fp:
                self.sapnotes = json.load(fp)
                self.log.info("SAP Notes Database found at: %s", FILE['DBSAP'])
                self.log.info("Loaded %d notes from SAP Notes database" % len(self.sapnotes))
        except Exception as error:
            self.save_notes()
            self.log.info("SAP Notes database not found. Created a new database for SAP Notes")


    def get_sapnote_metadata(self, sid):
        sid = self.normalize_sid(sid)

        try:
            return self.sapnotes[sid]
        except KeyError as error:
            # ~ self.log.debug("SAP Note %s doesn't exist in the database or it's been deleted" % sid)
            return None


    def exists(self, sid):
        sid = self.normalize_sid(sid)
        metadata = self.get_sapnote_metadata(sid)
        if metadata is not None:
            return True
        else:
            return False

    def get_title(self, sid):
        title = ''
        metadata = self.get_sapnote_metadata(sid)
        if metadata is not None:
            title = metadata['title']

        return title


    def get_component(self, sid):
        component = ''
        metadata = self.get_sapnote_metadata(sid)
        if metadata is not None:
            component = metadata['component-key']

        return component


    def save_notes(self):
        '''
        Save SAP Notes to json database file
        '''

        bag = self.get_notes()

        try:
            with open(FILE['DBSAP'], 'w') as fdb:
                json.dump(bag, fdb)
                self.log.debug ("Saved %d notes to %s" % (len(bag), FILE['DBSAP']))
        except Exception as error:
            self.log.error(error)


    def set_bookmark(self, lsid):
        for sid in lsid:
            sid = self.normalize_sid(sid)
            self.sapnotes[sid]['bookmark'] = True
            self.log.info("SAP Note %s bookmarked: True" % sid)
        self.save_notes()


    def set_no_bookmark(self, lsid):
        for sid in lsid:
            sid = self.normalize_sid(sid)
            self.sapnotes[sid]['bookmark'] = False
            self.log.info("SAP Note %s bookmarked: False" % sid)
        self.save_notes()


    def is_bookmark(self, sapnote):
        try:
            return self.sapnotes[sapnote]['bookmark']
        except:
            return False

    def get_collections(self, sid):
        try:
            return self.sapnotes[sid]['collections']
        except:
            return []


    def get_stats(self):
        return self.stats


    def search(self, term):
        bag = []

        for sid in self.get_notes():
            values = []
            sapnote = self.sapnotes[sid]
            for key in sapnote:
                values.append(str(sapnote[key]))
            text = ' '.join(values)
            if term.upper() in text.upper():
                bag.append(sapnote['id'])
        self.log.debug("Found term '%s' in %d SAP Notes" % (term, len(bag)))
        return bag


    def normalize_sid(self, sid):
        if isinstance(sid, int):
            sid = "0"*(10 - len(str(sid))) + str(sid)
        elif isinstance(sid, str):
            sid = "0"*(10 - len(sid)) + sid

        return sid


    def set_collections(self, sid, collections, overwrite=False):
        sid = self.normalize_sid(sid)
        self.log.info("SAP Note %s added to the following collections (overwrite mode is %s):", sid, overwrite)
        if sid != '0000000000':
            sid = self.normalize_sid(sid)
            try:
                if overwrite:
                    new_cols = []
                    self.sapnotes[sid]['collections'] = collections
                    for cid in collections:
                        if cid == COL_DOWNLOADED:
                            continue
                        if cid not in new_cols:
                            new_cols.append(cid)
                            self.log.info("\tCollection: %s", self.srvclt.get_name_by_cid(cid)) 
                else:
                    current_collections = self.sapnotes[sid]['collections']
                    current_collections.extend(collections)
                    bag = []
                    for cid in current_collections:
                        if cid == COL_DOWNLOADED:
                            continue
                        if cid not in bag:
                            bag.append(cid)
                            self.log.info("\tCollection: %s", self.srvclt.get_name_by_cid(cid)) 
                    self.sapnotes[sid]['collections'] = bag
                self.save_notes()
            except:
                self.log.error(error)
 

    def delete(self, sid):
        sid = self.normalize_sid(sid)
        deleted = False
        try:
            del (self.sapnotes[sid])
            deleted = True
            self.log.info("SAP Note %s deleted" % sid)
            self.save_notes()
        except Exception as error:
            self.log.debug(error)
            deleted = False

        return deleted


    def end(self):
        self.save_notes()

