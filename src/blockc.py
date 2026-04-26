import hashlib
import json
import time
import random
import os
import sys
import threading
from ecdsa import SigningKey, NIST256p
from filelock import FileLock

# Configurações
DATA_FILE = "blockchain_data.json"
NODES_FILE = "nodes_data.json"
LOCK_FILE = "blockchain.lock"
lock = FileLock(LOCK_FILE)

DIFFICULTY = 2
TAXA_BASE = 0.15
TAXA_POR_BYTE = 0.01
TAXA_MINIMA = 0.1
INTERVALO_MINERACAO = 5 # Reduzido de 15 para 5 para o runner do GitHub

class Block:
    def __init__(self, index, transactions, previous_hash, nonce, timestamp, state_root=None, hash="", **kwargs):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.state_root = state_root # Hash do estado após este bloco
        self.hash = hash
        
        # Armazena argumentos extras (como tr_count) para compatibilidade
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return self.__dict__

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.state = {} # Smart Contract State: {contract_addr: {storage}}
        self.contracts = {} # {contract_addr: code}
        self.mining_active = True
        self.load_from_file()
        if not self.chain:
            self.create_genesis_block()
        self.start_auto_mining()

    def create_genesis_block(self):
        genesis = Block(0, [], "0", 0, time.time(), self.get_state_hash())
        genesis.hash = self.compute_hash(genesis)
        self.chain.append(genesis)
        self.save_to_file()

    def get_state_hash(self):
        return hashlib.sha256(json.dumps(self.state, sort_keys=True).encode()).hexdigest()

    def load_from_file(self):
        with lock:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.chain = [Block(**b) for b in data['chain']]
                    self.pending_transactions = data.get('pending_transactions', [])
                    self.state = data.get('state', {})
                    self.contracts = data.get('contracts', {})

    def save_to_file(self):
        with lock:
            data = {
                'chain': [b.to_dict() for b in self.chain],
                'pending_transactions': self.pending_transactions,
                'state': self.state,
                'contracts': self.contracts
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)

    def compute_hash(self, block):
        content = json.dumps({
            'index': block.index,
            'transactions': block.transactions,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'state_root': block.state_root
        }, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()

    def process_contracts(self, transactions):
        """Executa a lógica dos contratos nas transações do bloco"""
        for tx in transactions:
            tx_type = tx.get('type', 'transfer')
            
            if tx_type == 'deploy':
                # Cria novo contrato
                code = tx.get('data')
                contract_addr = hashlib.sha256((tx['sender'] + code + str(tx['timestamp'])).encode()).hexdigest()[:40]
                self.contracts[contract_addr] = code
                self.state[contract_addr] = {}
                tx['contract_address'] = contract_addr
                print(f"🚀 Contrato Deployado: {contract_addr}")
                
                # Executa o código imediatamente para inicializar o estado
                storage = self.state[contract_addr]
                msg = {
                    'sender': tx['sender'], 
                    'amount': tx['amount'], 
                    'params': tx.get('data_params', {}), # Parâmetros opcionais de deploy
                    'timestamp': tx.get('timestamp', time.time())
                }
                try:
                    exec_env = {'storage': storage, 'msg': msg, 'result': None}
                    exec(code, {}, exec_env)
                    self.state[contract_addr] = exec_env['storage']
                    tx['execution_result'] = exec_env['result']
                except Exception as e:
                    tx['execution_error'] = str(e)
                    print(f"❌ Erro na Inicialização: {e}")

            elif tx_type == 'call':
                # Executa contrato existente
                contract_addr = tx.get('receiver')
                if contract_addr in self.contracts:
                    code = self.contracts[contract_addr]
                    params = tx.get('data', {})
                    
                    # VM Simples (Restrita)
                    # Injetamos: storage (estado do contrato), msg (detalhes da chamada)
                    storage = self.state.get(contract_addr, {})
                    msg = {
                        'sender': tx['sender'], 
                        'amount': tx['amount'], 
                        'params': params,
                        'timestamp': tx.get('timestamp', time.time())
                    }
                    
                    try:
                        # Ambiente de execução controlado
                        exec_env = {'storage': storage, 'msg': msg, 'result': None}
                        exec(code, {}, exec_env)
                        self.state[contract_addr] = exec_env['storage']
                        tx['execution_result'] = exec_env['result']
                        print(f"⚙️ Contrato Executado: {contract_addr}")
                    except Exception as e:
                        tx['execution_error'] = str(e)
                        print(f"❌ Erro no Contrato: {e}")

    def mine_block(self, miner_address):
        with lock:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    pending = data.get('pending_transactions', [])
            else: pending = []

        if not pending: return

        # Limita a 200 transações por bloco para manter a eficiência sob estresse
        batch = pending[:200]
        remaining = pending[200:]

        # Processa contratos antes de fechar o bloco
        self.process_contracts(batch)
        
        # Coinbase
        total_fees = sum(tx.get('fee', 0) for tx in batch)
        block_transactions = batch.copy()
        block_transactions.append({
            'sender': 'coinbase',
            'receiver': miner_address,
            'amount': 0.5 + total_fees,
            'type': 'reward',
            'signature': 'mining_reward'
        })

        last_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            transactions=block_transactions,
            previous_hash=last_block.hash,
            nonce=0,
            timestamp=time.time(),
            state_root=self.get_state_hash()
        )

        # Proof of Work
        while not new_block.hash.startswith('0' * DIFFICULTY):
            new_block.nonce += 1
            new_block.hash = self.compute_hash(new_block)

        self.chain.append(new_block)
        self.pending_transactions = remaining
        self.save_to_file()
        print(f"📦 Bloco #{new_block.index} minerado com {len(batch)} transações!")

    def start_auto_mining(self):
        def loop():
            while self.mining_active:
                time.sleep(INTERVALO_MINERACAO)
                if os.path.exists(NODES_FILE):
                    with open(NODES_FILE, 'r') as f:
                        nodes = json.load(f)
                        miner = random.choice(list(nodes.values()))['address']
                        self.mine_block(miner)
        threading.Thread(target=loop, daemon=True).start()

# --- Inicialização de Nós ---
if not os.path.exists(NODES_FILE):
    nodes = {'Alice': None, 'Bob': None, 'Charlie': None, 'David': None, 'Eve': None}
    for i in range(1, 51): nodes[f"User{i}"] = None
    node_data = {}
    for name in nodes:
        key = SigningKey.generate(curve=NIST256p)
        node_data[name] = {'address': key.get_verifying_key().to_string().hex()}
    with open(NODES_FILE, 'w') as f: json.dump(node_data, f, indent=4)

blockchain = Blockchain()

if __name__ == '__main__':
    print("💎 Blockchain VM Ativa. Aguardando transações...")
    while True: time.sleep(1)
