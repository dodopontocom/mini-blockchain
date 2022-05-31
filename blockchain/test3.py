#!/usr/bin/env python3

import time
import hashlib
import json
from urllib.parse import urlparse
import requests
from uuid import uuid4
from flask import Flask, jsonify, request
from hashlib import blake2b
from hmac import compare_digest

f = open('nodes.json')
data = json.load(f)
for (v) in data['nodes']:
    print(str(v))
    
    
    # nodes = json.get('nodes')
    # if nodes is None: 
    # return "No nodes to add"
    # for node in nodes:
    # self.add_node(node)
    # response = {'message' : 'Todos los nodos han sido conectados. La cadena de Jbcoins contiene ahora los nodos siguientes: ',
    #         'total_nodes': list(nodes)}
    # return jsonify(response), 201