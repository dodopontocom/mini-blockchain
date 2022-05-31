#!/usr/bin/env python3

from flask import Flask, jsonify, request
import miniblock
from uuid import uuid4
import time
import sys
import socket

app = Flask(__name__)
#app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = True

blockchain = miniblock.Blockchain()

hostname = socket.gethostname()
uuid_string = str(uuid4()).replace('-', '')
node_address = f'{hostname}_{uuid_string}'
PORT = sys.argv[1]

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

@app.route('/mine_block', methods=['GET'])
def _replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        _response = {'message' : 'Los nodos tenían diferentes cadenas, que han sido todas reemplazadas por la más larga.',
                    'new_chain': blockchain.chain}
    else:
        _response = {'message' : 'Todo correcto. La cadena en todos los nodos ya es la más larga.',
                    'actual_chain' : blockchain.chain}
    #return jsonify(_response), 200

    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block['hash']
    previous_tstamp = previous_block['timestamp']
    this_time = round(time.time())
    transactions_count = len(blockchain.transactions)
    reward = blockchain.calculate_reward(previous_tstamp, this_time, transactions_count)
    blockchain.add_transaction(sender = node_address, receiver = "Elisa", amount = reward, fee = 0.0, type = "reward")
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

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['receiver', 'amount', 'fee']
    if not all(key in json for key in transaction_keys):
        return 'Elementos incorretos na transacao', 400
    if json.get('sender'):
        index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'], json['fee'], "standard")
    else:
        index = blockchain.add_transaction(node_address, json['receiver'], json['amount'], json['fee'], "iso")
    response = {'message': f'Transaction adicionada ao Block {index}'}
    return jsonify(response), 201

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None: 
        return 'No hay nodos para añadir', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'Todos los nodos han sido conectados. La cadena de Jbcoins contiene ahora los nodos siguientes: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201
  
if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = PORT)

