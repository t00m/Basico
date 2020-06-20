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
levels = {
            10: 'DEBUG',
            20: 'INFO',
            30: 'WARNING',
            40: 'ERROR',
            50: 'CRITICAL'
        }


class LogIntercepter(logging.Handler):
    def emit(self, record):
        """Send the log records (created by loggers) to
        the appropriate destination.
        """
        queue_log.put(record)
        event_log.append(record)

logging.basicConfig(level=logging.DEBUG, format="%(levelname)7s | %(lineno)4d  |%(name)-25s | %(asctime)s | %(message)s")

def get_logger(name):
    """Returns a new logger with personalized.
    @param name: logger name
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)7s | %(lineno)4d  |%(name)-25s | %(asctime)s | %(message)s")
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    # ~ formatter = logging.Formatter("%(levelname)7s | %(lineno)4d  |%(name)-25s | %(asctime)s | %(message)s")
    # ~ fh = logging.FileHandler(FILE['LOG'])
    # ~ fh.setFormatter(formatter)
    # ~ fh.setLevel(logging.DEBUG)
    # ~ log.addHandler(fh)

    # ~ formatter = logging.Formatter("%(asctime)s | %(message)s")
    # ~ fe = logging.FileHandler(FILE['EVENTS'])
    # ~ fe.setFormatter(formatter)
    # ~ fe.setLevel(logging.INFO)
    # ~ log.addHandler(fe)

    return log
