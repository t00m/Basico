#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import basico.core.plg as plugintypes

class PluginBasicoCOREInfo(plugintypes.IBasicoCORE):
    def install(self):
        """
        Display Basico Core Info
        """
        config = self.app.get_envvar("FILE", "CNF")
        self.log.debug("FILE['CNF']: %s", config)
        # ~ self.app.stop()

    def uninstall(self, *args):
        pass

