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

def formatadorTempo(segundos: int) -> str:
    """Formata segundos em unidades legíveis conforme regras restritas (incluindo meses e anos)."""
    if segundos <= 180:
        return f"{segundos} segundos"
    
    if segundos < 3600:
        minutos = segundos / 60
        return f"{minutos:.1f} minutos"
    
    if segundos < 86400:
        horas = segundos / 3600
        return f"{horas:.1f} horas"
    
    if segundos < 2592000: # 30 dias
        dias = segundos / 86400
        return f"{dias:.1f} dias"
    
    if segundos < 31536000: # 365 dias
        meses = segundos / 2592000
        return f"{meses:.1f} meses"
    
    anos = segundos / 31536000
    return f"{anos:.1f} anos"

if __name__ == "__main__":
    # Testes solicitados expandidos
    testes = [60, 200, 4000, 100000, 3000000, 40000000]
    print("--- Resultados do formatadorTempo (V2) ---")
    for s in testes:
        print(f"{s}s -> {formatadorTempo(s)}")
