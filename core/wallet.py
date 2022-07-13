#!/usr/bin/env python3

import _global
import miniblock
import requests
import json
import time

class Wallet:

    def __init__(self):
        self.wallets = []
    
    def update_balance(self, amount, sender, receiver, dest_amount):
        for i in self.wallets:
            if (i['blake2b']==sender):
                balance = i['balance']
                i['balance'] = (balance - amount)
            if (i['blake2b']==receiver):
                balance = i['balance']
                i['balance'] = (balance + dest_amount)

    def create_wallet(self, amount):
        t_timestamp = str(time.time())
        cookie = (f"{t_timestamp}_{amount}").encode('utf-8')
        blake2b = ("mini_addr" + _global.sign_blake2(self, cookie))

        this_transaction = {
            "receiver": blake2b,
            "amount": amount,
            "type": "ico",
            "message": "Transaction to a new wallet creation!"
        }
        
        send_flag_state = {
                "flag": True
        }
        requests.post(_global.miniblock_base_url + "set_subtract_flag", json = send_flag_state)
        send_to_subtract = {
            "amount": amount,
            "fee": 0.0
        }
        if requests.post(_global.miniblock_base_url + "apply_subtr_function", json = send_to_subtract):
            self.wallets.append(
                {
                    "blake2b": blake2b,
                    "balance": amount,
                    "private_key": "x"
                }
            )
            requests.post(_global.miniblock_base_url + "add_transaction", json = this_transaction)
            reset_flag_state = {
                    "flag": False
            }
            requests.post(_global.miniblock_base_url + "set_subtract_flag", json = reset_flag_state)
            return (f"Wallet {len(self.wallets)} created!")
        else:
            return "Wallet not created, not funds in total supply"

