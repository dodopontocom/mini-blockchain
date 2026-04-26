#!/usr/bin/env python3

storage['results'] = storage.get('results', {opt: 0 for opt in msg['params'].get('options', [])})
storage['voters'] = storage.get('voters', [])
opt = msg['params'].get('opt')
if opt:
    if msg['sender'] in storage['voters']:
        result = 'ERRO: Ja votou'
    elif opt not in storage['results']:
        result = 'ERRO: Opcao invalida'
    else:
        storage['results'][opt] += 1
        storage['voters'].append(msg['sender'])
        result = f'Voto computado para {opt}'
else:
    result = 'Votacao Ativa'
