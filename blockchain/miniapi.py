#!/usr/bin/env python3

import uuid
from flask import Flask, jsonify, request, session, redirect, url_for, render_template
import miniblock
from uuid import uuid4
import time
import sys
import socket
import _global

app = Flask(__name__)
#app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = True

PORT = sys.argv[1]
blockchain = miniblock.Blockchain(PORT)

hostname = socket.gethostname()
uuid_string = str(uuid4()).replace('-', '')


@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : 'Los nodos tenían diferentes cadenas, que han sido todas reemplazadas por la más larga.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message' : 'Todo correcto. La cadena en todos los nodos ya es la más larga.',
                    'actual_chain' : blockchain.chain}
    return jsonify(response), 200

@app.route('/mint_block', methods=['GET'])
def _replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        _response = {'message' : 'Nodes are now replaced.',
                    'new_chain': blockchain.chain}
    else:
        _response = {'message' : 'All good. This node has most long chain',
                    'actual_chain' : blockchain.chain}
    #return jsonify(_response), 200

    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block['hash']
    previous_tstamp = previous_block['timestamp']
    this_time = round(time.time())
    transactions_count = len(blockchain.transactions)
    reward = blockchain.calculate_reward(previous_tstamp, this_time, transactions_count)
    _message = "This is a reward transaction for minting a block!"
    if request.user_agent.browser:
        node_address = f'{request.user_agent.browser}_{uuid_string}_{PORT}'
    else:
        node_address = f'{hostname}_{uuid_string}_{PORT}'
    blockchain.add_transaction(sender = node_address, receiver = "Elisa", amount = reward, message = _message, type = "reward")
    block = blockchain.create_block(previous_hash)

    response = {
        'message': "Congratulation! You've mined a Block",
        'era': block['era'],
        'index': block['index'],
        'hash': block['hash'],
        'proof': block['proof'],
        'time_to_proof': block['time_to_proof'],
        'previous_hash': block['previous_hash'],
        'timestamp': block['timestamp'],
        'transactions_count': block['transactions_count'],
        'transactions': block['transactions'],
        'blake2b': block['blake2b']
    }
    return jsonify(_response, response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {
            'message': "All good, the blockchain is valid"
        }
    else:
        response = {
            'message': "Problem!"
        }
    return jsonify(response), 200

@app.route('/info')
def hello():
    return 'Hello, world! running on %s' % request.host

@app.route("/")
def home():
    return render_template('add_transaction.html')

@app.route("/mint_a_block")
def _home():
    return render_template('mint_a_block.html')


@app.route('/_add_transaction', methods=['GET', 'POST'])
def _add_transaction():
    index = None
    response = None
    if request.form.get('add_transaction'):
        sender = request.form.get('sender')
        if sender == "":
            sender = f'{request.user_agent.browser}_{uuid_string}_{PORT}'
        receiver = request.form.get('receiver')
        amount = request.form.get('amount')
        message = request.form.get('message')
        index = blockchain.add_transaction(sender, receiver, amount, message, "ui-test")
        response = {'message': f'Transaction will be added to Block index: {index}+'}
    if request.form.get('add_and_mint'):
        sender = request.form.get('sender')
        if sender == "":
            sender = f'{request.user_agent.browser}_{uuid_string}_{PORT}'
        receiver = request.form.get('receiver')
        amount = request.form.get('amount')
        message = request.form.get('message')
        index = blockchain.add_transaction(sender, receiver, amount, message, "ui-test")
        response = {'message': f'Transaction added, and Block minted with index: {index}'}
        _replace_chain()

    #return redirect(url_for('_add_transaction')), 201
    return jsonify(response), 201

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['receiver', 'amount', 'message']
    if not all(key in json for key in transaction_keys):
        return 'Not correct elements in the transaction', 400
    if json.get('sender'):
        index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'], json['message'], "standard")
    else:
        node_address = f'{hostname}_{uuid_string}_{PORT}'
        index = blockchain.add_transaction(node_address, json['receiver'], json['amount'], json['message'], "iso")
    response = {'message': f'Transaction will be added to Block index: {index}+'}
    return jsonify(response), 201

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None: 
        return 'No nodes to add', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'All nodes is now connected.',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/latest_blocks', methods = ['GET'])
def latest_blocks():
    bchain = blockchain.chain
    #response = {
    #    'length': len(blockchain.chain)
    #}
    #response = {'message': 'oi'}
    #return jsonify(response), 200
    return render_template("latest_blocks.html", len = len(bchain), bchain = bchain)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = PORT, debug=True)
    #app.run(host = '0.0.0.0', port = PORT, debug=True, threaded=False)
    #app.run(host='192.168.10.7', port= PORT, debug=True, threaded=False)

