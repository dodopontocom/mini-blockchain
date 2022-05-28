#!/usr/bin/env python3

import time
import hashlib
import json
from urllib.parse import urlparse
import requests

ERA = "mini"

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, hash = "0000", previous_hash = "0000")
        self.nodes = set()

    def create_block(self, proof, previous_hash, hash):
        block = {
            'era': ERA,
            'index': len(self.chain) + 1,
            'hash': hash,
            'proof': proof,
            'previous_hash': previous_hash,
            'timestamp': str(round(time.time())),
            'transactions_count': len(self.transactions),
            'transactions': self.transactions,
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation
    
    def hash(self, block):
        #encoded_block = json.dumps(block, sort_keys = True).encode()
        encoded_block = json.dumps(block).encode()
        return hashlib.sha256(encoded_block).hexdigest()

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
            if hash_operation[:4] != "0000":
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

    #TODO recognize when transaction is from a node, reward or user to user

