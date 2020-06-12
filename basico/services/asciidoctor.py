#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_asciidoctor.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Asciidoctor generation service
"""

import os
from basico.core.srv import Service
from basico.core.env import FILE, LPATH, ATYPES, APP, GPATH

CMD_ASCIIDOCTOR = "%s %s -b html5 -D %s %s"
ADOCPROPS = {
    # ~ 'stylesheet'            :   'custom-asciidoc.css',
    # ~ 'stylesdir'             :   GPATH['CSS'],
    'imagesdir'             :   LPATH['ATTACHMENTS'],
    'source-highlighter'    :   'coderay',
    'toc'                   :   'left',
    'toclevels'             :   '6',
    'icons'                 :   'font',
    'experimental'          :   None,
    'linkcss'               :   None,
}

class Asciidoctor(Service):
    def initialize(self):
        """
        Asciidoctor service for preview generation in html
        """
        self.get_services()


    def get_services(self):
        self.srvant = self.get_service('Annotation')
        self.srvutl = self.get_service('Utils')


    def get_target_path(self, aid):
        source = self.get_source_path(aid)
        target_dir = LPATH['CACHE_HTML']
        target_file = os.path.basename(source).replace('.adoc', '.html')
        path = os.path.join(target_dir, target_file)
        return path


    def get_source_path(self, aid):
        return self.srvant.get_content_file(aid)


    def generate_preview(self, aid):
        adocprops = ''
        for prop in ADOCPROPS:
            if ADOCPROPS[prop] is not None:
                if '%s' in ADOCPROPS[prop]:
                    adocprops += '-a %s=%s \\\n' % (prop, ADOCPROPS[prop] % self.target_path)
                else:
                    adocprops += '-a %s=%s \\\n' % (prop, ADOCPROPS[prop])
            else:
                adocprops += '-a %s \\\n' % prop
        # ~ self.log.debug("\tParameters passed to Asciidoc:\n%s" % adocprops)

        source = self.srvant.get_content_file(aid)
        atitle = self.srvant.get_title(aid)
        tmp_content = "= %s\n\n%s" % (atitle, open(source, 'r').read())
        tmp_file = LPATH['TMP'] + os.path.basename(source)
        with open(tmp_file, 'w') as tmp:
            tmp.write(tmp_content)
        target_dir = LPATH['CACHE_HTML']
        target_file = os.path.basename(source).replace('.adoc', '.html')
        target = "file://" + target_dir + target_file
        asciidoctor = self.srvutl.which('asciidoctor')
        cmd = CMD_ASCIIDOCTOR % (asciidoctor, adocprops, target_dir, tmp_file)
        # ~ self.log.debug(cmd)
        res = os.system(cmd)
        # ~ self.log.debug("Asciidoctor result: %s", res)
        # ~ self.log.debug("Preview in: %s", target)
        return target
