# 🪨 mini-blockchain v2

Simulador de blockchain educacional com suporte a smart contracts, API REST e testes de performance.

```mermaid
graph TD
    %% Nodes
    Script["<b>smart-ops-v2.sh</b><br/>Controle remoto da blockchain"]

    Voting["<b>🗳 Votação</b><br/>Enquete com opções"]
    Vault["<b>🏦 Cofre (Vault)</b><br/>Banco on-chain"]
    Heritage["<b>⏳ Herança</b><br/>Dead man's switch"]

    V1[deploy-vote]
    V2[vote]
    VA1[deploy-vault]
    VA2[deposit]
    VA3[withdraw]
    H1[deploy]
    H2[ping]
    H3[recover]

    API["<b>API Blockchain</b><br/>localhost:5000"]
    Nodes[("<b>nodes_data.json</b><br/>Endereços dos usuários")]
    Block["<b>Bloco gravado</b><br/>Contrato executado"]

    %% Connections
    Script --> Voting
    Script --> Vault
    Script --> Heritage

    Voting --> V1
    Voting --> V2
    Vault --> VA1
    Vault --> VA2
    Vault --> VA3
    Heritage --> H1
    Heritage --> H2
    Heritage --> H3

    V1 & V2 & VA1 & VA2 & VA3 & H1 & H2 & H3 -- "Transação" --> API
    API <--> Nodes
    API --> Block

    %% Styling
    style Script fill:#333,stroke:#666,color:#fff
    style Voting fill:#3c3489,stroke:#afa9ec,color:#fff
    style Vault fill:#085041,stroke:#5dcaa5,color:#fff
    style Heritage fill:#633806,stroke:#ef9f27,color:#fff
    style API fill:#333,stroke:#666,color:#fff
    style Block fill:#0c447c,stroke:#85b7eb,color:#fff
    style Nodes fill:#444,stroke:#999,color:#fff
```

## 📁 Estrutura do Projeto

- `src/`: Core da aplicação (API, Lógica da Blockchain, Simuladores).
- `infra/`: Infraestrutura, Dockerfile e scripts operacionais.
- `.github/workflows/`: Automação de build e testes de performance.

## 🚀 Como Executar

### Localmente (Bash)
```bash
./infra/scripts/run.sh
```

### Via Docker
```bash
docker build -t mini-blockchain -f infra/Dockerfile .
docker run -p 5000:5000 mini-blockchain
```

## 📊 Funcionalidades
- **Blockchain**: Mineração automática, transações assinadas e integridade via hashes.
- **Smart Contracts**: Deploy e interação com contratos de votação, banco (vault) e herança.
- **API**: Endpoints para consulta de blocos, saldos e envio de transações.
- **Stress Test**: Motor de simulação de tráfego intenso e aleatório.

## 🛠️ Tecnologias
- Python 3.11+
- Flask & Flask-RESTX
- ECDSA (Criptografia)
- Docker & GitHub Actions
