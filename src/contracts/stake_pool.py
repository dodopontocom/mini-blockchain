#!/usr/bin/env python3
# stake_pool smart contract
# Inicialização do contrato (Executa apenas no deploy)
if 'owner' not in storage:
    storage['owner'] = msg['sender']
    storage['stakes'] = {}             # {endereco: valor_staked}
    storage['unstake_requests'] = {}   # {endereco: {amount: valor, timestamp: tempo}}
    storage['total_staked'] = 0
    storage['reward_index'] = 0.0      # Acumulado de recompensas por token
    storage['user_reward_index'] = {}  # {endereco: ultimo_index_visto}
    storage['user_accrued_rewards'] = {} # {endereco: recompensas_pendentes}
    result = 'Stake Pool Ativado'

sender = msg['sender']
action = msg['params'].get('action')

# Função auxiliar para atualizar recompensas do usuário antes de qualquer mudança no seu stake
def update_user_rewards(addr, st):
    if addr in st['stakes'] and st['stakes'][addr] > 0:
        last_idx = st['user_reward_index'].get(addr, 0.0)
        diff = st['reward_index'] - last_idx
        if diff > 0:
            reward = st['stakes'][addr] * diff
            st['user_accrued_rewards'][addr] = st['user_accrued_rewards'].get(addr, 0.0) + reward
    st['user_reward_index'][addr] = st['reward_index']

# Lógica principal
if action:
    if action == 'stake':
        amount = msg['amount']
        if amount > 0:
            update_user_rewards(sender, storage)
            
            # Se houver recompensas acumuladas sem stakers, distribui agora para o primeiro staker
            pending = storage.get('pending_rewards', 0.0)
            if pending > 0:
                storage['reward_index'] += pending / amount
                storage['pending_rewards'] = 0.0

            storage['stakes'][sender] = storage['stakes'].get(sender, 0) + amount
            storage['total_staked'] += amount
            result = f'Stake de {amount} realizado com sucesso'
        else:
            result = 'ERRO: Você precisa enviar tokens para fazer stake'

    elif action == 'request_unstake':
        amount = msg['params'].get('amount', 0)
        current_stake = storage['stakes'].get(sender, 0)
        if amount > 0 and current_stake >= amount:
            update_user_rewards(sender, storage)
            # Registra o pedido de saque (cooldown começa agora)
            storage['unstake_requests'][sender] = {
                'amount': amount,
                'timestamp': msg['timestamp']
            }
            result = f'Pedido de unstake de {amount} registrado. Aguarde para sacar com taxa reduzida.'
        else:
            result = 'ERRO: Saldo insuficiente em stake ou valor invalido'

    elif action == 'withdraw_stake':
        if sender in storage['unstake_requests']:
            req = storage['unstake_requests'][sender]
            amount = req['amount']
            time_diff = msg['timestamp'] - req['timestamp']
            
            # 1 dia = 86400 segundos (para testes rápidos no mini-blockchain, 
            # poderíamos usar valores menores, mas seguiremos a regra de "dias")
            days = int(time_diff // 86400)
            
            # Calculo da taxa: 0 dias (3%), 1 dia (2%), 2 dias (1%), 3+ dias (0%)
            fee_percent = 0
            if days == 0: fee_percent = 0.03
            elif days == 1: fee_percent = 0.02
            elif days == 2: fee_percent = 0.01
            
            fee = amount * fee_percent
            net_amount = amount - fee
            
            update_user_rewards(sender, storage)
            
            # Remove do stake e do total
            storage['stakes'][sender] -= amount
            storage['total_staked'] -= amount
            
            # A taxa coletada volta para o fundo de recompensas da pool
            if fee > 0 and storage['total_staked'] > 0:
                storage['reward_index'] += fee / storage['total_staked']
            
            # Limpa o pedido
            del storage['unstake_requests'][sender]
            
            # Comando de pagamento para a engine
            payout = {'address': sender, 'amount': net_amount}
            result = f'Saque de {net_amount} realizado. Taxa de {fee} aplicada ({days} dias passados).'
        else:
            result = 'ERRO: Nenhum pedido de unstake pendente encontrado'

    elif action == 'claim_reward':
        update_user_rewards(sender, storage)
        reward = storage['user_accrued_rewards'].get(sender, 0)
        if reward > 0:
            storage['user_accrued_rewards'][sender] = 0
            payout = {'address': sender, 'amount': reward}
            result = f'Recompensa de {reward} resgatada'
        else:
            result = 'ERRO: Nenhuma recompensa para resgatar'

    elif action == 'fund':
        # Apenas o dono pode injetar recompensas extras
        if sender == storage['owner']:
            amount = msg['amount']
            if amount > 0:
                if storage['total_staked'] > 0:
                    # Distribui o valor proporcionalmente entre os stakers atuais
                    storage['reward_index'] += amount / storage['total_staked']
                    result = f'Pool abastecida com {amount} em recompensas'
                else:
                    # Se ninguém estiver fazendo stake, guarda o valor em um fundo acumulado
                    storage['pending_rewards'] = storage.get('pending_rewards', 0.0) + amount
                    result = f'Recompensas de {amount} guardadas (aguardando stakers)'
            else:
                result = 'ERRO: Valor invalido para fund'
        else:
            result = 'ERRO: Apenas o dono do contrato pode usar fund'
    else:
        result = 'ERRO: Acao nao reconhecida'
