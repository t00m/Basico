#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_srv.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Service class
"""

import sys
import logging
import traceback as tb

from gi.repository import GObject

from basico.core.env import FILE



class Service(GObject.GObject):
    """
    Service class is the base class for those modules acting as services.
    Different modules (GUI, Database, Ask, etc...) share same methods
    which is useful to start/stop them, simplify logging and, comunicate
    each other easily.
    """

    def __init__(self, app=None):
        """Initialize Service instance
        @type app: Basico instance
        @param app: current Basico instance reference
        """
        GObject.GObject.__init__(self)

        if app is not None:
            self.app = app

        self.started = False

    def is_started(self):
        """Return True or False if service is running / not running
        """
        return self.started

    def print_traceback(self):
        self.log.error(tb.format_exc())

    def start(self, app, name, section_name):
        """
        Configure and Start a service
        Use 'initialize' for writinga custom init method
        """
        self.started = True
        self.app = app
        self.section = section_name
        self.log = logging.getLogger(name)
        self.log.addHandler(self.app.intercepter)
        self.init_section(section_name)
        self.get_services()
        try:
            self.initialize()
        except Exception as error:
            self.log.debug (self.get_traceback())
        self.log.debug("Service '%s' started" , name)

    def end(self):
        """
        End service
        Use 'finalize' for writting a custom end method
        """
        self.started = False
        try:
            self.finalize()
        except Exception as error:
            self.log.debug (self.get_traceback())

    def initialize(self):
        """Initialize service.
        All clases derived from Service class can implement this method
        """
        pass

    def finalize(self):
        """Finalize service.
        All clases derived from Service class can implement this method
        """
        pass

    def init_section(self, section):
        """Check if section exists in config. If not, create it"""
        self.srvstg = self.get_service('Settings')
        config = self.srvstg.get_config()
        try:
            config[section]
        except:
            config[section] = {}
            self.srvstg.save(config)
            self.log.debug("Section '%s' initialized in config file" % section)

    def get_traceback(self):
        """
        get traceback
        """
        return tb.format_exc()

    def get_services(self):
        pass

    def get_service(self, name):
        return self.app.get_service(name)

    def get_config(self):
        self.srvstg = self.get_service('Settings')
        return self.srvstg.load()

    def get_splash(self):
        return self.app.get_splash()

    def set_config_value(self, key, value):
        self.srvstg.set_value(self.section, key, value)

    def get_config_value(self, key):
        return self.srvstg.get_value(self.section, key)
