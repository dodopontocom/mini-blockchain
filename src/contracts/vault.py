#!/usr/bin/env python3

# Inicialização (Executa no deploy)
if 'balances' not in storage:
    storage['balances'] = {}
    result = 'Vault Ativado'

# Lógica de Execução
sender = msg['sender']
action = msg['params'].get('action')

if msg['amount'] > 0:
    # INTEGRAÇÃO: Tirar 2% do depósito para o stake-pool como incentivo
    fee = msg['amount'] * 0.02
    net_amount = msg['amount'] - fee
    
    # O saldo do usuário no Vault agora é o valor líquido (98%)
    storage['balances'][sender] = storage['balances'].get(sender, 0) + net_amount
    
    # Procura por um contrato de stake_pool para enviar a taxa
    for addr, state in all_states.items():
        if 'total_staked' in state: 
            if state['total_staked'] > 0:
                state['reward_index'] += fee / state['total_staked']
            else:
                state['pending_rewards'] = state.get('pending_rewards', 0.0) + fee
            
            # Registra o payout para a contabilidade da blockchain
            payout = {'address': addr, 'amount': fee}
            result = f'Deposito de {msg["amount"]} (Liq: {net_amount}). Taxa de 2% ({fee}) enviada para Stake Pool.'
            break
    else:
        # Se não houver pool, o vault guarda o valor total (opcional, ou cobra e queima)
        storage['balances'][sender] = storage['balances'].get(sender, 0) + msg['amount']
        result = f'Deposito de {msg["amount"]} recebido (sem Stake Pool ativa)'
elif action == 'withdraw':
    amt = msg['params'].get('amount', 0)
    if storage['balances'].get(sender, 0) >= amt:
        storage['balances'][sender] -= amt
        result = f'Saque de {amt} realizado'
    else:
        result = 'ERRO: Saldo insuficiente no Vault'
