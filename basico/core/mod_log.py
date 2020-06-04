#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_log.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: log module
"""

import queue
import logging

queue_log = queue.Queue()
event_log = []

class LogIntercepter(logging.Handler):
    def emit(self, record):
        """Send the log records (created by loggers) to
        the appropriate destination.
        """
        # ~ print("--> %s" % record.getMessage())
        global queue_log
        queue_log.put(record)
        event_log.append(record)
