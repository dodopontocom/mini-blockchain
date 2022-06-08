#!/usr/bin/env python3

from uuid import uuid4
import os

ERA = "mini"
ZEROS = "0000"
GENESIS_HASH = str(uuid4()).replace('-', '')
SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32

uri = os.environ['MONGO_CONN_STRING']