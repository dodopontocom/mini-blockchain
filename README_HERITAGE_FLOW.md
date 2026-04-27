# ⚰️ Fluxo de Herança Digital: O Guia Definitivo

Este documento explica a lógica de segurança por trás do contrato de herança (Dead Man's Switch) do projeto **mini-blockchain**.

---

## 1. O Paradoxo do Segredo na Blockchain
Uma blockchain é um livro **público**. Se você salvar o texto *"O segredo está enterrado sob a mangueira"* nela, todo mundo poderá ler. Se você criptografar com uma senha, terá um novo problema: onde guardar a senha para o herdeiro sem que ninguém mais veja?

**A Solução:** O uso de **Hashes SHA256** e o armazenamento **Offline**.

---

## 2. Analogias para Entender o Hash

### A Analogia da Impressão Digital 🖐️
Imagine que você quer provar que conhece uma pessoa, mas não quer revelar quem ela é. Você tira uma foto apenas da **impressão digital** dela e coloca na praça pública.
- **Geração:** É fácil pegar a pessoa e tirar a digital.
- **Unicidade:** Cada pessoa tem uma digital única.
- **Via Única (O Segredo):** Ninguém consegue olhar para a digital e reconstruir o rosto, a altura ou a voz da pessoa.
- **Verificação:** Quando alguém aparecer dizendo "Eu sou o herdeiro e tenho o segredo", você tira a digital dessa pessoa. Se bater com a que está na praça, ela é legítima.

### A Analogia do Envelope Selado no Vidro ✉️
O Smart Contract é como uma **caixa de vidro indestrutível** em uma praça:
1. Você coloca o dinheiro dentro da caixa.
2. Você cola um **envelope selado** do lado de fora da caixa. O envelope contém apenas o carimbo do cartório (o Hash).
3. O conteúdo do envelope (o Segredo) está guardado em um **cofre físico** na sua casa.
4. O contrato diz: "Se o dono não apertar o botão por 1 ano, o herdeiro pode vir aqui".
5. O herdeiro traz o papel que ele achou no seu cofre físico. Se o carimbo do papel bater com o carimbo da caixa, o vidro quebra e o dinheiro é dele.

---

## 3. Por que não existe "Decodificar"? 🚫🔓

O SHA256 é uma função matemática de "esmagamento". Ele pega qualquer quantidade de dados e transforma em 64 caracteres hexadecimais.
- Se você mudar uma única letra no seu segredo de 10 páginas, o Hash muda completamente.
- É impossível fazer o caminho inverso. A matemática do SHA256 é o que protege toda a internet moderna, transações bancárias e o próprio Bitcoin.

**"Decodificar" um hash seria como tentar transformar um hambúrguer de volta em uma vaca inteira.** Você até pode tentar adivinhar qual vaca foi usada (Ataque de Força Bruta), mas se houver bilhões de vacas no mundo, você nunca terminará.

---

## 4. O Fluxo de Trabalho (Workflow)

| Ator | Ação | Local |
| :--- | :--- | :--- |
| **Pai (Dono)** | Escreve o segredo em um papel físico. | 🏠 Offline (Cofre) |
| **Pai (Dono)** | Gera o Hash do segredo (Digital). | 💻 Hash Tool (Local) |
| **Blockchain** | Recebe o Hash e o Depósito. | ⛓️ On-Chain (Público) |
| **Herdeiro** | Aguarda o tempo de inatividade. | ⏳ Tempo |
| **Herdeiro** | Pega o papel físico no cofre do pai. | 🏠 Offline |
| **Blockchain** | Revela o Hash ao herdeiro após o timeout. | ⛓️ On-Chain |
| **Herdeiro** | Compara o papel com o Hash para ter certeza. | 💻 Hash Tool (Verificar) |

---

## 5. Lição de Segurança: A Força do Segredo 🛡️

O único inimigo do Hash é o **Ataque de Dicionário**.
- Se seu segredo for `123456`, um hacker pode gerar o hash de todos os números e descobrir o seu em milissegundos (isso é o que nossa ferramenta faz na aba **Desafio**).
- Se seu segredo for uma frase longa como: `O tesouro de família está na conta 99 do banco suíço sob o código Alpha-Beta-99`, a chance de alguém adivinhar é **zero** até o fim do universo.

---
*Este sistema garante que a Blockchain seja o Juiz, mas você continue sendo o único Guardião da Informação.*
