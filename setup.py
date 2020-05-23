#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: setup.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: setup.py tells you that the module/package you are about
# to install has been packaged and distributed with Distutils, which is
# the standard for distributing Python Modules.
"""

import os
from os.path import sep as SEP
import sys
import subprocess
from setuptools import setup

if sys.platform == 'win32':
    import os.path
    HOME = os.path.expanduser('~')
else:
    HOME = os.environ['HOME']

HOME_DESKTOP_DIR = HOME + SEP + '.local' + SEP + 'share' + SEP + 'applications'
HOME_ICONS_DIR = HOME + SEP + '.local' + SEP + 'share' + SEP + 'icons'


with open('README.adoc') as f:
    long_description = f.read()


def add_data_basico():
    try:
        data_files_basico = [
            ('share/applications', ['basico/data/desktop/basico.desktop']),
            ('share/icons', ['basico/data/icons/basico-component.svg']),
            ('basico/data/res/selenium/drivers',
                [
                    'basico/data/res/selenium/drivers/geckodriver',
                    'basico/data/res/selenium/drivers/geckodriver.README'
                ]),
            ('basico/data/res/css',
                [
                    'basico/data/res/css/basico.css',
                    'basico/data/res/css/custom-asciidoc.css',
                ]),
            ('basico/data/res/splash',
                [
                    'basico/data/res/splash/basico-splash-400x250.png',
                ]),
            ('basico/data/res/sap',
                [
                    'basico/data/res/sap/products.txt',
                ]),
            ('basico/data/tpl', ['basico/data/tpl/report.html']),
            ('basico/data/icons',
                [
                    'basico/data/icons/basico.svg',
                    'basico/data/icons/basico-about.svg',
                    'basico/data/icons/basico-add.svg',
                    'basico/data/icons/basico-annotation.svg',
                    'basico/data/icons/basico-annotation-type-bookmark.svg',
                    'basico/data/icons/basico-edit.svg',
                    'basico/data/icons/basico-annotation-type-note.svg',
                    'basico/data/icons/basico-annotation-type-fixme.svg',
                    'basico/data/icons/basico-annotation-type-incident.svg',
                    'basico/data/icons/basico-annotation-type-procedure.svg',
                    'basico/data/icons/basico-annotation-type-snippet.svg',
                    'basico/data/icons/basico-annotation-type-template.svg',
                    'basico/data/icons/basico-annotation-type-todo.svg',
                    'basico/data/icons/basico-annotation-type-email.svg',
                    'basico/data/icons/basico-annotation-type-meeting.svg',
                    'basico/data/icons/basico-arrow-up.svg',
                    'basico/data/icons/basico-arrow-down.svg',
                    'basico/data/icons/basico-archived.svg',
                    'basico/data/icons/basico-attachment.svg',
                    'basico/data/icons/basico-backup.svg',
                    'basico/data/icons/basico-backup-text-generic.svg',
                    'basico/data/icons/basico-backup-text-csv.svg',
                    'basico/data/icons/basico-backup-ms-excel.svg',
                    'basico/data/icons/basico-backup-restore.svg',
                    'basico/data/icons/basico-bookmark-off.svg',
                    'basico/data/icons/basico-bookmark-on.svg',
                    'basico/data/icons/basico-bookmarks.svg',
                    'basico/data/icons/basico-browse.svg',
                    'basico/data/icons/basico-category.svg',
                    'basico/data/icons/basico-chart.svg',
                    'basico/data/icons/basico-check-all.svg',
                    'basico/data/icons/basico-check-none.svg',
                    'basico/data/icons/basico-check-invert.svg',
                    'basico/data/icons/basico-check-accept.svg',
                    'basico/data/icons/basico-check-cancel.svg',
                    'basico/data/icons/basico-chronologic.svg',
                    'basico/data/icons/basico-clipboard.svg',
                    'basico/data/icons/basico-comments.svg',
                    'basico/data/icons/basico-component.svg',
                    'basico/data/icons/basico-copy-paste.svg',
                    'basico/data/icons/basico-dashboard.svg',
                    'basico/data/icons/basico-drafts.svg',
                    'basico/data/icons/basico-delete.svg',
                    'basico/data/icons/basico-description.svg',
                    'basico/data/icons/basico-dialog-error.svg',
                    'basico/data/icons/basico-dialog-information.svg',
                    'basico/data/icons/basico-dialog-ok.svg',
                    'basico/data/icons/basico-dialog-question.svg',
                    'basico/data/icons/basico-dialog-warning.svg',
                    'basico/data/icons/basico-duplicate.svg',
                    'basico/data/icons/basico-empty.svg',
                    'basico/data/icons/basico-filter.svg',
                    'basico/data/icons/basico-find.svg',
                    'basico/data/icons/basico-fullscreen.svg',
                    'basico/data/icons/basico-help.svg',
                    'basico/data/icons/basico-inbox.svg',
                    'basico/data/icons/basico-info.svg',
                    'basico/data/icons/basico-jump-sapnote.svg',
                    'basico/data/icons/basico-logviewer.svg',
                    'basico/data/icons/basico-menu-system.svg',
                    'basico/data/icons/basico-preview.svg',
                    'basico/data/icons/basico-priority.svg',
                    'basico/data/icons/basico-annotation-priority-high.svg',
                    'basico/data/icons/basico-annotation-priority-normal.svg',
                    'basico/data/icons/basico-annotation-priority-low.svg',
                    'basico/data/icons/basico-refresh.svg',
                    'basico/data/icons/basico-restore.svg',
                    'basico/data/icons/basico-sapnote.svg',
                    'basico/data/icons/basico-sap-knowledge-base-article.svg',
                    'basico/data/icons/basico-sap-note.svg',
                    'basico/data/icons/basico-sap-security-note.svg',
                    'basico/data/icons/basico-sap-standard-note.svg',
                    'basico/data/icons/basico-scope.svg',
                    'basico/data/icons/basico-select.svg',
                    'basico/data/icons/basico-settings.svg',
                    'basico/data/icons/basico-sid.svg',
                    'basico/data/icons/basico-stats.svg',
                    'basico/data/icons/basico-tag.svg',
                    'basico/data/icons/basico-tags.svg',
                    'basico/data/icons/basico-collection.svg',
                    'basico/data/icons/basico-type.svg',
                    'basico/data/icons/basico-unfullscreen.svg',
                ]),
            ('basico/data/share', []),
            ("basico/data/share/docs",
                    [
                    'AUTHORS',
                    'LICENSE',
                    'README.adoc',
                    'INSTALL',
                    'CREDITS',
                    'Changelog'
                    ]),
            ]
        return data_files_basico
    except:
        return []

data_files = []
data_files += add_data_basico()


def main():
    setup(
        name='basico',
        version='0.4',
        author='Tomás Vírseda',
        author_email='tomasvirseda@gmail.com',
        url='http://subversion.t00mlabs.net/basico',
        description='SAP Notes Manager for SAP Consultants',
        long_description=long_description,
        download_url = 'http://t00mlabs.net/downloads/basico-0.3.tar.gz',
        license='GPLv3',
        packages=['basico', 'basico.core', 'basico.services', 'basico.widgets'],
        # distutils does not support install_requires, but pip needs it to be
        # able to automatically install dependencies
        install_requires=[
              'python-dateutil',
              'selenium',
              'feedparser',
              'requests',
              'openpyxl',
              'rdflib',
        ],
        include_package_data=True,
        data_files=data_files,
        zip_safe=False,
        platforms='any',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: X11 Applications :: Gnome',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Other Audience',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Natural Language :: English',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3',
            'Topic :: Database :: Front-Ends',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities'
        ],
        entry_points={
            'gui_scripts': [
                'basico = basico.basico:main',
                ]
            },
    )


if __name__ == '__main__':
    main()
