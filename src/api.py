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
        from src.blockc import blockchain
        with lock:
            blockchain.load_from_file()
            return [b.to_dict() for b in blockchain.chain]

@api.route('/pending-transactions')
class PendingTransactions(Resource):
    def get(self):
        from src.blockc import blockchain
        with lock:
            blockchain.load_from_file()
            return blockchain.pending_transactions

@api.route('/contracts')
class Contracts(Resource):
    def get(self):
        from src.blockc import blockchain
        with lock:
            blockchain.load_from_file()
            return {
                "contracts": blockchain.contracts,
                "states": blockchain.state
            }

@api.route('/user-contracts/<address>')
class UserContracts(Resource):
    @api.doc(description='Retorna contratos relevantes para um endereço')
    def get(self, address):
        from src.blockc import blockchain
        with lock:
            blockchain.load_from_file()
            relevant_contracts = []
            
            # Coleta todas as transações para buscar histórico e criadores de contratos
            all_txs = []
            contract_creators = {} # {contract_addr: creator_addr}
            for block in blockchain.chain:
                for tx in block.transactions:
                    all_txs.append(tx)
                    if tx.get('type') == 'deploy' and tx.get('contract_address'):
                        contract_creators[tx['contract_address']] = tx['sender']
            
            for contract_addr, state in blockchain.state.items():
                is_relevant = False
                contract_type = "unknown"
                
                # Relevância por ser o criador (quem fez o deploy)
                if contract_creators.get(contract_addr) == address:
                    is_relevant = True

                # Detecta tipo e relevância por estado
                if 'voters' in state:
                    contract_type = "voting"
                    if address in state.get('voters', []):
                        is_relevant = True
                
                if 'owner' in state or 'heir' in state:
                    contract_type = "heritage"
                    if address == state.get('owner') or address == state.get('heir'):
                        is_relevant = True
                
                if 'balances' in state:
                    contract_type = "vault"
                    if address in state.get('balances', {}):
                        is_relevant = True
                
                if 'total_staked' in state:
                    contract_type = "stake_pool"
                    if address in state.get('stakes', {}) or address in state.get('unstake_requests', {}):
                        is_relevant = True
                
                # Se for relevante, adiciona à lista com informações extras
                if is_relevant:
                    # Busca histórico de transações deste contrato (últimas 5)
                    history = []
                    for tx in reversed(all_txs):
                        if tx.get('receiver') == contract_addr or tx.get('contract_address') == contract_addr:
                            history.append({
                                'sender': tx.get('sender'),
                                'type': tx.get('type'),
                                'data': tx.get('data') if tx.get('type') == 'call' else tx.get('data_params'),
                                'timestamp': tx.get('timestamp'),
                                'result': tx.get('execution_result'),
                                'error': tx.get('execution_error')
                            })
                            if len(history) >= 20: break

                    relevant_contracts.append({
                        "address": contract_addr,
                        "type": contract_type,
                        "state": state,
                        "history": history,
                        "timestamp": time.time(),
                        "is_creator": contract_creators.get(contract_addr) == address
                    })
            
            return relevant_contracts

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
                        current_balance -= (float(tx['amount']) + float(tx.get('fee', 0)))
                    if tx['receiver'] == s:
                        current_balance += float(tx['amount'])
                    
                    # NOVO: Considera ganhos vindos de contratos (payouts)
                    if 'payout' in tx and tx['payout']['address'] == s:
                        current_balance += float(tx['payout']['amount'])
                    
                    # NOVO: Se o endereço atual for o contrato, subtrai o payout que ele enviou
                    if 'payout' in tx and tx['receiver'] == s:
                        current_balance -= float(tx['payout']['amount'])
            
            for tx in blockchain_data.get('pending_transactions', []):
                if tx['sender'] == s:
                    current_balance -= (float(tx['amount']) + float(tx.get('fee', 0)))

            total_cost = new_transaction['amount'] + new_transaction['fee']

            if total_cost > current_balance:
                return {"message": f"Saldo insuficiente! Disponível: {current_balance:.2f}"}, 400

            from src.blockc import blockchain
            blockchain.add_transaction(new_transaction)

        return {"message": "Transação adicionada com sucesso!", "transaction": new_transaction}, 201

