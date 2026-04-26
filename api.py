from flask import Flask, request, jsonify, render_template, session, Blueprint
import requests
from flask_restx import Api, Resource, fields
from filelock import FileLock
import json
import hashlib
import os
import random
import string
import time

# Configurações
DATA_FILE = "blockchain_data.json"
LOCK_FILE = "blockchain.lock"
lock = FileLock(LOCK_FILE)
TAXA_BASE = 0.15
TAXA_POR_BYTE = 0.01
TAXA_MINIMA = 0.1
NODES_FILE = "nodes_data.json"

# Inicialização do Flask
app = Flask(__name__, template_folder='templates')
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
    'type': fields.String(description='transfer, deploy, call'),
    'data': fields.Raw(description='Código do contrato ou parâmetros da chamada'),
    'fee': fields.Float,
    'signature': fields.String(required=True)
})

# ===========================================
#               FUNÇÕES AUXILIARES
# ===========================================
def carregar_nodes():
    """Carrega e valida os nós do arquivo"""
    try:
        with lock:
            with open(NODES_FILE, 'r') as f:
                nodes = json.load(f)
                
                # Validação da estrutura
                for name, data in nodes.items():
                    if 'address' not in data:
                        raise ValueError(f"Nó {name} não tem endereço válido")
                
                return nodes
                
    except Exception as e:
        print(f"Erro crítico ao carregar nós: {str(e)}")
        raise
        
def calcular_taxa(transaction_data):
    tamanho = len(json.dumps(transaction_data))
    taxa = TAXA_BASE + (TAXA_POR_BYTE * tamanho)
    return max(taxa, TAXA_MINIMA)

def get_blockchain_data():
    with lock:
        if not os.path.exists(DATA_FILE):
            return {"chain": [], "pending_transactions": []}
        
        with open(DATA_FILE, 'r') as f:
            return json.load(f)

# ===========================================
#               ENDPOINTS DA API
# ===========================================
@api.route('/state')
class State(Resource):
    @api.doc(description='Retorna o estado global de todos os Smart Contracts')
    def get(self):
        with lock:
            if not os.path.exists(DATA_FILE): return {}
            with open(DATA_FILE, 'r') as f:
                return json.load(f).get('state', {})

@api.route('/blocks')
class Blocks(Resource):
    @api.doc(description='Lista todos os blocos da blockchain')
    @api.marshal_list_with(block_model)
    def get(self):
        data = get_blockchain_data()
        return data['chain']

@api.route('/blocks/<int:index>')
class BlockDetail(Resource):
    @api.doc(description='Retorna detalhes de um bloco específico')
    @api.marshal_with(block_model)
    def get(self, index):
        data = get_blockchain_data()
        if index < len(data['chain']):
            return data['chain'][index]
        api.abort(404, "Bloco não encontrado")

@api.route('/pending-transactions')
class PendingTransactions(Resource):
    @api.doc(description='Lista transações pendentes')
    @api.marshal_list_with(transaction_model)
    def get(self):
        data = get_blockchain_data()
        return data['pending_transactions']

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
                for field in ['sender', 'receiver']:
                    if tx[field] not in balances:
                        balances[tx[field]] = INITIAL_BALANCE
        
        # Cálculo de saldos (blocos confirmados)
        for block in data['chain']:
            for tx in block['transactions']:
                if tx['sender'] != 'coinbase':
                    balances[tx['sender']] -= tx['amount'] + tx.get('fee', 0)
                balances[tx['receiver']] += tx['amount']
        
        # Subtrair transações pendentes do saldo do remetente
        for tx in data.get('pending_transactions', []):
            sender = tx['sender']
            if sender != 'coinbase':
                if sender not in balances:
                    balances[sender] = INITIAL_BALANCE
                balances[sender] -= tx['amount'] + tx.get('fee', 0)
        
        return balances

@api.route('/contracts')
class Contracts(Resource):
    @api.doc(description='Retorna todos os contratos (código e estado)')
    def get(self):
        with lock:
            if not os.path.exists(DATA_FILE): return {}
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return {
                    "contracts": data.get('contracts', {}),
                    "states": data.get('state', {})
                }

# ===========================================
#               FRONT-END
# ===========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contratos')
def contratos_view():
    return render_template('contratos.html')

@app.route('/carteira')
def carteira():
    # Carrega todos os nós
    try:
        nodes = carregar_nodes()
    except FileNotFoundError:
        return render_template('erro.html', mensagem="Arquivo de nós não encontrado!")

    # Sincroniza dados do usuário se ele já estiver na sessão
    if 'user' in session:
        name = session['user']['name']
        if name in nodes:
            session['user']['address'] = nodes[name]['address']
        else:
            session.pop('user') # Usuário não existe mais

    # Seleciona um nó aleatório se não houver usuário
    if 'user' not in session:
        if not nodes:
            return render_template('erro.html', mensagem="Nenhum usuário cadastrado!")
            
        user_name, user_data = random.choice(list(nodes.items()))
        session['user'] = {
            'name': user_name,
            'address': user_data['address']
        }

    return render_template('carteira.html')

@app.route('/blockchain')
def blockchain_view():
    return render_template('blockchain.html')

@app.route('/mine', methods=['POST'])
def mine():
    with FileLock(LOCK_FILE):
        data = get_blockchain_data()
        pending = data.get('pending_transactions', [])
        
        # Seleciona um minerador aleatório (ou o usuário logado)
        miner_address = session.get('user', {}).get('address', '00000000')
        
        # Lógica simplificada de mineração para a API
        if not data['chain']:
            # Genesis se não existir
            last_block_hash = "0"
            index = 0
        else:
            last_block = data['chain'][-1]
            last_block_hash = last_block['hash']
            index = len(data['chain'])
        
        # Cálculo de taxas
        total_fees = sum(tx.get('fee', 0) for tx in pending)
        recompensa = max(total_fees, 0.5)
        
        # Adiciona coinbase
        block_transactions = pending.copy()
        block_transactions.append({
            'sender': 'coinbase',
            'receiver': miner_address,
            'amount': recompensa,
            'fee': 0.0,
            'signature': 'mining_reward'
        })
        
        new_block = {
            'index': index,
            'transactions': block_transactions,
            'previous_hash': last_block_hash,
            'nonce': random.randint(0, 1000),
            'timestamp': float(hashlib.sha256(str(random.random()).encode()).hexdigest()[:8], 16) / 10**10, # Mock timestamp
            'tr_count': len(block_transactions),
            'hash': ''
        }
        
        # Hash do bloco (simplificado para não travar a API)
        block_content = json.dumps(new_block, sort_keys=True).encode()
        new_block['hash'] = hashlib.sha256(block_content).hexdigest()
        
        data['chain'].append(new_block)
        data['pending_transactions'] = []
        
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
        
        # Verificação de saldo antes de enviar
        balances_response = requests.get('http://localhost:5000/api/balances')
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
            'http://localhost:5000/api/add-transaction',
            json=transacao
        )

        if response.status_code == 201:
            return {'status': 'success', 'message': 'Transação enviada!'}, 201
        
        return response.json(), response.status_code

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# ===========================================
#               INICIALIZAÇÃO
# ===========================================
if __name__ == '__main__':
    app.run(debug=False, port=5000, threaded=True)