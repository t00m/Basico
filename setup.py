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
import glob
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

def add_data_from_dir(root_data):
    """Add data files from a given directory."""
    dir_files = []
    resdirs = set()
    for root, dirs, files in os.walk(root_data):
        print("%s -> %s" % (root, dirs))
        resdirs.add(os.path.realpath(root))

    for directory in resdirs:
        files = glob.glob(os.path.join(directory, '*'))
        relfiles = []
        for thisfile in files:
            if not os.path.isdir(thisfile):
                relfiles.append(os.path.relpath(thisfile))

        num_files = len(files)
        if num_files > 0:
            dir_files.append((os.path.relpath(directory), relfiles))

    return dir_files


def add_data_basico():
    try:
        data_files_basico = [
            ('share/applications', ['basico/data/desktop/basico.desktop']),
            ('share/icons', ['basico/data/icons/basico-component.svg']),
            ('basico/data/res/selenium',
                [
                    'basico/data/res/selenium/webdriver_prefs.json'
                ]),
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
            ('basico/data/res/sap',
                [
                    'basico/data/res/sap/products.txt',
                ]),
            ('basico/data/tpl', ['basico/data/tpl/report.html']),
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
data_files += add_data_from_dir('basico/data/help')
data_files += add_data_from_dir('basico/data/kb4it')
data_files += add_data_from_dir('basico/data/icons')
data_files += add_data_from_dir('basico/data/plugins')

def main():
    setup(
        name='basico',
        version='0.4',
        author='Tomás Vírseda',
        author_email='tomasvirseda@gmail.com',
        url='https://github.com/t00m/Basico',
        description='SAP Notes Manager for SAP Consultants',
        long_description=long_description,
        download_url = 'https://github.com/t00m/Basico/archive/master.zip',
        license='GPLv3',
        packages=['basico', 'basico.core', 'basico.services', 'basico.widgets'],
        install_requires=[
            # ~ 'nltk',
            # ~ 'inotify',
            # ~ 'GitPython',
            'Yapsy==1.12.0'
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
