#!/usr/bin/env python3

from uuid import uuid4
import os
import pymongo
import time
from hashlib import blake2b
from hmac import compare_digest

ERA = "mini"
ZEROS = "0000"
TSUPPLY = 1_000_000_000_000
GENESIS_HASH = str(uuid4()).replace('-', '')
SECRET_KEY = "lifeisachessgame,youdontwanttowasteamove"
AUTH_SIZE = 32

W0_BALANCE = 120_000_000
W1_BALANCE = 345
W2_BALANCE = 560

INIT_SUPPLY = (TSUPPLY - W0_BALANCE - W1_BALANCE - W2_BALANCE)

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

def getUptime(startTime):
    return round(time.time() - startTime)

def sign_blake2(self, cookie):
        h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY.encode())
        h.update(cookie)
        return h.hexdigest()

def verify_disgest(self, cookie, sig):
    good_sig = self.sign_blake2(cookie)
    return compare_digest(good_sig, sig)
