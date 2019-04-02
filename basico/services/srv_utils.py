#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_utils.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Generic functions service
"""

import os
import re
import sys
import subprocess
import tarfile
import zipfile
import shutil
import requests
import webbrowser
import feedparser
from datetime import datetime
from basico.core.mod_env import GPATH, LPATH
from basico.core.mod_srv import Service

class Utils(Service):
    """
    Missing class docstring (missing-docstring)
    """

    def initialize(self):
        """
        Missing method docstring (missing-docstring)
        """
        self.get_services()


    def get_services(self):
        """
        Missing method docstring (missing-docstring)
        """
        self.srvdtb = self.get_service('DB')


    def timestamp(self):
        """
        Missing method docstring (missing-docstring)
        """
        now = datetime.now()
        timestamp = "%4d%02d%02d_%02d%02d%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)

        return timestamp


    def get_datetime(self, timestamp):
        """
        Missing method docstring (missing-docstring)
        """
        adate = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        return adate


    def get_human_date_from_timestamp(self, timestamp=None):
        """
        Missing method docstring (missing-docstring)
        """
        if timestamp is None:
            timestamp = self.timestamp()
            
        adate = self.get_datetime(timestamp)
        return "%s" % adate.strftime("%Y/%m/%d %H:%M")


    def get_excel_date(self, timestamp):
        timestamp = timestamp.replace('-', '/')        
        timestamp = timestamp.replace('T', ' ')
        adate = datetime.strptime(timestamp, "%Y/%m/%d %H:%M:%S")
        excel_date = "%s" % adate.strftime("%d/%m/%Y")
        return excel_date


    def fuzzy_date_from_timestamp(self, timestamp):
        """
        Missing method docstring (missing-docstring)
        """
        d1 = self.get_datetime(timestamp)
        d2 = datetime.now()
        rdate = d2 - d1 # DateTimeDelta
        if rdate.days > 0:
            if rdate.days <= 31:
                return "%d days ago" % int(rdate.days)

            if rdate.days > 31 and rdate.days < 365:
                return "%d months ago" % int((rdate.days/31))

            if rdate.days >= 365:
                return "%d years ago" % int((rdate.days/365))

        hours = rdate.seconds / 3600
        if int(hours) > 0:
            return "%d hours ago" % int(hours)

        minutes = rdate.seconds / 60
        if int(minutes) > 0:
            return "%d minutes ago" % int(minutes)

        if int(rdate.seconds) > 0:
            return "%d seconds ago" % int(rdate.seconds)

        if int(rdate.seconds) == 0:
            return "Right now"


    def browse(self, url):
        """
        Missing method docstring (missing-docstring)
        """
        if sys.platform in ['linux', 'linux2']:
            browser = webbrowser.get('firefox')
        elif sys.platform == 'win32':
            browser = webbrowser.get('windows-default')

        browser.open_new_tab(url)


    def which(self, program):
        """
        Missing method docstring (missing-docstring)
        """
        if sys.platform == 'win32':
            program = program + '.exe'

        def is_exe(fpath):
            """
            Missing method docstring (missing-docstring)
            """
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None


    def install_geckodriver(self):
        """
        Install Gecko Driver
        """
        GECKODRIVER_LINUX = GPATH['DRIVERS'] + 'geckodriver'
        GECKODRIVER_WIN32 = GPATH['DRIVERS'] + 'geckodriver.exe'
        GECKO_INSTALL_DIR = LPATH['DRIVERS']

        if sys.platform == 'linux':
            shutil.copy(GECKODRIVER_LINUX, GECKO_INSTALL_DIR)
        else:
            shutil.copy(GECKODRIVER_WIN32, GECKO_INSTALL_DIR)
        self.log.debug("Gecko driver installed to %s" % GECKO_INSTALL_DIR)


    def download(self, prgname, source, target):
        """
        Missing method docstring (missing-docstring)
        """
        try:
            self.log.debug("Downloading %s from: %s" % (prgname, source))
            response = requests.get(source, stream=True)
            with open(target, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            self.log.debug("%s downloaded to %s" % (prgname, target))
            return True
        except Exception as error:
            self.log.error(error)
            return False


    def extract(self, filename, target_path, protocol):
        """
        Missing method docstring (missing-docstring)
        """
        self.log.debug("Extracting %s to %s using protocol %s" % (filename, target_path, protocol))
        if protocol in ['tar.gz', 'bz2']:
            try:
                tar = tarfile.open(filename, "r:*")
                tar.extractall(target_path)
                tar.close()
                self.log.debug("Extracted successfully")
                return True
            except Exception as error:
                self.log.error(error)
                return False
        elif protocol == 'zip':
            try:
                self.unzip(filename, target_path)
                self.log.debug("Extracted successfully")
                return True
            except Exception as error:
                self.log.error(error)
                return False

    def zip(self, filename, directory):
        """
        Zip directory and rename to .bco
        """
        # http://stackoverflow.com/a/25650295
        #~ make_archive(archive_name, 'gztar', root_dir)
        self.log.debug("Target: %s", filename)
        sourcename = os.path.basename(filename)
        dot = sourcename.find('.')
        if dot == -1:
            basename = sourcename
        else:
            basename = sourcename[:dot]
        sourcedir = os.path.dirname(filename)
        source = os.path.join(sourcedir, basename)
        zipfile = shutil.make_archive(source, 'zip', directory)
        target = source + '.bco'
        shutil.move(zipfile, target)
        return target


    def unzip(self, target, install_dir):
        """
        Unzip file to a given dir
        """
        zip_archive = zipfile.ZipFile(target, "r")
        zip_archive.extractall(path=install_dir)
        zip_archive.close()


    def get_firefox_profile_dir(self):
        """
        Self-explained. Get default Firefox directory
        """
        if sys.platform in ['linux', 'linux2']:
            cmd = "ls -d /home/$USER/.mozilla/firefox/*.default/"
            p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
            FF_PRF_DIR = p.communicate()[0][0:-2]
            FF_PRF_DIR_DEFAULT = str(FF_PRF_DIR, 'utf-8')
        elif sys.platform == 'win32':
            import glob
            APPDATA = os.getenv('APPDATA')
            FF_PRF_DIR = "%s\\Mozilla\\Firefox\\Profiles\\" % APPDATA
            PATTERN = FF_PRF_DIR + "*default*"
            FF_PRF_DIR_DEFAULT = glob.glob(PATTERN)[0]

        return FF_PRF_DIR_DEFAULT


    def feedparser_parse(self, thing):
        """
        Missing method docstring (missing-docstring)
        """
        try:
            return feedparser.parse(thing)
        except TypeError:
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                return feedparser.parse(thing)
            else:
                self.log.error(self.get_traceback())
                return None


    def check(self):
        """
        Check Basico environment
        """
        gtk_version = self.uif.check_gtk_version() # Check GTK version
        gecko_driver = self.driver.check() # Check Gecko webdrver
        run = gtk_version and gecko_driver
        if run:
            self.log.debug("Basico environment ready!")
        else:
            self.log.error("Error(s) found checking Basico environment")

        return run




    def clean_html(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
