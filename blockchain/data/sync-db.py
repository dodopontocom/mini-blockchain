#!/usr/bin/env python3

import pymongo, requests
from urllib.parse import quote_plus
import _global
import sys

PORT = sys.argv[1]
node = f'127.0.0.1:{PORT}'

#client = pymongo.MongoClient(_global.uri)
mydb = _global.client[_global.db_name]
mycol = mydb[_global.collection_name]

def _get_chain():
    try:
        chain = requests.get(f'http://{node}/get_chain')
        if chain.status_code == 200:
            block_chain = chain.json()['chain']
            length = chain.json()['length']            
            return block_chain, length
    except requests.exceptions.ConnectionError:
        print("except from sync-db: status code different from 200, probably nodes in the given port are not online!")
        return "0", "0"

def add_block_db(*args):
    result = _global.client[_global.db_name][_global.collection_name].find()
    index = None
    for i in result:
        index = i['index']
    _to_add = (int(length) - index)
    _to_add_list = (int(length) - _to_add)
    if _to_add == 0:
        print(f'database is synced: {_to_add} index to add.')
    else:
        while _to_add_list < int(length):
            print('adding index: ' + str(block_chain[_to_add_list]['index']))
            x = mycol.insert_one(block_chain[_to_add_list])
            _to_add_list += 1
        print(f'database is synced: last index ({_to_add_list}) just added.')

block_chain, length = _get_chain()
if type(block_chain) == list and type(length) == int:
    if not _global._has_collection(name = _global.collection_name):
        print("Creating db and collection...")
        x = mycol.insert_one(block_chain[0])
        print("Adding Genesis block...")
    add_block_db(block_chain, length)

print(mydb.list_collection_names())