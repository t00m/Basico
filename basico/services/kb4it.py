#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: kb4it.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: KB4IT Service
"""

import os
import glob
import time
import queue
import shutil
import threading
from enum import IntEnum
from pathlib import Path
from argparse import Namespace

from gi.repository import GObject

from kb4it.kb4it import KB4IT
from kb4it.core.util import copydir

from basico.core.env import LPATH, GPATH, FILE
from basico.core.srv import Service
from basico.core.log import levels

class KB4Basico(Service):
    kb = None
    th = None
    queue = None
    params = None
    forced = False

    def initialize(self):
        # Install "KB Updated" signal
        GObject.signal_new('kb-updated', KB4Basico, GObject.SignalFlags.RUN_LAST, None, () )

        # Get KB4IT version
        self.log.debug("Basico is using %s" % KB4IT().get_version())

        # Clean KB4IT temporary folder
        shutil.rmtree(LPATH['TMP'])
        os.makedirs(LPATH['TMP'])
        self.log.debug("KB4IT temporary directory recreated")

        # Check settings / Initialize
        source_path = self.get_config_value('source_dir')
        if source_path is None:
            self.set_config_value('source_dir', LPATH['DOC_SOURCE'])

        target_path = self.get_config_value('target_dir')
        if target_path is None:
            self.set_config_value('target_dir', LPATH['DOC_TARGET'])

        force = self.get_config_value('force')
        if force is None:
            self.set_config_value('force', False)

        # Start listening to requests
        self.queue = queue.Queue()
        self.th = threading.Thread(name='update', target=self.update_kb)
        self.th.setDaemon(True)
        self.th.start()
        self.log.debug("KB Basico Manager started")

    def finalize(self):
        # Clean KB4IT temporary folder
        shutil.rmtree(LPATH['TMP'])
        # ~ os.makedirs(LPATH['TMP'])
        self.log.debug("KB4IT temporary directory deleted")

    def prepare(self):
        self.log.debug("Preparing request")
        # NO RESET ALLOWED HERE
        reset = False

        # Force compilation?
        force = self.get_config_value('force') or False
        self.log.debug("Force compilation is set to: %s", force)

        # Log level as plain text
        loglevel = levels[self.log.getEffectiveLevel()]

        # Get source directory
        source_path = self.get_config_value('source_dir') or LPATH['DOC_SOURCE']
        self.log.debug("[KB] Source path set to: %s", source_path)

        # Get target directory
        target_path = self.get_config_value('target_dir') or LPATH['DOC_TARGET']
        self.log.debug("[KB] Target path set to: %s", target_path)

        # Build KB4IT params
        params = Namespace(RESET=reset, FORCE=force, LOGLEVEL=loglevel, SORT_ATTRIBUTE='releasedon', SOURCE_PATH=source_path, TARGET_PATH=target_path, THEME=None)

        # Make sure the last theme version is installed
        self.log.debug("[KB] Installing KB4IT Basico theme")
        copydir(GPATH['KB4IT'], source_path)

        return params


    def request_update(self, forced=False):
        self.log.info("[KB] Update requested")
        self.queue.put('request')

    def is_running(self):
        try:
            self.running = kb.is_running() or False
        except:
            self.running = False
        return self.running

    def update_kb(self):
        running = self.is_running()
        while not running:
            self.queue.get()
            self.log.info("[KB] Executing update")
            # Get params
            params = self.prepare()

            # Get KB4IT instance
            kb = KB4IT(params)
            kbapp = kb.get_service('App')

            # Get KB4IT Basico theme properties
            kbapp.load_theme()
            theme = kbapp.get_theme_properties()
            installed = theme['id'] == 'basico'
            if not installed:
                self.log.error("[KB] KB4IT Theme for Basico not found. Using default theme :(")
            else:
                self.log.info("[KB] Basico KB4IT Theme %s found", theme['version'])

            # Update sources
            self.update_sources()

            kb.run()
            self.queue.task_done()
            if self.queue.empty():
                self.log.info("[KB] KB up to date")
                self.emit('kb-updated')
            time.sleep(1)
            running = self.is_running()
        time.sleep(1)

    def update_sources(self):
        srvdtb = self.get_service('DB')
        source_path = self.get_config_value('source_dir')
        db = srvdtb.get_notes()
        for sid in db:
            filename = os.path.join(source_path, '%s.adoc' % sid)
            with open(filename, 'w') as fadoc:
                fadoc.write("= %s\n\n" % db[sid]['title'])
                for p in db[sid]:
                    if p != 'id':
                        fadoc.write(":%s: %s\n" % (p, db[sid][p]))
                fadoc.write("\n// END-OF-HEADER. DO NOT MODIFY OR DELETE THIS LINE\n")

    def delete_document(self, adocs):
        params = self.prepare()
        kb = KB4IT(params)
        kbapp = kb.get_service('App')
        for adoc in adocs:
            kbapp.delete_document(adoc)
        self.request_update()

    def reset(self):
        self.log.debug("[KB] Executing reset")
        # Log level
        loglevel = levels[self.log.getEffectiveLevel()]

        # Get sources directory
        source_path = self.get_config_value('source_dir') or LPATH['DOC_SOURCE']
        self.log.debug("[KB] Source path set to: %s", source_path)

        # Get sources directory
        target_path = self.get_config_value('target_dir') or LPATH['DOC_TARGET']
        self.log.debug("[KB] Target path set to: %s", target_path)

        # Execute KB reset operation
        params = Namespace(RESET=True, FORCE=True, LOGLEVEL=loglevel, SORT_ATTRIBUTE=None, SOURCE_PATH=source_path, TARGET_PATH=target_path, THEME=None)
        kb = KB4IT(params)
        kbapp = kb.get_service('App')
        kb.run()

        # Then, KB diff update
        self.request_update()

        self.log.info("[KB] Reset finished")
