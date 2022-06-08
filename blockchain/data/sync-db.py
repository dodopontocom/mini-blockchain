#!/usr/bin/env python3

import pymongo, requests
from urllib.parse import quote_plus
from _global import uri
import sys

PORT = sys.argv[1]
node = f'127.0.0.1:{PORT}'

client = pymongo.MongoClient(uri)
mydb = client["testblockchain"]
mycol = mydb["blocks"]

def _has_collection(name):
    db = client['testblockchain']
    return name in db.list_collection_names()

if not _has_collection(name = "blocks"):
    try:
        chain = requests.get(f'http://{node}/get_chain')
        if chain.status_code == 200:
            print("Adding genesis block...")
            length = chain.json()['length']
            block_chain = chain.json()['chain']
            x = mycol.insert_one(block_chain[0])
            #print(mydb.list_collection_names())
    except requests.exceptions.ConnectionError:
        print("except: status code different from 200, probably nodes in the list are not online!")

try:
    chain = requests.get(f'http://{node}/get_chain')
    if chain.status_code == 200:
        length = chain.json()['length']
        block_chain = chain.json()['chain']
        result = client["testblockchain"]["blocks"].find()
        index = None
        for i in result:
            index = i['index']
        _to_add = (length - index)
        _to_add_list = (length - _to_add)
        if _to_add == 0:
            print(f'database is synced: {_to_add} index to add.')
        else:
            while _to_add_list < length:
                print('adding index: ' + str(block_chain[_to_add_list]['index']))
                x = mycol.insert_one(block_chain[_to_add_list])
                _to_add_list += 1
            print(f'database is synced: {_to_add_list} index.')
except requests.exceptions.ConnectionError:
    print("except: status code different from 200, probably nodes in the list are not online!")