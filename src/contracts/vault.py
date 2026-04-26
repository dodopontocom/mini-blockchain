#!/usr/bin/env python3

storage['balances'] = storage.get('balances', {})
sender = msg['sender']
if msg['amount'] > 0:
    storage['balances'][sender] = storage['balances'].get(sender, 0) + msg['amount']
    result = f'Operacao de Deposito: {msg["amount"]}'
elif msg['params'].get('action') == 'withdraw':
    amt = msg['params'].get('amount', 0)
    if storage['balances'].get(sender, 0) >= amt:
        storage['balances'][sender] -= amt
        result = f'Saque de {amt} realizado.'
    else:
        result = 'ERRO: Saldo insuficiente no Vault'
else:
    result = 'Vault Ready'
