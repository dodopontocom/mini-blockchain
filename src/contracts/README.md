# 📜 Smart Contracts

## 🧠 Entendendo os Smart Contracts

Pense em um **Smart Contract** como uma "máquina de vendas" digital: você insere os dados (ou valores), a máquina processa as regras sozinha e entrega o resultado, sem precisar de um humano no meio para validar.

Neste projeto, simulamos quatro tipos comuns:
1.  **Votação**: Uma urna eletrônica onde cada voto é registrado e ninguém pode apagar.
2.  **Cofre (Vault)**: Um banco pessoal onde você guarda seus valores e só você (o dono) pode sacar.
3.  **Herança (Dead Man Switch)**: Um contrato que envia seus bens para outra pessoa se você ficar muito tempo sem dar um "ping" (avisar que está vivo).
4.  **Stake Pool**: Um sistema de recompensas onde você trava seus valores para ajudar na rede e ganha juros por isso.

### Fluxo de Operação
O diagrama abaixo mostra como os scripts interagem com esses contratos através da nossa API:

```mermaid
graph TD
    %% Nodes
    Script["smart-ops-v2.sh<br/>Orquestrador de Smart Contracts"]

    Voting["🗳 Votação<br/>Enquetes On-chain"]
    Vault["🏦 Cofre (Vault)<br/>Gestão de Ativos"]
    Heritage["⏳ Herança<br/>Dead man's switch"]
    Stake["🥩 Stake Pool<br/>Recompensas e Governança"]

    V1[deploy]
    V2[vote]

    VA1[deploy]
    VA2[deposit]
    VA3[withdraw]
    VA4[set-pool]

    H1[deploy]
    H2[ping]
    H3[recover]
    H4[revoke]

    S1[deploy]
    S2[stake]
    S3[request-unstake]
    S4[withdraw-stake]
    S5[claim-reward]
    S6[fund]

    API["API Blockchain<br/>localhost:5000"]
    Nodes[("nodes_data.json<br/>Wallets e Chaves")]
    Block["Bloco gravado<br/>Estado atualizado"]

    %% Connections
    Script --> Voting
    Script --> Vault
    Script --> Heritage
    Script --> Stake

    Voting --> V1
    Voting --> V2

    Vault --> VA1
    Vault --> VA2
    Vault --> VA3
    Vault --> VA4

    Heritage --> H1
    Heritage --> H2
    Heritage --> H3
    Heritage --> H4

    Stake --> S1
    Stake --> S2
    Stake --> S3
    Stake --> S4
    Stake --> S5
    Stake --> S6

    V1 & V2 & VA1 & VA2 & VA3 & VA4 & H1 & H2 & H3 & H4 & S1 & S2 & S3 & S4 & S5 & S6 -- "Transação" --> API
    API <--> Nodes
    API --> Block

    %% Styling
    style Script fill:#333,stroke:#666,color:#fff
    style Voting fill:#3c3489,stroke:#afa9ec,color:#fff
    style Vault fill:#085041,stroke:#5dcaa5,color:#fff
    style Heritage fill:#633806,stroke:#ef9f27,color:#fff
    style Stake fill:#9c1c1c,stroke:#ff6b6b,color:#fff
    style API fill:#333,stroke:#666,color:#fff
    style Block fill:#0c447c,stroke:#85b7eb,color:#fff
    style Nodes fill:#444,stroke:#999,color:#fff
```
