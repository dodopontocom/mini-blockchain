#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

FLASK_ENV=development ${BASEDIR}/../core/walletapi.py
