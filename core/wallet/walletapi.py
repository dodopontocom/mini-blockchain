#!/usr/bin/env python3

from flask import Flask, jsonify, request, session, redirect, url_for, render_template
import wallet
import os

#template dir still not ok when call api from another directory
template_dir = os.path.abspath('../../ui/templates/wallet')
app = Flask(__name__, template_folder=template_dir)

app.config["JSON_SORT_KEYS"] = True

wallet = wallet.Wallet()

@app.route("/create_wallet")
def home():
    _return = wallet.create_wallet(100)
    return render_template("create_wallet.html",
        _return = _return)

@app.route("/get_wallets", methods=["GET"])
def get_wallets():
    response = {
        "wallets": wallet.wallets,
        "wlength": len(wallet.wallets)
    }
    return jsonify(response), 200

@app.route("/update_balance", methods = ["POST"])
def update_balance():
    json = request.get_json()
    amount = json.get("amount")
    sender = json.get("sender")
    receiver = json.get("receiver")
    dest_amount = json.get("dest_amount")
    wallet.update_balance(amount, sender, receiver, dest_amount)
   
    response = {
        "wallets": wallet.wallets,
        "wlength": len(wallet.wallets)
    }
    return jsonify(response), 200
    

if __name__ == "__main__":
    print(__name__)
    app.run(host = "0.0.0.0", port = 6500)
