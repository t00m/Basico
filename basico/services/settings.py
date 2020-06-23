#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_settings.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Settings service
"""


from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango
from gi.repository.GdkPixbuf import Pixbuf

import json

from basico.core.srv import Service
from basico.core.env import FILE

class Settings(Service):
    """
    Settings management service for Basico
    TODO: do not save a setting if the same is already in the settings database
    TODO: enqueue settings to be saved, so the service is not all the time accessing to disk
    """
    config = None

    def initialize(self):
        self.log.debug("Basico config file: %s" % FILE['CNF'])
        self.load()

    def load(self):
        """Load settings database. If it doesn't exist, create it"""
        try:
            with open(FILE['CNF'], 'r') as fp:
                self.config = json.load(fp)
        except Exception as error:
            self.log.debug("Config file not found. Creating a new one")
            self.config = {}
            self.save()

    def save(self, config=None):
        """Save settings database"""
        with open(FILE['CNF'], 'w') as fp:
            if config is not None:
                self.config = config
            json.dump(self.config, fp)

    def get_config(self):
        """Get database settings"""
        if self.config is None:
            self.load()
        return self.config

    def set_value(self, section, key, value):
        """Set value for a key in a given section"""
        try:
            self.config[section][key] = value
            self.log.debug("[%s][%s] = %s" % (section, key, value))
            self.save()
        except:
            self.log.error("Setting not saved")
            self.log.error(self.get_traceback())

    def get_value(self, section, key):
        """Get value for a key in a given section"""
        try:
            return self.config[section][key]
        except Exception as error:
            self.log.warning("[%s][%s] Value not found!" % (section, key))
            return None
