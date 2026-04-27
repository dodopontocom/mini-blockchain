#!/usr/bin/env python3

# Inicialização (Executa no deploy)
if 'balances' not in storage:
    storage['balances'] = {}
    storage['owner'] = msg['sender']
    # Opcional: Definir uma pool alvo específica no deploy
    storage['target_pool'] = msg['params'].get('target_pool')
    result = 'Vault Ativado'

# Lógica de Execução
sender = msg['sender']
action = msg['params'].get('action')

if msg['amount'] > 0:
    fee = msg['amount'] * 0.02
    net_amount = msg['amount'] - fee
    target = storage.get('target_pool') or PROTOCOL_POOL
    pool_found = None

    # 1. Tenta a pool alvo ou oficial
    if target and target in all_states and 'total_staked' in all_states[target]:
        pool_found = target
    
    # 2. Se não, procura qualquer uma
    if not pool_found:
        for addr, state in all_states.items():
            if 'total_staked' in state:
                pool_found = addr
                break

    # 3. Executa a lógica baseado se achou ou não
    if pool_found:
        state = all_states[pool_found]
        if state['total_staked'] > 0:
            state['reward_index'] += fee / state['total_staked']
        else:
            state['pending_rewards'] = state.get('pending_rewards', 0.0) + fee
        
        payout = {'address': pool_found, 'amount': fee}
        storage['balances'][sender] = storage['balances'].get(sender, 0) + net_amount
        result = f'Deposito de {msg["amount"]} (Liq: {net_amount}). Taxa de 2% enviada para Pool.'
    else:
        # SEM POOL: Depósito integral
        storage['balances'][sender] = storage['balances'].get(sender, 0) + msg['amount']
        result = f'Deposito de {msg["amount"]} recebido integralmente (sem taxa de incentivo)'

elif action == 'set_pool':
    # Apenas o dono do contrato (quem fez o deploy) pode mudar a pool alvo
    if sender == storage.get('owner'):
        new_pool = msg['params'].get('pool')
        if new_pool in all_states and 'total_staked' in all_states[new_pool]:
            storage['target_pool'] = new_pool
            result = f'Pool alvo atualizada para {new_pool[:8]}...'
        else:
            result = 'ERRO: Endereco informado nao e uma Stake Pool valida'
    else:
        result = 'ERRO: Apenas o dono pode mudar a pool alvo'

elif action == 'withdraw':
    amt = msg['params'].get('amount', 0)
    if storage['balances'].get(sender, 0) >= amt:
        storage['balances'][sender] -= amt
        result = f'Saque de {amt} realizado'
    else:
        result = 'ERRO: Saldo insuficiente no Vault'
