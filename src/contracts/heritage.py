#!/usr/bin/env python3

# Inicialização (Executa no deploy)
if 'owner' not in storage:
    storage['owner'] = msg['sender']
    storage['heir'] = msg['params'].get('heir')
    storage['secret'] = msg['params'].get('secret')
    storage['timeout'] = msg['params'].get('timeout', 0)
    storage['last_seen'] = msg['timestamp']
    storage['status'] = 'ATIVO'
    result = 'Contrato de Heranca Ativado'

# Lógica de Execução
action = msg['params'].get('action')

if action == 'ping' and msg['sender'] == storage['owner']:
    storage['last_seen'] = msg['timestamp']
    result = 'Sinal de vida recebido'
elif action == 'recover' and msg['sender'] == storage['heir']:
    # Calcula diferença de tempo
    diff = msg['timestamp'] - storage['last_seen']
    if diff > storage['timeout']:
        storage['status'] = 'REVELADO'
        result = f'Segredo: {storage["secret"]}'
    else:
        result = f'Ainda nao expirou (faltam {storage["timeout"] - diff:.1f}s)'
