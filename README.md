# projeto_the_maze_runner_introducao_a_programacao
# 🎮 The Maze Runner

Projeto desenvolvido para a disciplina de **Introdução à Computação I** da  
**Universidade Federal Rural de Pernambuco (UFRPE)**.

---

## 📚 Sobre o Projeto

O jogo **The Maze Runner** consiste em uma disputa entre dois jogadores em um tabuleiro repleto de desafios e obstáculos. O objetivo principal é chegar ao final do percurso vivo, administrando a quantidade de vida ao longo da partida.

Cada jogador deve utilizar estratégia e sorte nos lançamentos de dados para avançar pelo tabuleiro e sobreviver aos efeitos especiais de cada célula.

---

## 🎯 Objetivo do Jogo

- Chegar ao fim do tabuleiro antes do adversário;
- Manter os pontos de vida acima de zero;
- Utilizar as vantagens e superar as penalidades presentes no percurso.

---

## 🕹️ Regras do Jogo

### 🎲 Definição do Primeiro Jogador

No início da partida:

- Cada jogador lança **dois dados**;
- O jogador que obtiver a maior soma começa a partida;
- Os dados possuem valores de **1 a 6**.

---

### ❤️ Vida dos Jogadores

- Ambos os jogadores começam com **10 pontos de vida**;
- A vida máxima é limitada a **10 pontos**;
- Os jogadores podem ocupar a mesma célula simultaneamente.

---

### ▶️ Funcionamento das Rodadas

Durante sua vez:

1. O jogador lança **1 dado**;
2. O valor obtido determina quantas células serão percorridas;
3. Após o movimento, a ação da célula é aplicada;
4. O turno passa para o próximo jogador.

---

## 🎨 Tipos de Células

O tabuleiro possui células coloridas, cada uma com uma função específica:

| Cor da Célula | Efeito |
|---|---|
| ⚪ Branca | Espaço neutro, sem efeito |
| 🔴 Vermelha | Remove 3 pontos de vida |
| 🟢 Verde | Recupera 1 ponto de vida |
| 🟡 Amarela | Jogador perde um turno |
| 🔵 Azul | Jogador joga novamente |
| ⚫ Preta | Jogador retorna ao início |

> As células de início e fim não possuem efeitos especiais.

---

## 🗺️ Estrutura do Tabuleiro

- O tabuleiro inicia na célula **Início**;
- O objetivo é alcançar a célula **Fim**;
- O percurso contém diferentes tipos de obstáculos e bônus.

---

## 💻 Tecnologias Utilizadas

- Linguagem C
- Lógica de Programação
- Estruturas Condicionais
- Estruturas de Repetição
- Vetores e Matrizes
- Funções

---
