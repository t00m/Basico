#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Interfaces

import basico.core.plg as plugintypes

class PluginSAP(plugintypes.IBasicoSAP):
    def init(self, app):
        self.app = app

    def run(self, *args):
        # ~ self.add_category_filter("Database", plugintypes.IBasicoDatabase)
        self.log.debug("This is a plugin for SAP with args %s", args)
        srvgui = self.app.get_service('GUI')
        visor = srvgui.get_widget('visor_sapnotes')
        self.log.debug(visor)
        

