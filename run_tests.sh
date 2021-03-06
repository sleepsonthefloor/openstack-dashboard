#!/bin/bash

cd django-nova
python bootstrap.py
bin/buildout
bin/test

cd ../openstack-dashboard
python tools/install_venv.py

cp local/local_settings.py.example local/local_settings.py
tools/with_venv.sh dashboard/manage.py test
