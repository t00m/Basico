#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: notify.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: iNotify service
"""

import sys
import logging

from gi.repository import GLib
from gi.repository import GObject

from basico.core.env import GPATH, LPATH
from basico.core.srv import Service


class Notify(Service):
    notify = None

    def initialize(self):
        if sys.platform == 'linux':
            GObject.signal_new('notify-sapnote-new', Notify, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
            import inotify.adapters
            logging.getLogger('inotify.adapters').setLevel(logging.ERROR)
            self.notify = inotify.adapters.Inotify()
            self.notify.add_watch(LPATH['CACHE_XML'])
            GLib.timeout_add(3000, self.watch)
            self.log.debug("Watching DIR: %s" % LPATH['CACHE_XML'])

    def watch(self, *args):
        if self.notify is not None:
            # ~ events = self.notify.event_gen(yield_nones=False, timeout_s=1)
            for event in self.notify.event_gen(yield_nones=False, timeout_s=1):
                    (_, type_names, path, filename) = event
                    if 'IN_CREATE' in type_names:
                        self.log.debug("Added filename: %s", filename)
                        self.emit('notify-sapnote-new', filename)
                    if 'IN_DELETE' in type_names:
                        self.log.debug("Deleted filename: %s", filename)
                    # ~ self.log.debug("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
        return True


  # ~ DEBUG |   38  |Notify          | 2021-04-15 22:45:47,932 | PATH=[/home/t00m/.basico/var/cache/xml] FILENAME=[0000000000.xml] EVENT_TYPES=['IN_CREATE']
  # ~ DEBUG |   38  |Notify          | 2021-04-15 22:45:47,933 | PATH=[/home/t00m/.basico/var/cache/xml] FILENAME=[0000000000.xml] EVENT_TYPES=['IN_OPEN']
  # ~ DEBUG |   38  |Notify          | 2021-04-15 22:45:47,933 | PATH=[/home/t00m/.basico/var/cache/xml] FILENAME=[0000000000.xml] EVENT_TYPES=['IN_ATTRIB']
  # ~ DEBUG |   38  |Notify          | 2021-04-15 22:45:47,934 | PATH=[/home/t00m/.basico/var/cache/xml] FILENAME=[0000000000.xml] EVENT_TYPES=['IN_CLOSE_WRITE']
  # ~ DEBUG |   38  |Notify          | 2021-04-15 22:46:32,970 | PATH=[/home/t00m/.basico/var/cache/xml] FILENAME=[0000000000.xml] EVENT_TYPES=['IN_DELETE']

