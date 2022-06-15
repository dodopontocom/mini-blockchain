#!/usr/bin/env python3

from uuid import uuid4
import os
import pymongo

ERA = "mini"
ZEROS = "0000"
GENESIS_HASH = str(uuid4()).replace('-', '')
SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32

high_transaction_count = 50
proof_speed = 400
good_reward = 10.0
ok_reward = 6.5
high_transaction_count_good_reward = 50.0
high_transaction_count_ok_reward = 22.0

uri = os.environ['MONGO_CONN_STRING']
db_name = "testblockchain"
collection_name = "blocks"

#client = pymongo.MongoClient(uri)
def _has_collection(name):
    client = pymongo.MongoClient(uri)
    db = client[db_name]
    return name in db.list_collection_names()

def _return_collection_no_id(db, coll):
    client = pymongo.MongoClient(uri)
    return client[db][coll].find({}, {"_id": 0})

def _return_collection_with_id(db, coll):
    client = pymongo.MongoClient(uri)
    return client[db][coll].find({})

def return_conn():
    return pymongo.MongoClient(uri)

