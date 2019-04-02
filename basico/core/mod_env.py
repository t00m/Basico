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
from os.path import abspath, sep as SEP

ROOT = abspath(sys.modules[__name__].__file__ + "/../../")
USER_DIR = os.path.expanduser('~')

# App Info
APP = {}
APP['short'] = "basico"
APP['name'] = "SAP Notes Manager for SAP Consultants"
APP['license'] = "The code is licensed under the terms of the  GPL v3\nso you're free to grab, extend, improve and fork the code\nas you want"
APP['copyright'] = "Copyright \xa9 2016-2019 Tomás Vírseda"
APP['desc'] = "SAP Notes Manager for SAP Consultants\n\nThe code is licensed under the terms of the  GPL v3 so you're free to grab, extend, improve and fork the code as you want"
APP['version'] = "0.3"
APP['authors'] = ["Tomás Vírseda <tomasvirseda@gmail.com>"]
APP['documenters'] = ["Tomás Vírseda <tomasvirseda@gmail.com>"]
APP['email'] = "t00m@t00mlabs.net"


# Local paths
LPATH = {}
LPATH['ROOT'] = USER_DIR + SEP + '.basico' + SEP
LPATH['ETC'] = LPATH['ROOT'] + 'etc' + SEP
LPATH['VAR'] = LPATH['ROOT'] + 'var' + SEP
LPATH['PLUGINS'] = LPATH['VAR'] + 'plugins' + SEP
LPATH['LOG'] = LPATH['VAR'] + 'log' + SEP
LPATH['TMP'] = LPATH['VAR'] + 'tmp' + SEP
LPATH['CACHE'] = LPATH['VAR'] + 'cache' + SEP
LPATH['CACHE_XML'] = LPATH['CACHE'] + 'xml' + SEP
LPATH['CACHE_PDF'] = LPATH['CACHE'] + 'pdf' + SEP
LPATH['DB'] = LPATH['VAR'] + 'db' + SEP
LPATH['SAPNOTES'] = LPATH['DB'] + 'sapnotes' + SEP
LPATH['ANNOTATIONS'] = LPATH['DB'] + 'annotations' + SEP
LPATH['COLLECTIONS'] = LPATH['DB'] + 'collections' + SEP
LPATH['RESOURCES'] = LPATH['DB'] + 'resources' + SEP
LPATH['WWW'] = LPATH['VAR'] + 'www' + SEP
LPATH['EXPORT'] = LPATH['VAR'] + 'export' + SEP
LPATH['BACKUP'] = LPATH['EXPORT'] + 'backup' + SEP
LPATH['PDF'] = LPATH['EXPORT'] + 'pdf' + SEP
LPATH['OPT'] = LPATH['ROOT'] + 'opt' + SEP
LPATH['DRIVERS'] = LPATH['OPT'] + 'webdrivers' + SEP


# Global paths
GPATH = {}
GPATH['ROOT'] = ROOT
GPATH['DATA'] = GPATH['ROOT'] + SEP  + 'data' + SEP
GPATH['UI'] = GPATH['DATA'] + 'ui' + SEP
GPATH['ICONS'] = GPATH['DATA'] + 'icons' + SEP
GPATH['PLUGINS'] = GPATH['DATA'] + 'plugins' + SEP
GPATH['SHARE'] = GPATH['DATA'] + 'share' + SEP
GPATH['DOC'] = GPATH['SHARE'] + 'docs' + SEP
GPATH['RES'] = GPATH['DATA'] + 'res' + SEP
GPATH['SELENIUM'] = GPATH['RES'] + 'selenium' + SEP
GPATH['DRIVERS'] = GPATH['SELENIUM'] + 'drivers' + SEP
GPATH['HELP'] = GPATH['DATA'] + 'help' + SEP
GPATH['HELP_HTML'] = GPATH['HELP'] + 'html' + SEP

# Configuration, SAP Notes Database and Log files
FILE = {}
FILE['DBSAP'] = LPATH['SAPNOTES'] + 'sapnotes.json'
FILE['DBCOLS'] = LPATH['COLLECTIONS'] + 'collections.json'
FILE['CNF'] = LPATH['ETC'] + 'basico.ini'
FILE['LOG'] = LPATH['LOG'] + 'basico.log'
FILE['EVENTS'] = LPATH['LOG'] + 'events.log'
FILE['CREDITS'] = GPATH['DOC'] + 'CREDITS'
FILE['HELP_INDEX'] = GPATH['HELP_HTML'] + 'index.html'

# Annotations
ATYPES = ['Bookmark', 'Email', 'Fixme', 'Incident', 'Meeting', 'Note', 'Procedure', 'Snippet', 'Template', 'Todo']
