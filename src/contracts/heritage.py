#!/usr/bin/env python3

# Inicialização (Executa no deploy)
if 'owner' not in storage:
    storage['owner'] = msg['sender']
    storage['heir'] = msg['params'].get('heir')
    storage['secret'] = msg['params'].get('secret')
    storage['timeout'] = msg['params'].get('timeout', 0)
    storage['last_seen'] = msg['timestamp']
    storage['status'] = 'ATIVO'
    # BLOCO NOVO: Trava o valor enviado no deploy
    storage['locked_amount'] = msg.get('amount', 0)
    result = f'Contrato de Heranca Ativado com {storage["locked_amount"]} tokens'

# Lógica de Execução
action = msg['params'].get('action')

# PROBLEMA 1: Bloqueia chamadas se já foi resgatado
if storage.get('status') == 'REVELADO':
    result = 'ERRO: Heranca ja foi resgatada e o segredo revelado.'
elif storage.get('status') == 'REVOGADO':
    result = 'ERRO: O contrato ja foi revogado pelo dono.'
elif action == 'ping' and msg['sender'] == storage['owner']:
    storage['last_seen'] = msg['timestamp']
    result = 'Sinal de vida recebido'
elif action == 'revoke' and msg['sender'] == storage['owner']:
    # Nova funcionalidade: Revogação pelo dono
    amount = storage['locked_amount']
    storage['locked_amount'] = 0
    storage['status'] = 'REVOGADO'
    # Sinaliza para a engine realizar o pagamento de volta ao dono
    payout = {'address': storage['owner'], 'amount': amount}
    result = f'Contrato revogado. {amount} devolvido ao dono'
elif action == 'recover' and msg['sender'] == storage['heir']:
    # Calcula diferença de tempo
    diff = msg['timestamp'] - storage['last_seen']
    if diff > storage['timeout']:
        storage['status'] = 'REVELADO'
        # PROBLEMA 2: Libera o valor e limpa o storage
        liberado = storage['locked_amount']
        storage['locked_amount'] = 0
        # Sinaliza para a engine realizar o pagamento ao herdeiro
        payout = {'address': storage['heir'], 'amount': liberado}
        result = f'Segredo: {storage["secret"]} | Valor Liberado: {liberado}'
    else:
        result = f'Ainda nao expirou (faltam {storage["timeout"] - diff:.1f}s)'
