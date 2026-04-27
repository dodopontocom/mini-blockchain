import json
import random
import time
import os
import sys

# Commons
from src.commons.config import DATA_FILE, NODES_FILE
from src.commons.helpers import lock, calcular_taxa

# Configurações
INTERVALO_TRANSACOES = 30  # Reduzido para testes

class TransactionSimulator:
    def __init__(self):
        self.nodes = self.carregar_nodes()
        self.simulation_active = True

    def carregar_nodes(self):
        with lock:
            if not os.path.exists(NODES_FILE):
                print("Erro: Arquivo de nós não encontrado!")
                sys.exit(1)
            
            with open(NODES_FILE, 'r') as f:
                return json.load(f)

    def calcular_saldo_seguro(self, endereco):
        with lock:
            if not os.path.exists(DATA_FILE):
                return 100.0
            
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            
            saldo = 100.0
            # Processar blockchain
            for block in data['chain']:
                for tx in block['transactions']:
                    if tx['sender'] == endereco:
                        saldo -= tx['amount'] + tx.get('fee', 0)
                    if tx['receiver'] == endereco:
                        saldo += tx['amount']
            
            # Processar pendentes
            for tx in data['pending_transactions']:
                if tx['sender'] == endereco:
                    saldo -= tx['amount'] + tx.get('fee', 0)
                if tx['receiver'] == endereco:
                    saldo += tx['amount']
            
            return saldo

    def criar_transacao_valida(self):
        try:
            # Selecionar participantes
            all_nodes = list(self.nodes.items())
            if len(all_nodes) < 2:
                return None
                
            sender_name, sender_data = random.choice(all_nodes)
            receiver_name, receiver_data = random.choice([n for n in all_nodes if n[0] != sender_name])
            
            sender_address = sender_data['address']
            receiver_address = receiver_data['address']

            # Calcular saldo considerando taxas
            saldo_disponivel = self.calcular_saldo_seguro(sender_address)
            
            if saldo_disponivel <= 0.2:  # Margem de segurança
                return None
                
            # Gerar transação
            valor = round(random.uniform(0.1, saldo_disponivel * 0.5), 2)
            tx_data = {
                'sender': sender_address,
                'receiver': receiver_address,
                'amount': valor
            }
            
            # Calcular taxa
            fee = calcular_taxa(tx_data)
            
            if (valor + fee) > saldo_disponivel:
                return None
                
            return {
                'sender': sender_address,
                'receiver': receiver_address,
                'amount': valor,
                'fee': fee,
                'signature': f"simulated_sign_{random.randint(1000,9999)}"  # NOVO CAMPO
            }
            
        except Exception as e:
            print(f"Erro ao criar transação: {str(e)}")
            return None

    def adicionar_transacao_segura(self, transacao):
        with lock:
            try:
                # Ler dados atuais
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                else:
                    data = {'chain': [], 'pending_transactions': []}
                
                # Adicionar nova transação
                data['pending_transactions'].append(transacao)
                
                # Escrever de volta
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=4)
                
                required_fields = ['sender', 'receiver', 'amount', 'fee', 'signature']
                if not all(field in transacao for field in required_fields):
                    print("🚨 Transação inválida: campos faltando!")
                    return False
                
                return True
            except Exception as e:
                print(f"Erro ao adicionar transação: {str(e)}")
                return False

    def simular(self):
        print("🚀 Iniciando simulador de transações inteligente")
        print("📌 Monitorando saldos em tempo real")
        print(f"⏰ Intervalo de transações: {INTERVALO_TRANSACOES}s\n")
        
        try:
            while self.simulation_active:
                transacao = self.criar_transacao_valida()
                
                if transacao:
                    if self.adicionar_transacao_segura(transacao):
                        print(f"\n💸 Transação simulada adicionada:")
                        print(f"   De: {[k for k,v in self.nodes.items() if v['address'] == transacao['sender']][0]}")
                        print(f"   Para: {[k for k,v in self.nodes.items() if v['address'] == transacao['receiver']][0]}")
                        print(f"   Valor: {transacao['amount']:.2f} BTC")
                        print(f"   Taxa: {transacao['fee']:.2f} BTC")
                        print(f"   Saldo remetente: {self.calcular_saldo_seguro(transacao['sender']):.2f} BTC")
                else:
                    print("\n⏭️  Saldos insuficientes para transação simulada")
                
                time.sleep(INTERVALO_TRANSACOES)
                
        except KeyboardInterrupt:
            print("\n🔌 Desligando simulador...")
            self.simulation_active = False

if __name__ == "__main__":
    simulator = TransactionSimulator()
    simulator.simular()