import json
from filelock import FileLock
from src.commons.config import LOCK_FILE, TAXA_BASE, TAXA_POR_BYTE, TAXA_MINIMA

# Lock Global compartilhado por todos os módulos
lock = FileLock(LOCK_FILE)

def calcular_taxa(transaction_data):
    """Calcula taxa da transação baseada no tamanho em bytes"""
    tamanho = len(json.dumps(transaction_data))
    taxa = TAXA_BASE + (TAXA_POR_BYTE * tamanho)
    return max(taxa, TAXA_MINIMA)
