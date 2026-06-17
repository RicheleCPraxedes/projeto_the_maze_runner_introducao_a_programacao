
"""
tabuleiro.py - Define o tabuleiro e as cores do jogo The Maze Runner.

RESPONSABILIDADE: Estrutura do tabuleiro (sequência de células, posições no
                  grid, cores e descrições de cada tipo de célula).
"""

# REQUISITO: Sequência de células percorridas em ordem (formato serpentina)
# Cada string representa o tipo/cor da célula naquela posição do caminho
CELULAS = [
    "inicio",    # 0
    "branco",    # 1
    "vermelho",  # 2
    "verde",     # 3
    "branco",    # 4
    "azul",      # 5
    "branco",    # 6
    "amarelo",   # 7
    "branco",    # 8
    "vermelho",  # 9
    "verde",     # 10
    "preto",     # 11
    "azul",      # 12
    "branco",    # 13
    "branco",    # 14
    "vermelho",  # 15
    "branco",    # 16
    "branco",    # 17
    "verde",     # 18
    "vermelho",  # 19
    "branco",    # 20
    "amarelo",   # 21
    "branco",    # 22
    "verde",     # 23
    "vermelho",  # 24
    "amarelo",   # 25
    "verde",     # 26
    "preto",     # 27
    "fim",       # 28 — célula de vitória
]

# REQUISITO: Constantes derivadas do tabuleiro usadas por jogo.py e interface.py
TOTAL_CELULAS = len(CELULAS)
INDICE_FIM = TOTAL_CELULAS - 1

# REQUISITO: Cores RGB para renderização de cada tipo de célula
CORES_RGB = {
    "inicio":   (30,  30,  30),
    "fim":      (255, 215,  0),
    "branco":   (240, 240, 230),
    "vermelho": (210,  40,  40),
    "verde":    (50,  160,  60),
    "amarelo":  (230, 180,   0),
    "azul":     (50,  120, 210),
    "preto":    (20,   20,  20),
}

# Cor do texto exibido sobre cada tipo de célula
TEXTO_COR = {
    "inicio":   (255, 255, 255),
    "fim":      (20,   20,  20),
    "branco":   (60,   60,  60),
    "vermelho": (255, 255, 255),
    "verde":    (255, 255, 255),
    "amarelo":  (20,   20,  20),
    "azul":     (255, 255, 255),
    "preto":    (255, 255, 255),
}

# REQUISITO: Descrição textual do efeito de cada célula (exibida no log)
DESCRICAO = {
    "inicio":   "Início — sem efeito",
    "fim":      "🏁 FIM — você venceu!",
    "branco":   "Espaço neutro",
    "vermelho": "Perde 3 pontos de vida!",
    "verde":    "Recupera 1 ponto de vida",
    "amarelo":  "Preso! Perde 1 turno",
    "azul":     "Jogue novamente!",
    "preto":    "Volta para o início!",
}

# REQUISITO: Coordenadas (coluna, linha) de cada célula no grid 10×6
# O tabuleiro percorre em serpentina:
#   Linha 0:   células  0-9   (esq → dir)
#   Coluna 9:  células 10-14  (cima → baixo, linhas 1-5)
#   Linha 5:   células 15-23  (dir → esq, colunas 8→0)
#   Coluna 0:  células 24-26  (baixo → cima, linhas 4→2)
#   Célula 27 → (0, 1)
#   Célula 28 (fim) → (1, 1) — posição especial no centro-esquerda
GRID_POS: list[tuple[int, int]] = []

# Linha 0, colunas 0-9 → índices 0-9
for c in range(10):
    GRID_POS.append((c, 0))

# Coluna 9, linhas 1-5 → índices 10-14
for r in range(1, 6):
    GRID_POS.append((9, r))

# Linha 5, colunas 8→0 → índices 15-23
for c in range(8, -1, -1):
    GRID_POS.append((c, 5))

# Coluna 0, linhas 4→2 → índices 24-26
for r in range(4, 1, -1):
    GRID_POS.append((0, r))

# Célula 27 → (0, 1)
GRID_POS.append((0, 1))

# Célula 28 (fim) → (1, 1)
GRID_POS.append((1, 1))


# REQUISITO: Função auxiliar — retorna o tipo de célula dado um índice
def cor_da_celula(indice: int) -> str:
    """Retorna o nome do tipo da célula na posição 'indice'."""
    if 0 <= indice < TOTAL_CELULAS:
        return CELULAS[indice]
    return "fim"