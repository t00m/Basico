rm -rf basico.egg-info build dist
pip3 uninstall basico -qy
python3 setup.py install --user
