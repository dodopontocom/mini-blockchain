#!/usr/bin/env python3

import _global
import miniblock
import requests

url = 'http://127.0.0.1:5005/add_transaction'

class Wallet:

    def __init__(self):
        print("the wallet")
        self.blockchain = miniblock.Blockchain(port = 6500)
        self.wallets = []
        
    def create_wallet(self, amount):
        print("create wallet")
        blake2b = "axxxBC"
        
        self.wallets.append(
            {
                "blake2b": blake2b,
                "balance": amount,
                "private_key": "x"
            }
        )
        
        this_transaction = {
            "receiver": blake2b,
            "amount": amount,
            "message": "Transaction to a new wallet creation!"
        }
        requests.post(url, json = this_transaction)
        
        return self.blockchain.subtract_supply(amount)

    def give_reward_on_creation(self):
        print("Reward for creating a miniblock wallet")
