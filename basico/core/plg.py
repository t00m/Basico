#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton

from basico.core.log import get_logger
from basico.core.srv import Service


class IBasico(IPlugin):
    log = None

    def __init__(self):
        pass

    def init(self):
        """Basic plugin initialization."""
        self.manager = PluginManagerSingleton.get()
        self.app = self.manager.app
        self.log = get_logger(__class__.__name__)

    def run(self):
        """Execute plugin.

        It can be overrided in your plugin.
        """
        self.install()

    def install(self):
        """Install plugin.

        It must be overrided by your plugin
        """
        pass
    
    def uninstall(self):
        """Uninstall plugin.

        It must be overrided by your plugin
        """
        pass

class IBasicoCORE(IBasico):
    def __init__(self, *args):
        self.log = get_logger(__class__.__name__)

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
