import json
from filelock import FileLock
from src.commons.config import LOCK_FILE, TAXA_BASE, TAXA_POR_BYTE, TAXA_MINIMA, TAXA_POR_VALOR

# Lock Global compartilhado por todos os módulos
lock = FileLock(LOCK_FILE)

def calcular_taxa(transaction_data):
    """Calcula taxa híbrida: baseada no tamanho (bytes) + percentual do valor"""
    amount = float(transaction_data.get('amount', 0))
    
    # 1. Filtra campos para o cálculo por tamanho (bytes)
    tx_clean = {
        'sender': transaction_data.get('sender'),
        'receiver': transaction_data.get('receiver'),
        'amount': amount,
        'data': transaction_data.get('data'),
        'type': transaction_data.get('type')
    }
    tamanho = len(json.dumps(tx_clean))
    
    # 2. Cálculo Híbrido:
    # (Base) + (Custo por Espaço) + (Custo por Valor)
    taxa_espaco = TAXA_POR_BYTE * tamanho
    taxa_valor = amount * TAXA_POR_VALOR
    
    taxa_total = TAXA_BASE + taxa_espaco + taxa_valor
    
    # Garante taxa mínima e arredonda para 8 casas (padrão crypto)
    return round(max(taxa_total, TAXA_MINIMA), 8)
