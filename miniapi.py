#!/usr/bin/env python3

from flask import Flask, jsonify, request
import miniblock
from uuid import uuid4

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = miniblock.Blockchain()

node_address = str(uuid4()).replace('-', '')

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = previous_block['hash']
    proof, hash = blockchain.proof_of_work(previous_proof)
    #previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = "Elisa", amount = 10, fee = 0.001)
    block = blockchain.create_block(proof, previous_hash, hash)

    response = {
        'message': "Congratulation!",
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'hash': block['hash'],
        'transactions': block['transactions']
    }
    return jsonify(response), 200

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
    transaction_keys = ['sender', 'receiver', 'amount', 'fee']
    if not all(key in json for key in transaction_keys):
        return 'Faltam elementos na transacao', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'], json['amount'])
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
    
if __name__ == "__main__":
    app.run()