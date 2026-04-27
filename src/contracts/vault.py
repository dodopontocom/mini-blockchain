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
    result = f'Deposito de {msg["amount"]} recebido'
elif action == 'withdraw':
    amt = msg['params'].get('amount', 0)
    if storage['balances'].get(sender, 0) >= amt:
        storage['balances'][sender] -= amt
        result = f'Saque de {amt} realizado'
    else:
        result = 'ERRO: Saldo insuficiente no Vault'
