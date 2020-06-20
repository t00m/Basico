#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: kb4it.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: KB4IT Service
"""

import time
import queue
import threading
from enum import IntEnum
from argparse import Namespace

from gi.repository import GObject

from kb4it.kb4it import KB4IT
from kb4it.core.util import copydir

from basico.core.env import LPATH, GPATH, FILE
from basico.core.srv import Service
from basico.core.log import levels

class KBStatus(IntEnum):
    UPTODATE = 0 # Basico KB updated
    UPDATING = 1 # Basico KB is being updated

class KB4Basico(Service):
    kb = None
    th = None
    queue = None
    params = None
    status = KBStatus.UPTODATE

    def initialize(self):
        # Install "KB Updated" signal
        GObject.signal_new('kb-updated', KB4Basico, GObject.SignalFlags.RUN_LAST, None, () )

        # Get KB4IT version
        self.log.debug("Basico is using %s" % KB4IT().get_version())

        # Start listening to requests
        self.queue = queue.Queue()
        self.th = threading.Thread(name='update', target=self.update)
        self.th.setDaemon(True)
        self.th.start()
        self.log.debug("KB Basico Manager started")

    def prepare(self):
        self.log.debug("Preparing request")

        force = self.get_config_value('force') or False
        self.log.debug("\tCompilation is set to: %s", force)

        # FIXME: Get all settings
        loglevel = levels[self.app.log.getEffectiveLevel()]
        self.log.debug("\tFIXME: Log level for KB4IT: %s", loglevel)
        params = Namespace(FORCE=force, LOGLEVEL=loglevel, SORT_ATTRIBUTE=None, SOURCE_PATH=LPATH['DOC_SOURCE'], TARGET_PATH=LPATH['DOC_TARGET'], THEME=None)

        # Make sure the last theme version is installed
        self.log.debug("\tInstalling KB4IT Basico theme")
        copydir(GPATH['KB4IT'], LPATH['DOC_SOURCE'])

        # Get KB4IT Basico theme properties
        kb = KB4IT(params)
        kbapp = kb.get_service('App')
        kbapp.load_theme()
        theme = kbapp.get_theme_properties()
        installed = theme['id'] == 'basico'
        if not installed:
            self.log.error("\tKB4IT Theme for Basico not found. Using default theme :(")
        else:
            self.log.info("\tBasico KB4IT Theme %s found", theme['version'])

        self.status = KBStatus.UPDATING

        return kb

    def request_update(self):
        self.log.info("Basico KB update requested")
        self.queue.put('request')

    def update(self):
        while self.status == KBStatus.UPTODATE:
            self.queue.get()
            kb = self.prepare()
            kb.run()
            self.queue.task_done()
            if self.queue.empty():
                self.status = KBStatus.UPTODATE
                self.log.info("Basico KB up to date")
                self.emit('kb-updated')
            time.sleep(1)

    def get_status(self):
        return self.status

