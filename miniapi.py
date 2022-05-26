#!/usr/bin/env python3

from flask import Flask, jsonify
import miniblock

app = Flask(__name__)

blockchain = miniblock.Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = previous_block['hash']
    proof, hash = blockchain.proof_of_work(previous_proof)
    #previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash, hash)

    response = {
        'message': "Congratulation!",
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'hash': block['hash']
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

if __name__ == "__main__":
    app.run()