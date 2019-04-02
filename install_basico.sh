#!/usr/bin/env bash

LOCAL_DESKTOP_DIR=$HOME/.local/share/applications
LOCAL_ICONS_DIR=$HOME/.local/share/icons

# Instal Basico Desktop file
mkdir -p $LOCAL_DESKTOP_DIR
mkdir -p $LOCAL_ICONS_DIR
cp basico/data/desktop/basico.desktop $LOCAL_DESKTOP_DIR
cp basico/data/icons/basico-component.svg $LOCAL_ICONS_DIR
python3 setup.py install --user
