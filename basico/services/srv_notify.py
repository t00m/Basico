#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_notify.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: notifications service
"""

import sys
import gi

try:
    gi.require_version('Notify', '0.7') 
    from gi.repository import Notify
    NOTIFY_INSTALLED = True
except:
    NOTIFY_INSTALLED = False

from basico.core.mod_srv import Service


class Notification(Service):
    def initialize(self):
        if NOTIFY_INSTALLED:
            Notify.init('Basico')

    def show(self, module, message):
        if NOTIFY_INSTALLED:
            icon = "basico-component"# % icon_name # information | question | warning | error
            notification = Notify.Notification.new ("Basico - %s" % module, "<b>%s</b>" % message, icon)
            notification.show()
        else:
            return

