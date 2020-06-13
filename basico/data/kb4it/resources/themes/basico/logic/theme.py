#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Server module.

# File: theme.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Basico theme for Basico app
"""

from kb4it.services.builder import Builder

class Theme(Builder):
    def hello(self):
        self.log.debug("This is the theme Basico")

    def generate_sources(self):
        pass

    def build(self):
        # Default pages
        self.create_page_properties()
        self.create_page_stats()
        self.create_page_index_all()
        # ~ self.create_page_index()
        self.create_page_about_app()
        self.create_page_about_theme()
        self.create_page_about_kb4it()
        self.create_page_help()

