#!/usr/bin/env python3
# voting smart contract
# Inicialização (Executa no deploy)
if 'results' not in storage:
    options = msg['params'].get('options', [])
    storage['results'] = {opt: 0 for opt in options}
    storage['voters'] = []
    result = 'Votacao Iniciada'

# Lógica de Execução
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
