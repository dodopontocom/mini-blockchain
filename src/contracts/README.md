# 📜 Smart Contracts

## 🧠 Entendendo os Smart Contracts

Pense em um **Smart Contract** como uma "máquina de vendas" digital: você insere os dados (ou valores), a máquina processa as regras sozinha e entrega o resultado, sem precisar de um humano no meio para validar.

Neste projeto, simulamos três tipos comuns:
1.  **Votação**: Uma urna eletrônica onde cada voto é registrado e ninguém pode apagar.
2.  **Cofre (Vault)**: Um banco pessoal onde você guarda seus valores e só você (o dono) pode sacar.
3.  **Herança (Dead Man Switch)**: Um contrato que envia seus bens para outra pessoa se você ficar muito tempo sem dar um "ping" (avisar que está vivo).

### Fluxo de Operação
O diagrama abaixo mostra como os scripts interagem com esses contratos através da nossa API:

```mermaid
graph TD
    %% Nodes
    Script["smart-ops-v2.sh<br/>Controle remoto da blockchain"]

    Voting["🗳 Votação<br/>Enquete com opções"]
    Vault["🏦 Cofre (Vault)<br/>Banco on-chain"]
    Heritage["⏳ Herança<br/>Dead man's switch"]

    V1[deploy-vote]
    V2[vote]
    VA1[deploy-vault]
    VA2[deposit]
    VA3[withdraw]
    H1[deploy]
    H2[ping]
    H3[recover]

    API["API Blockchain<br/>localhost:5000"]
    Nodes[("nodes_data.json<br/>Endereços dos usuários")]
    Block["Bloco gravado<br/>Contrato executado"]

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

    V1 -- "Transação" --> API
    V2 -- "Transação" --> API
    VA1 -- "Transação" --> API
    VA2 -- "Transação" --> API
    VA3 -- "Transação" --> API
    H1 -- "Transação" --> API
    H2 -- "Transação" --> API
    H3 -- "Transação" --> API

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
