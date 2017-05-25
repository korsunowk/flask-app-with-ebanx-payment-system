#!/usr/bin/env bash
virtualenv venv -p python3 --no-site-packages
source ./venv/bin/activate
pip install -r ./requirements.txt
