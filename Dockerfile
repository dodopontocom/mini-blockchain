# Imagem base leve
FROM python:3.11-slim

# Instala dependências do sistema necessárias para os scripts
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Garante as bibliotecas extras que identificamos
RUN pip install --no-cache-dir flask flask-restx requests ecdsa filelock

# Copia todo o código do projeto
COPY . .

# Dá permissão de execução para todos os scripts
RUN chmod +x *.sh

# Expõe a porta da API
EXPOSE 5000

# O run.sh já orquestra o blockc, api e simulador
# Usamos o comando direto para evitar problemas com venv dentro do Docker
CMD ["./run.sh"]
