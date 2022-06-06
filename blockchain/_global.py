#!/usr/bin/env python3

from uuid import uuid4

ERA = "mini"
ZEROS = "0000"
GENESIS_HASH = str(uuid4()).replace('-', '')
SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32