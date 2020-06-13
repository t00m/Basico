#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: kb4it.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: KB4IT Service
"""

from argparse import Namespace
from kb4it.kb4it import KB4IT

from basico.core.srv import Service


class KB4Basico(Service):
    def initialize(self):
        self.log.debug("Basico using %s" % KB4IT().get_version())
