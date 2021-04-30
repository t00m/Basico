#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import basico.core.plg as plugintypes


class PluginSAP(plugintypes.IBasicoSAP):
    def run(self, *args):
        self.log.debug("This is a plugin for SAP with args %s", args)
        srvgui = self.app.get_service('GUI')
        visor = srvgui.get_widget('visor_sapnotes')
        self.log.debug(visor)


