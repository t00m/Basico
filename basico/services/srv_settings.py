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

from basico.core.mod_srv import Service
from basico.core.mod_env import FILE

#COMMENT Default settings for SAP module
#COMMENT LOGIN_PAGE_URL = "https://accounts.sap.com"
#COMMENT LOGOUT_PAGE_URL = "https://accounts.sap.com/ui/logout"
#COMMENT ODATA_NOTE_URL = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')" #$expand=LongText" #?$expand=LongText,RefTo,RefBy"
#COMMENT SAP_NOTE_URL = "https://launchpad.support.sap.com/#/notes/%s"
#COMMENT SAP_NOTE_URL_PDF = "https://launchpad.support.sap.com/services/pdf/notes/%s/E"
#COMMENT TIMEOUT = 5


class Settings(Service):
    def initialize(self):
        self.log.debug("Basico config file: %s" % FILE['CNF'])
        config = self.load()


    def get(self, section, key):
        config = self.load()
        try:
            return config[section][key]            
        except Exception as error:
            self.log.error(error)
            return None


    def set(self, section, key, value):
        config = self.load()
        try:
            config[section][key] = value
            self.log.debug("[%s][%s] = %s" % (section, key, value))
            self.save(config)            
        except:
            self.log.error("Setting not saved")
            self.log.error(self.get_traceback())


    def load(self):
        try:
            with open(FILE['CNF'], 'r') as fp:
                config = json.load(fp)
        except Exception as error:
            self.log.debug("Config file not found. Creating a new one")
            config = {}
            self.save(config)

        return config


    def save(self, config=None):
        if config is None:
            self.log.error("A dictionary with all settings must be provided")
            return
        with open(FILE['CNF'], 'w') as fp:
            json.dump(config, fp)
        self.log.debug("Settings saved successfully")
