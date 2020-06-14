#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: kb4it.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: KB4IT Service
"""

import queue
import threading
from enum import IntEnum
from argparse import Namespace

from gi.repository import GObject

from kb4it.kb4it import KB4IT
from kb4it.core.util import copydir

from basico.core.env import LPATH, GPATH, FILE
from basico.core.srv import Service

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

        # Make sure the last theme version is installed
        self.params = Namespace(FORCE=True, LOGLEVEL='INFO', SORT_ATTRIBUTE=None, SOURCE_PATH=LPATH['DOC_SOURCE'], TARGET_PATH=LPATH['DOC_TARGET'], THEME=None)
        self.install_theme()

        # Get KB4IT Basico theme properties
        self.kb = KB4IT(self.params)
        kbapp = self.kb.get_service('App')
        theme = kbapp.get_theme_properties()
        installed = theme['id'] == 'basico'
        if not installed:
            self.log.error("KB4IT Theme for Basico not found. Using default theme :(")
        else:
            self.log.info("Basico KB4IT Theme %s found", theme['version'])

        # Update KB target
        self.queue = queue.Queue()
        self.th = threading.Thread(name='update', target=self.update)
        self.th.setDaemon(True)
        self.th.start()
        self.log.debug("KB Basico Manager started")
        self.request_update()

    def install_theme(self):
        self.log.debug("Installing KB4IT Basico theme")
        copydir(GPATH['KB4IT'], LPATH['DOC_SOURCE'])
        self.kb = KB4IT(self.params)
        kbapp = self.kb.get_service('App')
        theme = kbapp.get_theme_properties()
        return theme

    def request_update(self):
        self.log.info("Basico KB update requested")
        self.queue.put('request')

    def update(self):
        while True:
            self.queue.get()
            self.kb.run()
            self.queue.task_done()
            if self.queue.empty():
                self.log.info("Basico KB updated")
                self.emit('kb-updated')


