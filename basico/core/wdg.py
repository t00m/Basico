#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_wdg.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Basico Widget Base class
"""

import logging
import traceback as tb

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class BasicoWidget(object):
    """Service class is the base class for Basico widgets"""
    app = None
    log = None
    name = None
    section = None

    def __init__(self, app, name):
        """Initialize Service instance"""
        self.app = app
        self.name = name
        self.log = logging.getLogger(name)
        self.log.addHandler(self.app.intercepter)
        self.srvstg = self.get_service('Settings')
        self.__init_section(name)
        self.log.debug("Loading widget: %s", name)

    def get_traceback(self):
        """Get traceback"""
        return tb.format_exc()

    def get_service(self, name):
        """Get a service"""
        return self.app.get_service(name)

    def __init_section(self, name):
        """Check if section exists in config. If not, create it"""
        self.section = 'Widget#%s' % name
        config = self.srvstg.load()

        try:
            config[self.section]
        except:
            config[self.section] = {}
            self.srvstg.save(config)
            self.log.debug("Section '%s' initialized in config file" % name)

    def get_section_name(self):
        return self.name

    def set_config_value(self, key, value):
        self.srvstg.set_value(self.section, key, value)

    def get_config_value(self, key):
        return self.srvstg.get_value(self.section, key)
