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
from configparser import SafeConfigParser

from gi.repository import GLib
from gi.repository import GObject

from yapsy.PluginManager import PluginManager
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager
from yapsy.VersionedPluginManager import VersionedPluginManager
from yapsy.PluginManager import PluginManagerSingleton

from basico.core.env import APP, FILE, GPATH, LPATH
from basico.core.srv import Service
import basico.core.plg as plugintypes

# ~ CONFIG_SECTION_NAME = 'Plugin Management'

APP_NAME = APP['short']

class Plugins(Service):
    manager = None    
    config = None

    def initialize(self):
        self.log.debug("Init Plugin System")                
        logging.getLogger('yapsy').setLevel(logging.INFO) # Disable Yaspy logging
        
        # Define plugins configuration file
        self.config_file = FILE['PLUGINS_CONF']
        self.config = SafeConfigParser()
        self.config.read(self.config_file)
        
        # Create plugin manager
        PluginManagerSingleton.setBehaviour([
            ConfigurablePluginManager,
            VersionedPluginManager,
        ])
        self.manager = PluginManagerSingleton.get()
        self.manager.app = self.app
        self.manager.setConfigParser(self.config, self.write_config)
        
        # ~ self.manager = ConfigurablePluginManager(configparser_instance=ConfigParser())
        self.log.debug(dir(self.manager))
        self.add_plugin_dir(GPATH['PLUGINS'])
        self.add_plugin_dir(LPATH['PLUGINS'])
        # ~ for name in self.app.get_services():
        self.add_category_filter("Reporting", plugintypes.IBasicoReporting)
        self.add_category_filter("Database", plugintypes.IBasicoDatabase)
        self.add_category_filter("SAP", plugintypes.IBasicoSAP)
        self.add_category_filter("GUI", plugintypes.IBasicoGUI)
        self.manager.collectPlugins()
        self.init()
        self.log.debug("Plugin System initialized")

    def write_config(self):
        """Write configuration to disk"""
        self.log.debug("Writing configuration file: %s" % self.config_file)
        with open(self.config_file, "w") as f:
            self.config.write(f)
            
        # ~ f = open(self.config_file, "w")
        # ~ self.config.write(f)
        # ~ f.close()

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
        
        cp = self.manager.config_parser
        self.log.debug("Config Parser: %s", list(cp.keys()))

    def init(self):
        plugins = self.get_plugins()
        self.log.debug("Found %d plugins:", len(plugins))
        for pluginInfo in plugins:
            plugin = pluginInfo.plugin_object
            try:
                plugin.init(self.app)
                self.manager.activatePluginByName(pluginInfo.name, ', '.join(pluginInfo.categories))
                self.log.debug("\t-> %s (%s) by %s on category %s" % (pluginInfo.name, pluginInfo.description, pluginInfo.author, "'%s'" % ', '.join(pluginInfo.categories)))
            except Exception as error:
                self.log.error(error)
                self.log.error(self.get_traceback())
