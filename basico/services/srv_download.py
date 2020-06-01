#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_driver.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Selenium Driver service
"""

import os
import sys
import time
import glob
import logging
from enum import IntEnum
import threading
import queue
import time
import uuid

from gi.repository import GObject
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as SeleniumService
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from basico.core.mod_env import LPATH, FILE
from basico.core.mod_srv import Service

# Disable logging for imported modules
# Comment to see what is going on behind the scenes
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)

TIMEOUT = 3

class DriverStatus(IntEnum):
    STOPPED = 0 # Webdriver not loaded
    WAITING = 1 # Webdriver loaded. Waiting for a request
    RUNNING = 2 # Webdriver executing a request
    DISABLE = 3 # Webdriver broken!


class DownloadManager(Service):
    queue = queue.Queue()
    requests = {}
    retry = 0
    driver = None
    driver_status = DriverStatus.STOPPED

    def initialize(self):
        GObject.signal_new('download-profile-missing', DownloadManager, GObject.SignalFlags.RUN_LAST, None, () )
        GObject.signal_new('download-complete', DownloadManager, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        threading.Thread(target=self.download, daemon=True).start()
        self.log.debug("Basico Download Manager started")

    def check_profile(self):
        files = glob.glob(os.path.join(LPATH['FIREFOX_PROFILE'], '*'))
        has_profile = len(files) > 0
        self.log.debug("Webdriver profile available? %s", has_profile)
        if not has_profile:
            self.emit('download-profile-missing')
        return has_profile

    def __set_driver(self, driver):
        self.driver = driver

    def get_driver(self):
        return self.driver

    def __set_driver_status(self, status):
        self.driver_status = status

    def get_driver_status(self):
        return self.driver_status

    def get_url_uri(self):
        return self.url_uri

    def get_url_type(self):
        return self.url_type

    def request(self, url_sid, url_uri, url_type):
        has_profile = self.check_profile()
        if not has_profile:
            return

        uuid4 = str(uuid.uuid4())
        rid = uuid4[:uuid4.find('-')]
        self.log.info("[%s] Request created", rid)
        self.requests[rid] = {}
        self.requests[rid]['url_rid'] = rid
        self.requests[rid]['url_sid'] = url_sid
        self.requests[rid]['url_uri'] = url_uri
        self.requests[rid]['url_typ'] = url_type
        self.queue.put(rid)

    def download(self):
        while True:
            rid = self.queue.get()
            url = self.requests[rid]['url_uri']
            self.log.debug("[%s] Request download: %s", rid, url)
            # ~ self.log.debug("[%s] %s", rid, url)
            if self.retry > 2:
                self.__set_driver_status(DriverStatus.DISABLE)

            status = self.get_driver_status()
            self.log.debug("[%s] WebDriver status: %s", rid, status)

            if status == DriverStatus.DISABLE:
                self.log.error("[%s] Webdriver not working anymore", rid)
                return None

            while status == DriverStatus.RUNNING:
                time.sleep(1)
                status = self.get_driver_status()

            if status == DriverStatus.STOPPED:
                try:
                    options = Options()
                    options.profile = LPATH['FIREFOX_PROFILE']
                    options.headless = True
                    # ~ 'security.default_personal_cert'
                    self.log.debug(options.preferences)
                    GDM = GeckoDriverManager(log_level=logging.ERROR)
                    gecko = SeleniumService(executable_path=GDM.install())
                    driver = webdriver.Firefox(options=options, service=gecko)
                    self.__set_driver_status(DriverStatus.WAITING)
                    self.__set_driver(driver)
                    self.log.debug("[%s] Webdriver instance created and ready", rid)
                except Exception as error:
                    self.__set_driver_status(DriverStatus.STOPPED)
                    self.log.error("[%s] Webdriver Error: %s", rid, error)
                    self.retry += 1
                    url_sid = self.requests[rid]['url_sid']
                    url_uri = self.requests[rid]['url_uri']
                    url_type = self.requests[rid]['url_typ']
                    self.request(url_sid, url_uri, url_type)

            status = self.get_driver_status()
            if status == DriverStatus.WAITING:
                self.__set_driver_status(DriverStatus.RUNNING)
                try:
                    driver = self.get_driver()
                    driver.get(url)
                    element_present = EC.presence_of_element_located((By.ID, 'content'))
                    WebDriverWait(driver, TIMEOUT).until(element_present)
                except TimeoutException:
                    self.__set_driver_status(DriverStatus.WAITING)
                except Exception as error:
                    self.log.error(error)
                    self.retry += 1
                    self.__set_driver_status(DriverStatus.STOPPED)
                    self.request(url)
                finally:
                    self.log.debug("[%s] SAP Note %s downloaded", rid, self.requests[rid]['url_sid'])
                    self.retry = 0
                    self.__set_driver_status(DriverStatus.WAITING)
                    self.emit('download-complete', (self.requests[rid]))
            self.queue.task_done()

    def browse(self, url):
        try:
            self.browser.get(url)
        except:
            options = Options()
            options.profile = LPATH['FIREFOX_PROFILE']
            options.headless = False
            gecko = SeleniumService(executable_path=self.gdm.install())
            self.browser = webdriver.Firefox(options=options, service=gecko)
            self.browser.get(url)
        self.log.debug("Browsing %s", url)

    def end(self):
        self.queue.join()
        driver = self.get_driver()
        if driver is not None:
            driver.quit()
            self.__set_driver(None)
        self.log.debug("Basico Download Manager stopped")
