#!/usr/bin/env python3

import time
from datetime import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests
from uuid import uuid4
from hashlib import blake2b
import _global
from hmac import compare_digest
import cryptocode

class Blockchain:
    
    def __init__(self, port):
        self.total_supply = _global.TSUPPLY
        self.initial_supply = _global.INIT_SUPPLY
        self.subtrac_frunction_has_been_called = False
        self.wallet_wallet_tx = False
        self.port = port
        self.chain = []
        self.transactions = []
        self.nodes = set()

        self.get_all_wallets_balance_and_subtract_in_t_supply()
        
        ##########################################
        #self.connect_nodes()
        ##########################################

        # if _global._has_collection(name = _global.collection_name):
        #     print("database has blocks previously added")
        #     cursor = _global._return_collection_no_id(_global.db_name, _global.collection_name)
        #     print("Retrieving blockchain from MongoDB...")
        #     for document in cursor:
        #         self.add_from_db(block = document)
        # elif not self.replace_chain():
        print("Let there be Block!!! Creating Genesis Block!!!")
        self.create_block(previous_hash = "big_bang_minus_one")
    
    def get_all_wallets_balance_and_subtract_in_t_supply(self):
        get_all_balance = []
        response = requests.get(_global.get_wallet_api_url).text
        r = json.loads(response)
        for i in r['wallets']:
            get_all_balance.append(i['balance'])
        #total_balance = "sum of all balances"
        total_balance = 0
        for i in range(len(get_all_balance)):
            total_balance = total_balance + get_all_balance[i]
        print(f"total balance among wallets: {total_balance}")
        self.initial_supply = (self.initial_supply - total_balance)        
    
    def if_wallet_to_wallet_flag(self, flag):
        self.wallet_wallet_tx = flag
    
    def set_function_has_been_called(self, flag):
        self.subtrac_frunction_has_been_called = flag
    
    def subtract_supply(self, amount, fee):
        if not self.wallet_wallet_tx:
            if not self.subtrac_frunction_has_been_called:
                if ((amount + fee) <= self.initial_supply):
                    self.initial_supply = (self.initial_supply - amount - fee)
                    print(f"----------------------- {self.initial_supply}")
                    self.subtrac_frunction_has_been_called = True
                    return True
                else:
                    return False
            else:
                self.subtrac_frunction_has_been_called = False
                return True
        else:
            self.wallet_wallet_tx = False
            return True

    def connect_nodes(self):
        f = open("nodes.json")
        data = json.load(f)

        port = self.port
        for (v) in data["nodes"]:
            if v is None:
                return "No nodes to add"
            if v.split(":")[2] != port:
                parsed_url = urlparse(str(v))
                self.nodes.add(parsed_url.netloc)
        print("nodes: " + str(list(self.nodes)))

    def add_from_db(self, block):
        self.block = block
        self.chain.append(block)
        return block

    def create_block(self, previous_hash):
        cookie = json.dumps(self.transactions).encode('utf-8')
        sig = _global.sign_blake2(self, cookie)
        tx_encoded = cryptocode.encrypt(str(cookie), _global.SECRET_KEY)
        if _global.verify_disgest(self, json.dumps(self.transactions).encode(), sig):
            block = {
                "era": _global.ERA,
                "index": len(self.chain) + 1,
                "previous_hash": previous_hash,
                "timestamp": str(round(time.time())),
                "timestamp_pretty": str(datetime.fromtimestamp(round(time.time())).utcnow()).split(".")[0] + "Z",
                "transactions_count": len(self.transactions),
                "transactions_hash": self.transactions,
            }
            self.transactions = []
            self.subtrac_frunction_has_been_called = False
            self.chain.append(self.hash("sha", block))
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    def hash(self, type, block):
        new_proof = 1
        check_proof = False
        init_proof = time.time()
        if type == "sha":
            while check_proof is False:
                block["proof"] = new_proof
                hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
                if hash[:len(_global.ZEROS)] == _global.ZEROS:
                    check_proof = True
                    done_proof = time.time()
                    block["hash"] = hash
                    block["proof"] = new_proof
                    block["time_to_proof"] = round((done_proof - init_proof),10)

                    h = blake2b(digest_size=_global.AUTH_SIZE, key=_global.SECRET_KEY.encode())
                    h.update(json.dumps(block).encode())
                    block["blake2b"] = h.hexdigest()
                else:
                    new_proof += 1
        return block

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != previous_block["hash"]:
                return False
            previous_block = block
            block_index += 1
        return True

    def check_sender(self, sender, amount, fee, type):
        response = requests.get(_global.get_wallet_api_url).text
        s = json.loads(response)
        for i in s['wallets']:
            if (i['blake2b']==sender):
                balance = (i['balance'])
                if balance >= (amount + fee):
                    return True
                else:
                    return False
        if type == "reward" or type == "iso" or type == "ico" or type == "standard" or type == "ui-test":
            if self.subtract_supply(amount, fee):
                return True
            else:
                return False
        else:
            return False

    def check_receiver(self, receiver, amount, fee, type):
        response = requests.get(_global.get_wallet_api_url).text
        r = json.loads(response)
        for i in r['wallets']:
            if (i['blake2b']==receiver):
                balance = (i['balance'])
                if self.subtract_supply(amount, fee):
                    return True
                else:
                    return False

        if type == "reward" or type == "iso" or type == "ico" or type == "standard" or type == "ui-test":
            if self.subtract_supply(amount, fee):
                return True
            else:
                return False
        else:
            return False

    def add_transaction(self, sender, receiver, amount, message, type, index_ref):
        
        previous_block = self.get_previous_block()
        if type == "reward" or type == "iso" or type == "ico":
            fee = 0.0
        else:
            fee = float(self.calculate_fee(amount))
        if self.check_sender(sender = sender, amount = amount, fee = fee, type = type):
            if self.check_receiver(receiver = receiver, amount = amount, fee = fee, type = type):

                _post = {
                    "amount": (amount + fee),
                    "sender": sender,
                    "receiver": receiver,
                    "dest_amount": amount
                }
                if type != "ico":
                    requests.post("http://127.0.0.1:6500/update_balance", json = _post)
                #return (f"Wallet {len(self.wallets)} created!")

                t_timestamp = str(round(time.time()))
                tx = blake2b(digest_size=_global.AUTH_SIZE, key=_global.SECRET_KEY.encode())
                to_hex = f"{message}_{t_timestamp}"
                tx.update((to_hex).encode())
                transaction_blake2b = tx.hexdigest()
                
                self.transactions.append(
                    {
                        "transaction_blake2b": transaction_blake2b,
                        "sender": sender,
                        "receiver": receiver, 
                        "amount": amount,
                        "index_ref": index_ref,
                        "message": message,
                        "fee": fee,
                        "type": type,
                        "t_timestamp": t_timestamp,
                        "t_timestamp_pretty": str(datetime.fromtimestamp(round(time.time())).utcnow()).split(".")[0] + "Z"
                    }
                )
                self.subtrac_frunction_has_been_called = False
                return previous_block["index"] + 1
            else:
                return False
        else:
            False

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        port = self.port
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            if node.split(":")[1] != port:
                try:
                    response = requests.get(f"http://{node}/get_chain")
                    if response.status_code == 200:
                        length = response.json()["length"]
                        chain = response.json()["chain"]
                        if length > max_length and self.is_chain_valid(chain):
                            max_length = length
                            longest_chain = chain
                except requests.exceptions.ConnectionError:
                    print("except from miniblock: status code different from 200, probably nodes in the list are not online!")
                    pass
        if longest_chain: 
            self.chain = longest_chain
            return True
        return False

    def calculate_reward(self, previous_block_tstamp, just_minted_block_tstamp, transactions_count):
        if transactions_count > _global.high_transaction_count:
            good = _global.high_transaction_count_good_reward
            ok = _global.high_transaction_count_ok_reward
        else:
            good = _global.good_reward
            ok = _global.ok_reward
        if (int(just_minted_block_tstamp) - int(previous_block_tstamp)) < _global.proof_speed:
            return str(good)
        else:
            return str(ok)

    #TODO function to add transaction confirmations
        # hint comes from node replication/updates

    #TODO improve fees (add calculation to it)
        # maybe use time_to_proof element
        # cardano uses babel fees (whats that?)
    def calculate_fee(self, amount):
        return str(round(float(amount) * float(0.18)/float(100),3))

    #TODO how to create json for multiple transactions and add them accordly