@api.route('/balances')
class Balances(Resource):
    @api.doc(description='Retorna saldos de todas as carteiras')
    def get(self):
        from src.blockc import blockchain
        with lock:
            blockchain.load_from_file()
            data = {
                'chain': [b.to_dict() for b in blockchain.chain],
                'pending_transactions': blockchain.pending_transactions,
                'contracts': blockchain.contracts,
                'state': blockchain.state
            }
        balances = {}
        INITIAL_BALANCE = 100.0
        
        # 1. Coleta todos os endereços conhecidos do sistema
        all_addresses = set()
        
        # Adiciona endereços do nodes_data.json (todos os usuários registrados)
        nodes = carregar_nodes()
        for node_info in nodes.values():
            all_addresses.add(node_info['address'])

        # Adiciona endereços que apareceram na blockchain (incluindo payouts e coinbase)
        for block in data['chain']:
            for tx in block['transactions']:
                if tx['sender'] != 'coinbase':
                    all_addresses.add(tx['sender'])
                if tx['receiver'] and tx['receiver'] != 'contract_deploy':
                    all_addresses.add(tx['receiver'])
                if 'payout' in tx:
                    all_addresses.add(tx['payout']['address'])
        
        for tx in data.get('pending_transactions', []):
            all_addresses.add(tx['sender'])
            if tx['receiver'] and tx['receiver'] != 'contract_deploy':
                all_addresses.add(tx['receiver'])

        # 2. Inicializa saldos
        for addr in all_addresses:
            balances[addr] = INITIAL_BALANCE
            
        # 3. Processa blocos confirmados
        for block in data['chain']:
            for tx in block['transactions']:
                # Sender paga (se não for coinbase)
                if tx['sender'] != 'coinbase':
                    balances[tx['sender']] -= (float(tx['amount']) + float(tx.get('fee', 0)))
                
                # Receiver recebe (se não for deploy de contrato)
                if tx['receiver'] and tx['receiver'] != 'contract_deploy':
                    balances[tx['receiver']] += float(tx['amount'])
                
                # NOVO: Se houver um payout do contrato, adiciona ao destinatário e subtrai do contrato
                if 'payout' in tx:
                    p_addr = tx['payout']['address']
                    p_amt = float(tx['payout']['amount'])
                    contract_addr = tx['receiver']
                    
                    if p_addr not in balances:
                        balances[p_addr] = INITIAL_BALANCE
                    balances[p_addr] += p_amt
                    
                    if contract_addr in balances:
                        balances[contract_addr] -= p_amt
        
        # 4. Pendentes (bloqueia saldo do sender)
        for tx in data.get('pending_transactions', []):
            s = tx['sender']
            if s not in balances:
                balances[s] = INITIAL_BALANCE
            balances[s] -= (float(tx['amount']) + float(tx.get('fee', 0)))

        return balances

@api.route('/hash-secret')
class HashSecret(Resource):
    @api.doc(description='Gera o hash SHA256 de um segredo')
    def post(self):
        data = request.json
        if not data or 'secret' not in data:
            return {"message": "Campo 'secret' é obrigatório"}, 400
        
        secret = data['secret']
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        
        return {"hash": secret_hash}, 200

@api.route('/verify-hash')
class VerifyHash(Resource):
    @api.doc(description='Verifica se um segredo corresponde a um hash SHA256')
    def post(self):
        data = request.json
        if not data or 'secret' not in data or 'hash' not in data:
            return {"message": "Campos 'secret' e 'hash' são obrigatórios"}, 400
        
        secret = data['secret']
        provided_hash = data['hash']
        computed_hash = hashlib.sha256(secret.encode()).hexdigest()
        
        is_valid = (computed_hash.lower() == provided_hash.lower())
        
        return {
            "valid": is_valid,
            "computed_hash": computed_hash
        }, 200

