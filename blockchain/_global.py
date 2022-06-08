#!/usr/bin/env python3

from uuid import uuid4
import os
import pymongo

ERA = "mini"
ZEROS = "0000"
GENESIS_HASH = str(uuid4()).replace('-', '')
SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32

uri = os.environ['MONGO_CONN_STRING']
db_name = "testblockchain"
collection_name = "blocks"

client = pymongo.MongoClient(uri)
def _has_collection(name):
    db = client[db_name]
    return name in db.list_collection_names()