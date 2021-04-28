#!/usr/bin/python 3
# -*- coding: utf-8 -*-
"""
# File: plg.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Plugin Interfaces
"""

import sys
import logging

from gi.repository import GLib
from gi.repository import GObject

# ~ from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager

from basico.core.env import GPATH, LPATH
from basico.core.srv import Service
import basico.core.plg as plugintypes


class Plugins(Service):
    manager = None

    def initialize(self):
        self.log.debug("Init Plugin System")
        logging.getLogger('yapsy').setLevel(logging.INFO)
        self.manager = PluginManager()
        self.add_plugin_dir(GPATH['PLUGINS'])
        self.add_plugin_dir(LPATH['PLUGINS'])
        # ~ for name in self.app.get_services():
        self.add_category_filter("Reporting", plugintypes.IBasicoReporting)
        self.add_category_filter("Database", plugintypes.IBasicoDatabase)
        self.add_category_filter("SAP", plugintypes.IBasicoSAP)
        self.manager.collectPlugins()
        self.init()
        self.log.debug("Plugin System initialized")

    def add_plugin_dir(self, plugin_dir):
        locator = self.manager.getPluginLocator()
        locator.plugins_places.append(plugin_dir)
        self.manager.setPluginLocator(locator)
        self.log.debug("Added plugin path '%s' to PluginManager" % plugin_dir)

    def add_category_filter(self, name, interface):
        categories = self.manager.categories_interfaces
        categories[name] = interface
        self.manager.setCategoriesFilter(categories)
        self.log.debug("Added category '%s' to PluginManager" % name)

    def get_plugins(self, category=None):
        if category is None:
            return self.manager.getAllPlugins()

    def run(self, category=None):
        if self.manager is None:
            return

        self.log.debug("Running pluggins of category '%s'", category)
        if category is None:
            for pluginInfo in self.get_plugins():
                plugin = pluginInfo.plugin_object
                plugin.run(self.app)
        elif category in self.manager.getCategories():
            for pluginInfo in self.manager.getPluginsOfCategory(category):
                plugin = pluginInfo.plugin_object
                plugin.run(self.app)
        else:
            self.log.warning("No plugins found for category '%s'", category)

    def init(self):
        plugins = self.get_plugins()
        self.log.debug("Found %d plugins:", len(plugins))
        for pluginInfo in plugins:
            plugin = pluginInfo.plugin_object
            try:
                plugin.init(self.app)
                self.log.debug("\t-> %s (%s) by %s on category %s" % (pluginInfo.name, pluginInfo.description, pluginInfo.author, "'%s'" % ', '.join(pluginInfo.categories)))
            except Exception as error:
                self.log.error(error)
                self.log.error(self.get_traceback())
