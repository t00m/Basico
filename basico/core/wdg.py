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
        self._get_services()
        self.get_services()
        self._setup_widget()
        self.log.debug("Widget '%s' initialized", name)
        self.setup_widget()
        self.log.debug("Widget '%s' configured", name)

    def _get_services(self):
        """ Services loaded by default"""
        self.srvgui = self.app.get_service('GUI')
        self.srvuif = self.app.get_service('UIF')

    def __init_section(self, name):
        """Check if section exists in config. If not, create it"""
        self.section = 'Widget#%s' % name
        config = self.srvstg.get_config()
        try:
            config[self.section]
        except:
            config[self.section] = {}
            self.srvstg.save(config)
            self.log.debug("Section '%s' initialized in config file" % name)

    def _setup_widget(self):
        """Widget initialization"""
        pass

    def setup_widget(self):
        """Widget post-initialization"""
        pass

    def get_services(self):
        """ Services loaded on demand"""
        pass

    def get_traceback(self):
        """Get traceback"""
        return tb.format_exc()

    def get_service(self, name):
        """Get a service"""
        return self.app.get_service(name)

    def get_section_name(self):
        return self.name

    def set_config_value(self, key, value):
        self.srvstg.set_value(self.section, key, value)

    def get_config_value(self, key):
        return self.srvstg.get_value(self.section, key)
