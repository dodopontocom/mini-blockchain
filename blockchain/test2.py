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
            },
            {
                "remetente": "John",
                "destinatario": "Peter",
                "mensagem": "300"
            },
            {
                "remetente": "John",
                "destinatario": "Peter",
                "mensagem": "300"
            }

        ]
block_chain = []
def get_time():
    return time.time()


def isValidHashDifficulty(hash, difficulty):
	count = 0
	for i in hash:
		count += 1
		if(i == '0'):
			break
	return count > difficulty

def generate_hash(block):
	nonce = 0
	block["nonce"] = nonce
	hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
	while(not isValidHashDifficulty(hash, 6)):
		nonce = nonce + 1
		block["nonce"] = nonce
		hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
		#hash = sha256(json.dumps(block)).hexdigest()
	return hash


def add_block(block):
	if(len(block_chain) == 0):
		block["timestamp"] = get_time()
		block["hash"] = generate_hash(block)
	else:
		block["timestamp"] = get_time()
		last_block = block_chain[-1]
		block["last_hash"] = last_block["hash"]
		block["hash"] = generate_hash(block)
	block_chain.append(block)

for c in chain:
	add_block(c)

print(block_chain)