#!/usr/bin/env python3

import _global
import miniblock
import requests
import json
import time

url_to_add_transaction = 'http://127.0.0.1:5005/add_transaction'
set_flag = 'http://127.0.0.1:5005/set_subtract_flag'
subtr_function_url = 'http://127.0.0.1:5005/apply_subtr_function'

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
        requests.post(set_flag, json = send_flag_state)
        send_to_subtract = {
            "amount": amount,
            "fee": 0.0
        }
        if requests.post(subtr_function_url, json = send_to_subtract):
            self.wallets.append(
                {
                    "blake2b": blake2b,
                    "balance": amount,
                    "private_key": "x"
                }
            )
            requests.post(url_to_add_transaction, json = this_transaction)
            reset_flag_state = {
                    "flag": False
            }
            requests.post(set_flag, json = reset_flag_state)
            return (f"Wallet {len(self.wallets)} created!")
        else:
            return "Wallet not created, not funds in total supply"

