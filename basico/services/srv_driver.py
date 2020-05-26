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
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from basico.core.mod_env import LPATH, FILE
from basico.core.mod_srv import Service

# GECKODRIVER_URL = "https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz"


class SeleniumDriver(Service):
    def initialize(self):
        """
        Check Gecko driver availability. If not found, install it
        """
        self.check()


    def check(self):
        """
        Check gecko webdriver
        You must install geckodriver. It is mandatory
        Yo can download it from:
        https://github.com/mozilla/geckodriver/
        Then, extract the binary and copy it to somewhere in your $PATH.
        If OS is Linux: /usr/local/bin/geckodriver
        If OS is Windows: C:\Windows\System32 or elsewhere.

        Basico will try to do it for you.
        """
        # Show Selenium version
        self.log.debug("Selenium version: %s" % selenium.__version__)

        utils = self.get_service('Utils')

        # First, add BASICO OPT Path to $PATH
        GECKO_INSTALL_DIR = LPATH['DRIVERS']
        os.environ["PATH"] += os.pathsep + GECKO_INSTALL_DIR

        # Asciidoctor installed?
        ASCIIDOCTOR = utils.which('asciidoctor')

        # Then, look for Geckodriver
        GECKODRIVER = utils.which('geckodriver')

        if not GECKODRIVER:
            self.log.debug("Gecko driver not found.")
            utils.install_geckodriver()

        GECKODRIVER = utils.which('geckodriver')
        if GECKODRIVER is None:
            self.log.warning("Gecko driver not found.")
            return False
        else:
            self.log.debug("Gecko Webdriver found in: %s" % GECKODRIVER)
            return True


    def open(self):
        '''
        In order to have selenium working with Firefox and be able to
        get SAP Notes from launchpad.support.sap.com you must:
        1. Use a browser certificate (SAP Passport) in order to avoid
           renewed logons.
           You can apply for it at:
           https://support.sap.com/support-programs-services/about/getting-started/passport.html
        2. Get certificate and import it into Firefox.
           Open menu -> Preferences -> Advanced -> View Certificates
           -> Your Certificates -> Import
        3. Trust this certificate (auto select)
        4. Check it. Visit some SAP Note url in Launchpad.
           No credentials will be asked.
           Launchpad must load target page successfully.
        '''
        driver = None

        # Enable custom Firefox profile
        options = Options()
        options.profile = LPATH['FIREFOX_PROFILE']

        # Enable headless
        options.headless = True

        # Enable custom geckodriver
        # Disabled as the driver directory with the binary is defined
        # above in the envvar PATH
        # service = Service(FILE['FIREFOX_DRIVER'])

        try:
            # With Service
            # ~ driver = webdriver.Firefox(options=options, service=service)

            # Without Service:
            driver = webdriver.Firefox(options=options)
            self.log.debug("Webdriver initialited: %s", driver)
        except Exception as error:
            self.log.error(error)
            # Geckodriver not found
            # Download it from:
            # https://github.com/mozilla/geckodriver/releases/latest

        return driver

        # ~ driver = Firefox(
                # ~ capabilities=capabilities,
                # ~ firefox_profile=profile2)

        # ~ from selenium import webdriver

        # ~ url = "https://mail.google.com"
        # ~ fp = webdriver.FirefoxProfile('/Users/<username>/Library/Application Support/Firefox/Profiles/71v1uczn.default')

        # ~ driver = webdriver.Firefox(fp)


    def close(self, driver):
        driver.quit()
        self.log.debug("Webdriver closed")
        driver = None


    def load(self, driver, URL):
        driver.get(URL)
        return driver