@api.route('/crack-hash')
class CrackHash(Resource):
    @api.doc(description='Simula um ataque de força bruta didático contra um hash')
    def post(self):
        data = request.json
        target_hash = data.get('hash', '').lower()
        
        # Dicionário de segredos fracos (simulação)
        common_secrets = [
            "123456", "password", "senha", "admin", "ouro", "segredo", 
            "123", "abc", "blockchain", "bitcoin", "minha-senha",
            "Ouro no Jardim", "Ouro esta no jardim"
        ]
        
        # 1. Tenta o dicionário
        for word in common_secrets:
            if hashlib.sha256(word.encode()).hexdigest() == target_hash:
                return {"found": True, "secret": word, "method": "Ataque de Dicionário"}, 200
        
        # 2. Tenta números simples (0-9999)
        for i in range(10000):
            word = str(i)
            if hashlib.sha256(word.encode()).hexdigest() == target_hash:
                return {"found": True, "secret": word, "method": "Força Bruta (Números)"}, 200
                
        return {"found": False, "message": "O segredo é complexo demais para ser quebrado rapidamente."}, 200

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
    if not nodes:
        return render_template('erro.html', mensagem="Nenhum nó encontrado no sistema.")
    
    # Identifica endereços com contratos ativos e conta quantos
    from src.blockc import blockchain
    with lock:
        blockchain.load_from_file()
        contract_counts = {} # {address: count}
        
        # Mapeia criadores de contratos
        contract_creators = {}
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.get('type') == 'deploy' and tx.get('contract_address'):
                    contract_creators[tx['contract_address']] = tx['sender']

        for contract_addr, state in blockchain.state.items():
            involved_addresses = set()
            
            # Criador sempre envolvido
            creator = contract_creators.get(contract_addr)
            if creator: involved_addresses.add(creator)
            
            # Outros envolvidos por estado
            if 'voters' in state:
                for v in state.get('voters', []): involved_addresses.add(v)
            if 'owner' in state: involved_addresses.add(state['owner'])
            if 'heir' in state: involved_addresses.add(state['heir'])
            if 'balances' in state:
                for v in state.get('balances', {}): involved_addresses.add(v)
            if 'total_staked' in state:
                for v in state.get('stakes', {}): involved_addresses.add(v)
                for v in state.get('unstake_requests', {}): involved_addresses.add(v)
            
            for addr in involved_addresses:
                contract_counts[addr] = contract_counts.get(addr, 0) + 1

    # Se o parâmetro ?user=Nome estiver presente, troca o usuário da sessão
    requested_user = request.args.get('user')
    if requested_user in nodes:
        session['user'] = {
            'name': requested_user,
            'address': nodes[requested_user]['address']
        }
    
    # Login padrão se não houver sessão
    if 'user' not in session:
        first_node = list(nodes.keys())[0]
        session['user'] = {
            'name': first_node,
            'address': nodes[first_node]['address']
        }
    
    return render_template('carteira.html', user=session['user'], nodes=nodes, contract_counts=contract_counts)

@app.route('/blockchain')
def blockchain_view():
    return render_template('blockchain.html')

@app.route('/heritage-sim')
def heritage_sim():
    return render_template('heritage_sim.html')

@app.route('/hash-tool')
def hash_tool():
    return render_template('hash_tool.html')

@app.route('/mine', methods=['POST'])
def mine():
    from src.blockc import blockchain
    
    miner_address = session.get('user', {}).get('address', '00000000')
    new_block = blockchain.mine_block(miner_address)
    
    if new_block:
        return jsonify({'status': 'success', 'message': f'Bloco #{new_block.index} minerado!'})
    else:
        return jsonify({'status': 'error', 'message': 'Sem transações para minerar'}), 400

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

@app.route('/chamar-contrato', methods=['POST'])
def chamar_contrato():
    try:
        # Verifica se o usuário está logado
        if 'user' not in session:
            return {'status': 'error', 'message': 'Usuário não autenticado'}, 401

        contract_address = request.form['contract_address']
        action = request.form['action']
        params = json.loads(request.form.get('params', '{}'))
        amount = float(request.form.get('amount', 0))

        # Dados da transação
        sender_address = session['user']['address']
        
        # Usa host_url para ser dinâmico
        api_url = request.host_url.rstrip('/')
        
        # Montagem da transação de chamada
        transacao = {
            'sender': sender_address,
            'receiver': contract_address,
            'amount': amount,
            'type': 'call',
            'data': {'action': action, **params},
            'signature': 'assinatura_mockada'
        }

        # Envio para a API
        response = requests.post(
            f'{api_url}/api/add-transaction',
            json=transacao
        )

        if response.status_code == 201:
            return {'status': 'success', 'message': f'Ação {action} enviada!'}, 201
        
        res_data = response.json()
        return {'status': 'error', 'message': res_data.get('message', 'Erro na API')}, response.status_code

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# ===========================================
#               INICIALIZAÇÃO
# ===========================================
if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
