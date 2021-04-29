#!/usr/bin/python 3
# -*- coding: utf-8 -*-
"""
# File: basico.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Main entry point por Basico app
"""

import os
import sys
import signal
import shutil
import queue
import logging

import selenium

from gi.repository import GLib
from gi.repository import GObject

from yapsy.PluginManager import PluginManager

from basico.core.env import APP, LPATH, GPATH, FILE
from basico.core.log import LogIntercepter, queue_log, get_logger

# ~ from basico.services.kb4it import KB4Basico
from basico.services.util import Utils
from basico.services.gui import GUI
from basico.services.icons import IconManager
from basico.services.sap import SAP
from basico.services.settings import Settings
from basico.services.uif import UIFuncs
from basico.services.callbacks import Callback
from basico.services.database import Database
from basico.services.notify import Notify
from basico.services.plugins import Plugins

# ~ from basico.services.download import DownloadManager
from basico.services.collections import Collections
from basico.widgets.splash import Splash


logging.basicConfig(level=logging.INFO, format="%(levelname)7s | %(lineno)4d  |%(name)25s | %(asctime)s | %(message)s")

# DOC: http://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
signal.signal(signal.SIGINT, signal.SIG_DFL)

class Basico(object):
    """
    Basico Application class
    """
    plugins = None
    intercepter = LogIntercepter()

    def __init__(self):
        """
        Basico class
        """
        self.setup_logging()
        self.setup_environment()
        self.setup_services()
        self.setup_splash()

    def get_splash(self):
        return self.splash


    def setup_splash(self):
        title = "%s\n%s\n%s" % (APP['short'].title(), APP['name'], APP['version'])
        self.splash = Splash(title=title, font='Roboto Slab 24', font_weight='bold', font_color="#FFFFFF", background_image=FILE['SPLASH'], app=self)

    def setup_environment(self):
        """
        Setup Basico environment
        """
        self.log.debug("Checking directories for Basico")
        for entry in LPATH:
            if not os.path.exists(LPATH[entry]):
                os.makedirs(LPATH[entry])
                self.log.debug("Directory %s created", LPATH[entry])
        self.log.debug("Basico directory structure ok")

        self.log.debug("Global path: %s", GPATH['ROOT'])
        self.log.debug("Local path: %s", LPATH['ROOT'])

    def setup_logging(self):
        """
        Setup Basico logging
        """
        self.log = get_logger(__class__.__name__)
        self.log.addHandler(self.intercepter)
        self.log.info("Basico %s started", APP['version'])

    def setup_services(self):
        """
        Setup Basico Services
        """

        self.log.debug("Declare and register services")
        self.services = {}
        try:
            services = {
                'GUI'           :   GUI(),
                'Utils'         :   Utils(),
                'UIF'           :   UIFuncs(),
                'SAP'           :   SAP(),
                'IM'            :   IconManager(),
                'Callbacks'     :   Callback(),
                'DB'            :   Database(),
                'Notify'        :   Notify(),
                'Collections'   :   Collections()
            }

            self.register_service('Settings', Settings())
            self.get_service('Settings')
            self.register_service('Plugins', Plugins())
            self.plugins = self.get_service('Plugins')
            self.plugins.start(self, 'Plugins', 'Plugins')
            for name in services:
                self.register_service(name, services[name])

        except Exception as error:
            self.log.error(error)
            raise

    def get_service(self, name):
        """
        Get/Start a registered service
        """
        try:
            service = self.services[name]
            logname = service.__class__.__name__
            if service is not None and not service.is_started():
                if self.plugins is not None and name != 'Plugins':
                    service.start(self, logname, name)
            return service
        except KeyError as service:
            self.log.error("Service %s not registered or not found", service)
            raise

    def get_services(self):
        """Get all services registered"""
        return list(self.services.keys())


    def register_service(self, name, service):
        """
        Register a new service
        """
        try:
            self.services[name] = service
        except KeyError as error:
            self.log.error(error)


    def deregister_service(self, name):
        """
        Deregister a running service
        """
        try:
            self.services[name].end()
            self.services[name] = None
        except AttributeError:
            self.log.debug("Service %s was not running!" % name)


    def stop(self):
        """
        For each service registered, it executes the 'end' method
        (if any) to finalize them properly.
        """

        self.splash.show()
        # Deregister all services loaded starting by the GUI service
        self.deregister_service('GUI')
        for name in self.services:
            try:
                if name != 'GUI':
                    self.deregister_service(name)
            except Exception as error:
                self.log.error(error)
                raise
        self.splash.destroy()
        self.log.info("Basico %s finished", APP['version'])


    def run(self):
        """
        Start Basico
        """
        GUI = self.get_service('GUI')
        GUI.run()


def main():
    """
    Entry point
    """
    basico = Basico()
    basico.run()
