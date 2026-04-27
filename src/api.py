from flask import Flask, request, jsonify, render_template, session, Blueprint
import requests
from flask_restx import Api, Resource, fields
import json
import hashlib
import os
import random
import string
import time

# Commons
from src.commons.config import DATA_FILE, NODES_FILE, TAXA_BASE, TAXA_POR_BYTE, TAXA_MINIMA, LOCK_FILE
from src.commons.helpers import lock, calcular_taxa
from filelock import FileLock

# Inicialização do Flask
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = 'teste123'  # Para sessões

# ===========================================
#               CONFIGURAÇÃO DA API
# ===========================================
api_bp = Blueprint('api', __name__)
api = Api(api_bp,
    version="1.0",
    title="Blockchain API",
    description="API para interagir com a blockchain",
    doc='/docs'  # Documentação em /api/docs
)

app.register_blueprint(api_bp, url_prefix='/api')

# ===========================================
#                MODELOS SWAGGER
# ===========================================
block_model = api.model('Block', {
    'index': fields.Integer,
    'transactions': fields.List(fields.Raw),
    'previous_hash': fields.String,
    'nonce': fields.Integer,
    'timestamp': fields.Float,
    'hash': fields.String,
    'tr_count': fields.Integer
})

transaction_model = api.model('Transaction', {
    'sender': fields.String(required=True),
    'receiver': fields.String(required=True),
    'amount': fields.Float(required=True),
    'fee': fields.Float,
    'signature': fields.String(required=True),
    'type': fields.String,
    'data': fields.Raw,
    'data_params': fields.Raw
})

