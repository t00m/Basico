#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_env.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Environment variables module
"""

import sys
import os


# ~ from git import Repo

from os.path import abspath, sep as SEP

# Git Repo info
# ~ repo = Repo('.', search_parent_directories=True)
# ~ sha = repo.head.commit.hexsha
# ~ short_sha = repo.git.rev_parse(sha, short=8)

# Directory initialization
ROOT = abspath(sys.modules[__name__].__file__ + "/../../")
USER_DIR = os.path.expanduser('~')

# App Info
APP = {}
APP['short'] = "basico"
APP['name'] = "SAP Notes Manager for SAP Consultants"
APP['license'] = "The code is licensed under the terms of the  GPL v3\nso you're free to grab, extend, improve and fork the code\nas you want"
APP['copyright'] = u"Copyright \xa9 Tomás Vírseda"
APP['desc'] = "SAP Notes Manager for SAP Consultants\n\nThe code is licensed under the terms of the  GPL v3 so you're free to grab, extend, improve and fork the code as you want"
APP['version'] = "0.4"
APP['authors'] = [u"Tomás Vírseda <tomasvirseda@gmail.com>"]
APP['documenters'] = []
APP['email'] = "tomasvirseda@gmail.com"


# Local paths
LPATH = {}
LPATH['ROOT'] = os.path.join(USER_DIR, '.basico')
LPATH['ETC'] = os.path.join(LPATH['ROOT'], 'etc')
LPATH['VAR'] = os.path.join(LPATH['ROOT'], 'var')
LPATH['DOC'] = os.path.join(LPATH['VAR'], 'doc')
LPATH['DOC_SOURCE'] = os.path.join(LPATH['DOC'], 'sources')
LPATH['DOC_TARGET'] = os.path.join(LPATH['DOC'], 'html')
LPATH['PLUGINS'] = os.path.join(LPATH['VAR'], 'plugins')
LPATH['LOG'] = os.path.join(LPATH['VAR'], 'log')
LPATH['TMP'] = os.path.join(LPATH['VAR'], 'tmp')
LPATH['CACHE'] = os.path.join(LPATH['VAR'], 'cache')
LPATH['CACHE_XML'] = os.path.join(LPATH['CACHE'], 'xml')
LPATH['CACHE_PDF'] = os.path.join(LPATH['CACHE'], 'pdf')
LPATH['CACHE_HTML'] = os.path.join(LPATH['CACHE'], 'html')
LPATH['DB'] = os.path.join(LPATH['VAR'], 'db')
LPATH['SAPNOTES'] = os.path.join(LPATH['DB'], 'sapnotes')
LPATH['ANNOTATIONS'] = os.path.join(LPATH['DB'], 'annotations')
LPATH['COLLECTIONS'] = os.path.join(LPATH['DB'], 'collections')
LPATH['RESOURCES'] = os.path.join(LPATH['DB'], 'resources')
LPATH['ATTACHMENTS'] = os.path.join(LPATH['DB'], 'attachments')
LPATH['WWW'] = os.path.join(LPATH['VAR'], 'www')
LPATH['EXPORT'] = os.path.join(LPATH['VAR'], 'export')
LPATH['BACKUP'] = os.path.join(LPATH['EXPORT'], 'backup')
LPATH['PDF'] = os.path.join(LPATH['EXPORT'], 'pdf')
LPATH['OPT'] = os.path.join(LPATH['ROOT'], 'opt')
LPATH['DRIVERS'] = os.path.join(LPATH['OPT'], 'webdrivers') # Deprecated
LPATH['FIREFOX_PROFILE'] = os.path.join(LPATH['DRIVERS'], 'basico.default')


# Global paths
GPATH = {}
GPATH['ROOT'] = ROOT
GPATH['DATA'] = os.path.join(GPATH['ROOT'], 'data')
GPATH['UI'] = os.path.join(GPATH['DATA'], 'ui')
GPATH['KB4IT'] = os.path.join(GPATH['DATA'], 'kb4it')
GPATH['ICONS'] = os.path.join(GPATH['DATA'], 'icons')
GPATH['PLUGINS'] = os.path.join(GPATH['DATA'], 'plugins')
GPATH['SHARE'] = os.path.join(GPATH['DATA'], 'share')
GPATH['DOC'] = os.path.join(GPATH['SHARE'], 'docs')
GPATH['RES'] = os.path.join(GPATH['DATA'], 'res')
GPATH['CSS'] = os.path.join(GPATH['RES'], 'css')
GPATH['SAP'] = os.path.join(GPATH['RES'], 'sap')
# ~ GPATH['SPLASH'] = os.path.join(GPATH['RES'], 'splash')
GPATH['SELENIUM'] = os.path.join(GPATH['RES'], 'selenium')
GPATH['DRIVERS'] = os.path.join(GPATH['SELENIUM'], 'drivers')
GPATH['HELP'] = os.path.join(GPATH['DATA'], 'help')
GPATH['HELP_HTML'] = os.path.join(GPATH['HELP'], 'html')

# Configuration, SAP Notes Database and Log files
FILE = {}
FILE['CSS'] = os.path.join(GPATH['CSS'], 'basico.css')
FILE['EXT'] = os.path.join(GPATH['RES'], 'extensions.json')
FILE['DBSAP'] = os.path.join(LPATH['SAPNOTES'], 'sapnotes.json')
FILE['DBCOLS'] = os.path.join(LPATH['COLLECTIONS'], 'collections.json')
FILE['CNF'] = os.path.join(LPATH['ETC'], 'basico.ini')
FILE['PLUGINS_CONF'] = os.path.join(LPATH['ETC'], 'plugins.ini')
FILE['LOG'] = os.path.join(LPATH['LOG'], 'basico.log')
FILE['EVENTS'] = os.path.join(LPATH['LOG'], 'events.log')
FILE['CREDITS'] = os.path.join(GPATH['DOC'], 'CREDITS')
FILE['KB4IT_INDEX'] = os.path.join(LPATH['DOC_TARGET'], 'index.html')
FILE['HELP_INDEX'] = os.path.join(GPATH['HELP_HTML'], 'index.html')
FILE['HELP_FIREFOX_PROFILE'] = os.path.join(GPATH['HELP_HTML'], 'firefox_profile.html')
# ~ FILE['SPLASH'] = os.path.join(GPATH['SPLASH'], 'basico-splash-400x250.png')
FILE['G_SAP_PRODUCTS'] = os.path.join(GPATH['SAP'], 'products.txt')
FILE['L_SAP_PRODUCTS'] = os.path.join(LPATH['RESOURCES'], 'products.txt')
FILE['FIREFOX_DRIVER'] = os.path.join(LPATH['DRIVERS'], 'geckodriver')
FILE['SELENIUM_FIREFOX_WEBDRIVER_CONFIG_SOURCE'] = os.path.join(GPATH['SELENIUM'], 'webdriver_prefs.json')

# Default settings for SAP module
LOGIN_PAGE_URL = "https://accounts.sap.com"
LOGOUT_PAGE_URL = "https://accounts.sap.com/ui/logout"
ODATA_NOTE_URL = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')"
ODATA_NOTE_URL_LONGTEXT = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')?$expand=LongText"
SAP_NOTE_URL = "https://launchpad.support.sap.com/#/notes/%s"
SAP_NOTE_URL_PDF = "https://launchpad.support.sap.com/services/pdf/notes/%s/E"
TIMEOUT = 10

# KB Basico
ATYPES = ['Bookmark', 'Email', 'Fixme', 'Incident', 'Meeting', 'Note', 'Procedure', 'Snippet', 'Template', 'Todo']
