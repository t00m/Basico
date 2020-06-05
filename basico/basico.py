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
from basico.core.mod_env import APP, LPATH, GPATH, FILE
from basico.core.mod_log import LogIntercepter, queue_log
from basico.services.srv_utils import Utils
from basico.services.srv_gui import GUI
from basico.services.srv_iconmgt import IconManager
from basico.services.srv_bnr import BackupRestoreMan
from basico.services.srv_sap import SAP
from basico.services.srv_settings import Settings
from basico.services.srv_uif import UIFuncs
from basico.services.srv_callbacks import Callback
from basico.services.srv_notify import Notification
from basico.services.srv_database import Database
from basico.services.srv_download import DownloadManager
from basico.services.srv_collections import Collections
from basico.services.srv_annotations import Annotation
from basico.services.srv_attachment import Attachment
from basico.services.srv_notify import Notification
from basico.services.srv_asciidoctor import Asciidoctor
from basico.widgets.wdg_splash import Splash


logging.basicConfig(level=logging.DEBUG, format="%(levelname)7s | %(lineno)4d  |%(name)-25s | %(asctime)s | %(message)s")

#DOC: http://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
signal.signal(signal.SIGINT, signal.SIG_DFL)

class Basico(object):
    """
    Basico Application class
    """
    intercepter = LogIntercepter()

    def __init__(self):
        """
        Basico class
        """

        self.setup_environment()
        self.setup_logging()
        self.setup_services()
        self.setup_splash()
        self.setup_post()


    def get_splash(self):
        return self.splash


    def setup_splash(self):
        self.splash = Splash(title="Basico\n0.4", font='Roboto Slab 24', font_weight='bold', font_color="#FFFFFF", background_image=FILE['SPLASH'], app=self)


    def setup_environment(self):
        """
        Setup Basico environment
        """
        # Create local paths if they do not exist
        for entry in LPATH:
            if not os.path.exists(LPATH[entry]):
                os.makedirs(LPATH[entry])


    def setup_logging(self):
        """
        Setup Basico logging
        """
        # Truncate existing log file
        if os.path.exists(FILE['LOG']):
            with open(FILE['LOG'], 'w') as flog:
                pass

        #Initialize logging
        self.log = logging.getLogger(__class__.__name__)
        self.log.addHandler(self.intercepter)
        self.log.info("Basico %s started", APP['version'])
        self.log.debug("Global path: %s", GPATH['ROOT'])
        self.log.debug("Local path: %s", LPATH['ROOT'])
        self.log.debug("Logging all messages to file: %s", FILE['LOG'])
        self.log.debug("Logging only events: %s", FILE['EVENTS'])


    def setup_services(self):
        """
        Setup Basico Services
        """

        # Declare and register services
        self.services = {}
        try:
            services = {
                'GUI'           :   GUI(),
                'Utils'         :   Utils(),
                'UIF'           :   UIFuncs(),
                'SAP'           :   SAP(),
                'Settings'      :   Settings(),
                # ~ 'Notify'        :   Notification(),
                'IM'            :   IconManager(),
                'Callbacks'     :   Callback(),
                'DB'            :   Database(),
                'Driver'        :   DownloadManager(),
                'Collections'   :   Collections(),
                # ~ 'Annotation'    :   Annotation(),
                # ~ 'Attachment'    :   Attachment(),
                # ~ 'BNR'           :   BackupRestoreMan(),
                # ~ 'Notify'        :   Notification(),
                # ~ 'Asciidoctor'   :   Asciidoctor(),
            }

            for name in services:
                self.register_service(name, services[name])
        except Exception as error:
            self.log.error(error)
            raise


    def setup_post(self):
        # Patch Selenium 4
        FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_TARGET'] = os.path.join(os.path.dirname(selenium.__file__), 'webdriver/firefox/webdriver_prefs.json')
        if not os.path.exists(FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_TARGET']):
            try:
                shutil.copy(FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_SOURCE'], FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_TARGET'])
                self.log.debug("Webdriver preferences config file not found. Python Selenium libs patched locally")
            except:
                self.log.warning("Firefox Webdriver preferences not found in: ")
                self.log.warning(FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_TARGET'])
                self.log.warning("Copied missing file from: ")
                self.log.warning(FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_SOURCE'])

        if not os.path.exists(FILE['L_SAP_PRODUCTS']):
            shutil.copy(FILE['G_SAP_PRODUCTS'], FILE['L_SAP_PRODUCTS'])
            self.log.debug("SAP Products file copied to local database resources directory")


    def get_service(self, name):
        """
        Get/Start a registered service
        """
        try:
            service = self.services[name]
            logname = service.__class__.__name__
            if not service.is_started():
                service.start(self, logname, name)
            return service
        except KeyError as service:
            self.log.error("Service %s not registered or not found", service)
            raise


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
        self.services[name].end()
        self.services[name] = None


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
        # ~ self.srvclb = self.get_service('Callbacks')
        # ~ GLib.timeout_add(500, self.srvclb.update_statusbar)
        GUI.run()


def main():
    """
    Entry point
    """
    basico = Basico()
    basico.run()