# ===========================================
#                  HELPERS
# ===========================================
def get_blockchain_data():
    with lock:
        if not os.path.exists(DATA_FILE):
            # Estado inicial se não houver arquivo
            genesis_block = {
                'index': 0,
                'transactions': [],
                'previous_hash': "0",
                'nonce': 0,
                'timestamp': time.time(),
                'hash': "0000" + "0" * 60,
                'tr_count': 0
            }
            data = {
                'chain': [genesis_block],
                'pending_transactions': [],
                'contracts': {},
                'state': {}
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            return data
            
        with open(DATA_FILE, 'r') as f:
            return json.load(f)

def carregar_nodes():
    if not os.path.exists(NODES_FILE):
        return {}
    with open(NODES_FILE, 'r') as f:
        return json.load(f)

# ===========================================
#                 ENDPOINTS
# ===========================================

@api.route('/blocks')
class Blocks(Resource):
    @api.marshal_list_with(block_model)
    def get(self):
        data = get_blockchain_data()
        return data['chain']

@api.route('/pending-transactions')
class PendingTransactions(Resource):
    def get(self):
        data = get_blockchain_data()
        return data.get('pending_transactions', [])

@api.route('/contracts')
class Contracts(Resource):
    def get(self):
        data = get_blockchain_data()
        return {
            "contracts": data.get('contracts', {}),
            "states": data.get('state', {})
        }

@api.route('/add-transaction')
class AddTransaction(Resource):
    @api.doc(description='Adiciona nova transação')
    @api.expect(transaction_model)
    def post(self):
        data = request.json
        
        # Validação básica
        required_fields = ['sender', 'receiver', 'amount', 'signature']
        if not all(field in data for field in required_fields):
            return {"message": "Campos obrigatórios faltando"}, 400

        # Cria transação completa com hash e timestamp
        timestamp = time.time()
        tx_base = {
            'sender': data['sender'],
            'receiver': data['receiver'],
            'amount': data['amount'],
            'type': data.get('type', 'transfer'),
            'data': data.get('data'),
            'data_params': data.get('data_params', {}),
            'signature': data['signature'],
            'timestamp': timestamp
        }
        fee = calcular_taxa(tx_base)
        
        # Gera TXID (Transaction Hash)
        tx_string = json.dumps({**tx_base, 'fee': fee}, sort_keys=True).encode()
        tx_hash = hashlib.sha256(tx_string).hexdigest()

        new_transaction = {
            'tx_hash': tx_hash,
            **tx_base,
            'fee': fee
        }

        # Verificação de saldo otimizada
        with lock:
            blockchain_data = get_blockchain_data()
            
            # Cálculo de saldo simplificado apenas para o sender atual
            current_balance = 100.0 # Saldo inicial
            s = new_transaction['sender']
            
            for block in blockchain_data['chain']:
                for tx in block['transactions']:
                    if tx['sender'] == s:
                        current_balance -= (tx['amount'] + tx.get('fee', 0))
                    if tx['receiver'] == s:
                        current_balance += tx['amount']
            
            for tx in blockchain_data.get('pending_transactions', []):
                if tx['sender'] == s:
                    current_balance -= (tx['amount'] + tx.get('fee', 0))

            total_cost = new_transaction['amount'] + new_transaction['fee']

            if total_cost > current_balance:
                return {"message": f"Saldo insuficiente! Disponível: {current_balance:.2f}"}, 400

            blockchain_data['pending_transactions'].append(new_transaction)
            
            with open(DATA_FILE, 'w') as f:
                json.dump(blockchain_data, f, indent=4)

        return {"message": "Transação adicionada com sucesso!", "transaction": new_transaction}, 201

@api.route('/balances')
class Balances(Resource):
    @api.doc(description='Retorna saldos de todas as carteiras')
    def get(self):
        data = get_blockchain_data()
        balances = {}
        INITIAL_BALANCE = 100.0
        
        # Inicialização de saldos
        for block in data['chain']:
            for tx in block['transactions']:
                s = tx['sender']
                r = tx['receiver']
                
                if s != 'coinbase' and s not in balances:
                    balances[s] = INITIAL_BALANCE
                if r != 'contract_deploy' and r not in balances:
                    balances[r] = INITIAL_BALANCE
        
        # Cálculo de saldos (blocos confirmados)
        for block in data['chain']:
            for tx in block['transactions']:
                if tx['sender'] != 'coinbase':
                    balances[tx['sender']] -= (tx['amount'] + tx.get('fee', 0))
                if tx['receiver'] != 'contract_deploy':
                    balances[tx['receiver']] += tx['amount']
        
        # Pendentes (bloqueia saldo)
        for tx in data.get('pending_transactions', []):
            s = tx['sender']
            if s not in balances:
                balances[s] = INITIAL_BALANCE
            balances[s] -= (tx['amount'] + tx.get('fee', 0))

        return balances

# ===========================================
#               ROTAS DA UI
# ===========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contratos')
def contratos():
    return render_template('contratos.html')

@app.route('/carteira')
def carteira():
    nodes = carregar_nodes()
    # Se não houver nodes, o usuário precisa ser redirecionado ou criado
    if not nodes:
        return render_template('erro.html', mensagem="Nenhum nó encontrado no sistema.")
    
    # Simula login com o primeiro nó se não houver sessão
    if 'user' not in session:
        first_node = list(nodes.keys())[0]
        session['user'] = {
            'name': first_node,
            'address': nodes[first_node]['address']
        }
    
    return render_template('carteira.html', user=session['user'], nodes=nodes)

@app.route('/blockchain')
def blockchain_view():
    return render_template('blockchain.html')

@app.route('/heritage-sim')
def heritage_sim():
    return render_template('heritage_sim.html')

@app.route('/mine', methods=['POST'])
def mine():
    with lock:
        data = get_blockchain_data()
        pending = data.get('pending_transactions', [])
        
        if not pending:
             return jsonify({'status': 'error', 'message': 'Sem transações para minerar'}), 400

        # Carrega contratos e estado existentes
        contracts = data.get('contracts', {})
        state = data.get('state', {})

        # Processa transações de contrato
        for tx in pending:
            tx_type = tx.get('type')
            
            if tx_type == 'deploy':
                code = tx.get('data')
                # Se for apenas o nome, tenta carregar o arquivo
                if code and not '\n' in code and os.path.exists(f"src/contracts/{code}.py"):
                    with open(f"src/contracts/{code}.py", 'r') as f:
                        code = f.read()
                        tx['data'] = code

                contract_addr = hashlib.sha256((tx['sender'] + str(code) + str(tx['timestamp'])).encode()).hexdigest()[:40]
                contracts[contract_addr] = code
                state[contract_addr] = {}
                tx['contract_address'] = contract_addr
                
                # Executa inicialização
                storage = state[contract_addr]
                msg = {'sender': tx['sender'], 'amount': tx['amount'], 'params': tx.get('data_params', {}), 'timestamp': tx.get('timestamp', time.time())}
                try:
                    exec_env = {'storage': storage, 'msg': msg, 'result': None}
                    exec(code, {}, exec_env)
                    state[contract_addr] = exec_env['storage']
                    tx['execution_result'] = exec_env['result']
                except Exception as e:
                    tx['execution_error'] = str(e)

            elif tx_type == 'call':
                contract_addr = tx.get('receiver')
                if contract_addr in contracts:
                    code = contracts[contract_addr]
                    storage = state.get(contract_addr, {})
                    msg = {'sender': tx['sender'], 'amount': tx['amount'], 'params': tx.get('data', {}), 'timestamp': tx.get('timestamp', time.time())}
                    try:
                        exec_env = {'storage': storage, 'msg': msg, 'result': None}
                        exec(code, {}, exec_env)
                        state[contract_addr] = exec_env['storage']
                        tx['execution_result'] = exec_env['result']
                    except Exception as e:
                        tx['execution_error'] = str(e)

        # Atualiza dados da chain
        miner_address = session.get('user', {}).get('address', '00000000')
        last_block = data['chain'][-1] if data['chain'] else {'hash': '0', 'index': -1}
        
        new_block = {
            'index': last_block['index'] + 1,
            'transactions': pending + [{
                'sender': 'coinbase',
                'receiver': miner_address,
                'amount': 0.5 + sum(tx.get('fee', 0) for tx in pending),
                'type': 'reward',
                'signature': 'mining_reward'
            }],
            'previous_hash': last_block['hash'],
            'nonce': random.randint(0, 1000),
            'timestamp': time.time(),
            'tr_count': len(pending) + 1
        }
        
        block_content = json.dumps(new_block, sort_keys=True).encode()
        new_block['hash'] = hashlib.sha256(block_content).hexdigest()
        
        data['chain'].append(new_block)
        data['pending_transactions'] = []
        data['contracts'] = contracts
        data['state'] = state
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    return jsonify({'status': 'success', 'message': f'Bloco #{new_block["index"]} minerado!'})

@app.route('/enviar-transacao', methods=['POST'])
def enviar_transacao():
    try:
        # Verifica se o usuário está logado
        if 'user' not in session:
            return {'status': 'error', 'message': 'Usuário não autenticado'}, 401

        # Carrega todos os nós para validação
        nodes = carregar_nodes()
        receiver_address = request.form['receiver']

        # Validação do destinatário
        if not any(node['address'] == receiver_address for node in nodes.values()):
            return {'status': 'error', 'message': 'Destinatário inválido'}, 400

        # Dados da transação
        sender_address = session['user']['address']
        amount = float(request.form['amount'])
        
        # Verificação de saldo antes de enviar - usa host_url para ser dinâmico
        api_url = request.host_url.rstrip('/')
        balances_response = requests.get(f'{api_url}/api/balances')
        balances = balances_response.json()
        current_balance = balances.get(sender_address, 100.0)

        # Cálculo correto da taxa
        tx_data = {
            'sender': sender_address,
            'receiver': receiver_address,
            'amount': amount
        }
        fee = calcular_taxa(tx_data)

        if (amount + fee) > current_balance:
            return {'status': 'error', 'message': f'Saldo insuficiente! Você tem {current_balance:.2f} BTC, mas o custo total (valor + taxa) é {(amount + fee):.2f} BTC'}, 400

        # Montagem da transação
        transacao = {
            'sender': sender_address,
            'receiver': receiver_address,
            'amount': amount,
            'fee': fee,
            'signature': 'assinatura_mockada'
        }

        # Envio para a API
        response = requests.post(
            f'{api_url}/api/add-transaction',
            json=transacao
        )

        if response.status_code == 201:
            return {'status': 'success', 'message': 'Transação enviada!'}, 201
        
        # Padroniza resposta de erro da API
        res_data = response.json()
        return {'status': 'error', 'message': res_data.get('message', 'Erro na API')}, response.status_code

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# ===========================================
#               INICIALIZAÇÃO
# ===========================================
if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
