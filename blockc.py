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
TRANSACTION_DELAY = 1.5
MINING_DELAY = 0.7
BLOCK_DELAY = 2.0
INITIAL_BALANCE = 100.0
DIFFICULTY = 3
TAXA_BASE = 0.15
TAXA_POR_BYTE = 0.01
TAXA_MINIMA = 0.1
INTERVALO_MINERACAO = 15
RECOMPENSA_VAZIO = 0.5  # Recompensa para blocos sem transações
LOCK_FILE = "blockchain.lock"
lock = FileLock(LOCK_FILE)

class Block:
    def __init__(self, index, transactions, previous_hash, nonce, timestamp, tr_count, hash):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.tr_count = tr_count
        self.hash = hash

    @classmethod
    def from_dict(cls, block_dict):
        return cls(
            index=block_dict['index'],
            transactions=block_dict['transactions'],
            previous_hash=block_dict['previous_hash'],
            nonce=block_dict['nonce'],
            timestamp=block_dict['timestamp'],
            tr_count=block_dict.get('tr_count', len(block_dict['transactions'])),
            hash=block_dict['hash']
        )

    def to_dict(self):
        return self.__dict__

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = DIFFICULTY
        self.mining_active = True
        self.load_from_file()
        print("⛓️  Blockchain carregada!" if os.path.exists(DATA_FILE) else "⛓️  Nova blockchain criada!")
        time.sleep(BLOCK_DELAY)
        self.start_auto_mining()
    
    def create_genesis_block(self):
        genesis_block = Block(0, [], "0", 0, time.time(), "0", 0)
        self.chain.append(genesis_block)
        self.save_to_file()

    def load_from_file(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                self.chain = [Block.from_dict(block) for block in data['chain']]
                self.pending_transactions = data['pending_transactions']
        else:
            self.create_genesis_block()

    def save_to_file(self):
        with lock:
            # Manter pending_transactions atualizados
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    existing_data = json.load(f)
                    current_pending = existing_data.get('pending_transactions', [])
            else:
                current_pending = []
            
            # Mesclar transações locais com as do arquivo
            merged_pending = current_pending + self.pending_transactions
            
            data = {
                'chain': [block.to_dict() for block in self.chain],
                'pending_transactions': merged_pending
            }
            
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            self.pending_transactions = []  # Resetar lista local

    def calcular_taxa(self, transaction_data):
        tamanho = sys.getsizeof(json.dumps(transaction_data))
        taxa = TAXA_BASE + (TAXA_POR_BYTE * tamanho)
        return max(taxa, TAXA_MINIMA)

    def add_transaction(self, sender, receiver, amount, signature):
        with lock:
            # Carregar transações existentes
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    pending = data.get('pending_transactions', [])
            else:
                pending = []
            
            # --- CÁLCULO DA TAXA FALTANDO ---
            tx_data = {'sender': sender, 'receiver': receiver, 'amount': amount}
            fee = self.calcular_taxa(tx_data)  # Adicione esta linha
            
            # Adicionar nova transação (agora com fee calculada)
            pending.append({
                'sender': sender,
                'receiver': receiver,
                'amount': amount,
                'fee': fee,  # Agora fee existe!
                'signature': signature
            })
            
            # Salvar atualizado
            data['pending_transactions'] = pending
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)

    def mine_block(self, miner_address):
        # Carregar transações pendentes diretamente do arquivo
        with lock:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    pending_transactions = data['pending_transactions']
            else:
                pending_transactions = []

        total_fees = sum(tx['fee'] for tx in pending_transactions)
        recompensa = max(total_fees, RECOMPENSA_VAZIO)

        # Criar cópia das transações para o bloco
        # block_transactions = pending_transactions.copy()
        # Corrigido (em mine_block()):
        # block_transactions = [tx.copy() for tx in pending_transactions]  # Copia todos os campos
        # Substitua por:
        block_transactions = []
        for tx in pending_transactions:
            new_tx = tx.copy()  # Isso preserva todos os campos (incluindo signature)
            block_transactions.append(new_tx)
        
        # Adicionar recompensa de mineração
        block_transactions.append({
            'sender': 'coinbase',
            'receiver': miner_address,
            'amount': recompensa,
            'fee': 0.0,
            'signature': 'mining_reward'
        })

        # Resto da lógica de mineração...
        last_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            transactions=block_transactions,
            previous_hash=last_block.hash,
            nonce=0,
            timestamp=time.time(),
            tr_count=len(block_transactions),
            hash=""
        )

        print(f"\n⛏️  Minerando bloco #{new_block.index} (Dificuldade: {self.difficulty})")
        start_time = time.time()
        attempts = 0
        
        while self.mining_active:
            new_block.nonce += 1
            attempts += 1
            new_block.hash = self.compute_hash(new_block)
            
            if attempts % 100000 == 0:
                print(f"   🕳️  Tentativa #{attempts:,}... Nonce: {new_block.nonce}")
                
            if new_block.hash.startswith('0' * self.difficulty):
                break

        
        # Atualizar chain e limpar pendentes
        with lock:
            self.chain.append(new_block)
            # Atualizar arquivo com pending_transactions vazio
            data = {
                'chain': [block.to_dict() for block in self.chain],
                'pending_transactions': []
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)

        # self.chain.append(new_block)
        # self.pending_transactions = []
        # self.save_to_file()

        print(f"\n✅ Bloco #{new_block.index} minerado em {time.time() - start_time:.2f}s!")
        print(f"   Hash: {new_block.hash}")
        print(f"   Recompensa: {recompensa:.2f} BTC ({'taxas' if total_fees > 0 else 'bloco vazio'})")

    def compute_hash(self, block):
        block_string = json.dumps({
            'index': block.index,
            'transactions': block.transactions,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'timestamp': block.timestamp
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def calculate_balances(self):
        balances = {}
        for node in nodes.values():
            balances[node.address] = INITIAL_BALANCE
        
        for block in self.chain:
            for tx in block.transactions:
                if tx['sender'] != 'coinbase':
                    balances[tx['sender']] -= tx['amount'] + tx['fee']
                balances[tx['receiver']] += tx['amount']
        
        for tx in self.pending_transactions:
            if tx['sender'] != 'coinbase':
                balances[tx['sender']] -= tx['amount'] + tx['fee']
            balances[tx['receiver']] += tx['amount']
        
        return balances

    def start_auto_mining(self):
        def mining_loop():
            available_miners = []
            while self.mining_active:
                time.sleep(INTERVALO_MINERACAO)
                if nodes and self.mining_active:
                    if not available_miners:
                        # Recria a lista com os nós atuais e embaralha
                        available_miners = list(nodes.values()).copy()
                        random.shuffle(available_miners)
                    # Seleciona o próximo minerador da lista
                    miner = available_miners.pop()
                    print(f"\n🎲 Minerador sorteado: {miner.name}")
                    self.mine_block(miner.address)

        mining_thread = threading.Thread(target=mining_loop, daemon=True)
        mining_thread.start()

class Node:
    def __init__(self, name):
        self.wallet = SigningKey.generate(curve=NIST256p)
        self.address = self.wallet.get_verifying_key().to_string().hex()
        self.name = name

    def send_transaction(self, receiver, amount):
        if self.address == receiver:
            print("🚨 Erro: Não pode enviar para si mesmo!")
            return False
            
        tx_data = {'sender': self.address, 'receiver': receiver, 'amount': amount}
        fee = blockchain.calcular_taxa(tx_data)
        
        tx_data['fee'] = fee
        signature = self.wallet.sign(json.dumps(tx_data).encode()).hex()
        
        # Adicione a transação com todos os campos
        return blockchain.add_transaction(
            sender=self.address,
            receiver=receiver,
            amount=amount,
            signature=signature
        )

# Carregar/Criar nós
if os.path.exists(NODES_FILE):
    with open(NODES_FILE, 'r') as f:
        nodes_data = json.load(f)
        nodes = {name: Node(name) for name in nodes_data}
        for name, node in nodes.items():
            node.address = nodes_data[name]['address']
else:
    nodes = {
        'Alice': Node('Alice'),
        'Bob': Node('Bob'),
        'Charlie': Node('Charlie'),
        'David': Node('David'),
        'Eve': Node('Eve')
    }
    # Gera 50 usuários extras
    for i in range(1, 51):
        name = f"User{i}"
        nodes[name] = Node(name)
        
    with open(NODES_FILE, 'w') as f:
        json.dump({name: {'address': node.address} for name, node in nodes.items()}, f, indent=4)

blockchain = Blockchain()

def show_menu():
    while True:
        print("\n=== Blockchain Menu ===")
        print("1. Listar participantes")
        print("2. Nova transação")
        print("3. Ver blockchain")
        print("4. Ver saldos")
        print("5. Sair")
        
        choice = input("Escolha: ")
        
        if choice == "1":
            print("\nParticipantes:")
            for i, (name, node) in enumerate(nodes.items(), 1):
                print(f"{i}. {name} ({node.address[:8]}...)")

        elif choice == "2":
            try:
                print("\nRemetentes:")
                senders = list(nodes.items())
                for i, (name, _) in enumerate(senders, 1):
                    print(f"{i}. {name}")
                s_idx = int(input("Número do remetente: ")) - 1
                sender = senders[s_idx][1]

                print("\nDestinatários:")
                receivers = list(nodes.items())
                for i, (name, _) in enumerate(receivers, 1):
                    print(f"{i}. {name}")
                r_idx = int(input("Número do destinatário: ")) - 1
                receiver = receivers[r_idx][1]

                amount = float(input("Quantia: "))
                
                if sender.send_transaction(receiver.address, amount):
                    time.sleep(TRANSACTION_DELAY)
            except (ValueError, IndexError):
                print("🚫 Seleção inválida!")

        elif choice == "3":
            print("\n🔗 Blockchain:")
            for block in blockchain.chain:
                print(f"\nBloco #{block.index}")
                print(f"Hash: {block.hash}")
                print(f"Transações ({len(block.transactions)}):")
                for tx in block.transactions:
                    if tx['sender'] == 'coinbase':
                        print(f"  🪙 Mineração → {tx['receiver'][:8]}... (+{tx['amount']:.2f} BTC)")
                    else:
                        print(f"  💸 {tx['sender'][:8]}... → {tx['receiver'][:8]}...")
                        print(f"     Valor: {tx['amount']:.2f} BTC | Taxa: {tx['fee']:.2f} BTC")
            print("⎯"*50)

        elif choice == "4":
            balances = blockchain.calculate_balances()
            print("\n💰 Saldos:")
            for name, node in nodes.items():
                balance = balances.get(node.address, INITIAL_BALANCE)
                print(f"  {name}: {balance:.2f} BTC")
            time.sleep(2)

        elif choice == "5":
            print("\n💾 Salvando dados...")
            blockchain.mining_active = False
            blockchain.save_to_file()
            print("✅ Progresso salvo!")
            os._exit(0)

        else:
            print("🚫 Opção inválida!")

if __name__ == "__main__":
    if sys.stdin.isatty():
        show_menu()
    else:
        print("🚀 Modo serviço ativo (Auto-mining)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            blockchain.mining_active = False
            blockchain.save_to_file()