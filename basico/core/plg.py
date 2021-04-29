#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin

from basico.core.log import get_logger
from basico.core.srv import Service

# Interfaces

class IBasico(IPlugin):
    log = None

    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)

    def init(self, *args):
        self.log.debug(args)
    
    def run(self, *args):
        self.install()

class IBasicoDatabase(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)

class IBasicoDownload(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)

class IBasicoServices(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)

class IBasicoReporting(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)

class IBasicoSAP(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)
        
class IBasicoGUI(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)
    