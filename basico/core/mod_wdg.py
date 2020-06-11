#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: mod_wdg.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Basico Widget Base class
"""

import sys
import logging
import traceback as tb

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from basico.core.mod_env import FILE


class BasicoWidget(object):
    """
    Service class is the base class for Basico widgets.
    """
    log=None

    def __init__(self, app, logname):
        """Initialize Service instance
        @type app: Basico instance
        @param app: current Basico instance reference
        """
        self.app = app
        self.log = logging.getLogger(logname)
        self.log.addHandler(self.app.intercepter)
        self.init_section(logname)
        self.log.debug("Loading widget: %s", logname)


    def get_traceback(self):
        """
        get traceback
        """
        return tb.format_exc()


    def get_service(self, name):
        """
        get a service
        """
        return self.app.get_service(name)


    def init_section(self, name):
        """
        Check if section exists in config. If not, create it
        """
        self.srvstg = self.get_service('Settings')
        config = self.srvstg.load()

        try:
            config['Widget#%s' % name]
        except:
            config['Widget#%s' % name] = {}
            self.srvstg.save(config)
            self.log.debug("Section '%s' initialized in config file" % name)

    # ~ ### DECORATORS
    # ~ def hide_popovers(func):
        # ~ """
        # ~ FIXME: Quick and dirty hack to popdown all popovers when they
        # ~ remain open.
        # ~ """
        # ~ def exec_gui_method(self, *args):
            # ~ gui = self.app.get_service('GUI')
            # ~ uif = self.app.get_service('UIF')
            # ~ for name in gui.get_widgets():
                # ~ widget = gui.get_widget(name)
                # ~ if isinstance(widget, Gtk.Popover):
                    # ~ widget.popdown()
            # ~ func(self)
        # ~ return exec_gui_method

    # ~ hide_popovers = staticmethod( hide_popovers )
