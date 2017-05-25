#!/usr/bin/env bash
source ./venv/bin/activate
python ./tests/boleto_tests.py -v
python ./tests/credit_card_tests.py -v