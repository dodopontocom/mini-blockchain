#!/usr/bin/env python3

storage['owner'] = storage.get('owner', msg['sender'])
storage['heir'] = storage.get('heir', msg['params'].get('heir'))
storage['secret'] = storage.get('secret', msg['params'].get('secret'))
storage['timeout'] = storage.get('timeout', msg['params'].get('timeout', 0))
storage['last_seen'] = storage.get('last_seen', msg['timestamp'])
storage['status'] = storage.get('status', 'ATIVO')

action = msg['params'].get('action')
if action == 'ping' and msg['sender'] == storage['owner']:
    storage['last_seen'] = msg['timestamp']
    result = 'Sinal de vida recebido'
elif action == 'recover' and msg['sender'] == storage['heir']:
    if msg['timestamp'] - storage['last_seen'] > storage['timeout']:
        storage['status'] = 'REVELADO'
        result = f'Segredo: {storage["secret"]}'
    else:
        result = 'Ainda nao expirou'
