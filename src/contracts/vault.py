#!/usr/bin/env python3

# Inicialização (Executa no deploy)
if 'balances' not in storage:
    storage['balances'] = {}
    result = 'Vault Ativado'

# Lógica de Execução
sender = msg['sender']
action = msg['params'].get('action')

if msg['amount'] > 0:
    storage['balances'][sender] = storage['balances'].get(sender, 0) + msg['amount']
    # TODO (INTEGRAÇÃO): Enviar 2% de cada depósito para o stake-pool como incentivo
    # stake_pool_fee = msg['amount'] * 0.02
    result = f'Deposito de {msg["amount"]} recebido'
elif action == 'withdraw':
    amt = msg['params'].get('amount', 0)
    if storage['balances'].get(sender, 0) >= amt:
        storage['balances'][sender] -= amt
        result = f'Saque de {amt} realizado'
    else:
        result = 'ERRO: Saldo insuficiente no Vault'
