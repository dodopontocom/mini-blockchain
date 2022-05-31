#!/usr/bin/env python3

import time
import hashlib
import json
from urllib.parse import urlparse
import requests
from uuid import uuid4
from flask import Flask, jsonify, request
from hashlib import blake2b
from hmac import compare_digest

SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32

def hashing(type, block):
    if type == "sha":
        hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()

    if type == "blake":
        h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
        h.update(json.dumps(block).encode())
        hash = h.hexdigest()

    return hash

chain = []
block = {
    'era': "mini",
    'index': 1,
    'hash': 0000,
    'proof': 1,
    'time_to_proof': 1,
    'previous_hash': -1,
    'timestamp': str(round(time.time())),
    'transactions_count': 0,
    'transactions': [],

}

chain.append(block)
print(hashing("blake", block))

print(chain)

print(hashlib.sha256(json.dumps(block).encode()).hexdigest())

print(json.dumps(block))


#--------------------------
print("----\n")


message = "sometexthere".encode()
print("message: ", message)

print("BLAKE2B: ", blake2b(message).hexdigest())

SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32

chain = [
            {
                "remetente": "John",
                "destinatario": "Peter",
                "mensagem": "300"
            },
            {
                "remetente": "Henry",
                "destinatario": "Paul",
                "mensagem": "120"
            }

        ]
block_chain = []
def get_time():
    return time.time()

def sign(cookie):
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
    h.update(cookie)
    return h.hexdigest()
    
def verify(cookie, sig):
        good_sig = sign(cookie)
        return compare_digest(good_sig, sig)
        
for c in chain:

    cookie = json.dumps(c).encode()
    sig_cookie = sign(cookie)
    #print(verify(cookie, sig_cookie))

def add_block(block):
    if (len(block_chain) == 0):
        block["timestamp"] = get_time()
        block["hash"] = sign(json.dumps(block).encode())
    else:
        block["timestamp"] = get_time()
        last_block = block_chain[-1]
        block["last_hash"] = last_block["hash"]
        block["hash"] = sign(json.dumps(block).encode())
    block_chain.append(block)

for t in chain:
    add_block(t)

print(block_chain)

for v in block_chain:
    cookie = json.dumps(v).encode()
    sig_cookie = sign(cookie)
    print(verify(cookie, sig_cookie))