#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import basico.core.plg as plugintypes


class PluginBasicoGUIFullscreen(plugintypes.IBasicoCORE):
    def install(self):
        """
        Install Fullscreen toggle button
        """
        self.log.debug(self.app)

    def uninstall(self, *args):
        pass

