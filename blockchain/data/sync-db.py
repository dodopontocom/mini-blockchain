#!/usr/bin/env python3

import pymongo, requests
from urllib.parse import quote_plus
from _global import uri
import sys

PORT = sys.argv[1]
node = f'127.0.0.1:{PORT}'
db_name = "testblockchain"
collection_name = "blocks"

client = pymongo.MongoClient(uri)
mydb = client[db_name]
mycol = mydb[collection_name]

def _has_collection(name):
    db = client[db_name]
    return name in db.list_collection_names()

def _get_chain():
    try:
        chain = requests.get(f'http://{node}/get_chain')
        if chain.status_code == 200:
            block_chain = chain.json()['chain']
            length = chain.json()['length']            
            return block_chain, length
            #x = mycol.insert_one(block_chain[0])
            #print(mydb.list_collection_names())
    except requests.exceptions.ConnectionError:
        print("except: status code different from 200, probably nodes in the given port are not online!")
        return "0", "0"

block_chain, length = _get_chain()
if type(block_chain) == list and type(length) == int:
    if not _has_collection(name = collection_name):
        print("Creating db and collection...")
        x = mycol.insert_one(block_chain[0])
        print("Adding Genesis block...")

    result = client[db_name][collection_name].find()
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