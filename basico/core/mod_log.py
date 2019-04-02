#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_log.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: log module
"""

from os.path import sep as SEP
import logging
import inspect

from basico.core.mod_env import FILE

def get_logger(name):
    """Returns a new logger with personalized.
    @param name: logger name
    """
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)7s | %(lineno)4d  |%(name)-25s | %(asctime)s | %(message)s")
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(levelname)7s | %(lineno)4d  |%(name)-25s | %(asctime)s | %(message)s")
    fh = logging.FileHandler(FILE['LOG']) 
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)

    formatter = logging.Formatter("%(asctime)s | %(message)s")
    fe = logging.FileHandler(FILE['EVENTS']) 
    fe.setFormatter(formatter)
    fe.setLevel(logging.INFO)
    log.addHandler(fe)
    
    return log
