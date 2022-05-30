#!/usr/bin/env python3

import time
import hashlib
import json
from urllib.parse import urlparse
import requests
from uuid import uuid4
from hashlib import blake2b

ERA = "mini"
ZEROS = "0000"
GENESIS_HASH = str(uuid4()).replace('-', '')
SECRET_KEY = "sometextheretogeneraterandomsecret".encode()
AUTH_SIZE = 32

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        #self.create_block(proof = 1, time_to_proof = 0, hash = f'{ZEROS}{GENESIS_HASH}', previous_hash = "big_bang_minus_one")
        self.create_block(previous_hash = "big_bang_minus_one")
        self.nodes = set()

    def create_block(self, previous_hash):
        block = {
            'era': ERA,
            'index': len(self.chain) + 1,
            'previous_hash': previous_hash,
            'timestamp': str(round(time.time())),
            'transactions_count': len(self.transactions),
            'transactions': self.transactions,
        }
        self.transactions = []
        #self.chain.append(block)
        self.chain.append(self.hash("sha", block))
        #block['hash'] = self.hash("sha", block)
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    def hash(self, type, block):
        new_proof = 1
        check_proof = False
        init_proof = time.time()
        if type == "sha":
            while check_proof is False:
                block['proof'] = new_proof
                hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
                if hash[:len(ZEROS)] == ZEROS:
                    check_proof = True
                    done_proof = time.time()
                    block['hash'] = hash
                    block['proof'] = new_proof
                    block['time_to_proof'] = round((done_proof - init_proof),10)
                else:
                    new_proof += 1
        if type == "blake":
            while check_proof is False:
                h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
                h.update(json.dumps(block).encode())
                hash = h.hexdigest()
                if hash[:len(ZEROS)] == ZEROS:
                    check_proof = True
                    done_proof = time.time()
                    block['hash'] = hash
                    block['proof'] = new_proof
                    block['time_to_proof'] = round((done_proof - init_proof),10)
                else:
                    new_proof += 1
        return block

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            #if block['previous_hash'] != self.hash(previous_block):
            if block['previous_hash'] != previous_block['hash']:
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:len(ZEROS)] != ZEROS:
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount, fee, type):
        self.transactions.append(
            {
                'sender': sender,
                'receiver': receiver, 
                'amount': amount,
                'fee': fee,
                'type': type,
                't_timestamp': str(round(time.time()))
            }
        )
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain: 
            self.chain = longest_chain
            return True
        return False

    #TODO come out with a more elaborate reward calculation
    def calculate_reward(self, previous_block_tstamp, just_mined_block_tstamp):
        good = 12.0
        ok = 8.0
        if (int(just_mined_block_tstamp) - int(previous_block_tstamp)) < 400:
            return str(good)
        else:
            return str(ok)

    #TODO function to add transaction confirmations
        # hint comes from node replication/updates

    #TODO improve fees (add calculation to it)
        # maybe use time_to_proof element

    #TODO how to create json for multiple transactions and add them accordly

    #TODO the current global variable must come from configuration/definitions separated file!
