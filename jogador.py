"""
jogador.py - Classe Jogador e funções de dado.

RESPONSABILIDADE: Definição das regras do jogador (vida, movimento, status)
                  e funções de aleatoriedade (rolagem de dados).
"""

import random

# REQUISITO: Constantes de configuração do jogador
VIDA_MAXIMA = 10
VIDA_INICIAL = 10


# REQUISITO: Geração de número aleatório (dado de 6 faces por padrão)
def rolar_dado(faces: int = 6) -> int:
    """Retorna um número aleatório entre 1 e 'faces' (simula um dado)."""
    return random.randint(1, faces)


# REQUISITO: Rolagem dupla usada na fase de definição de ordem
def rolar_dois_dados() -> tuple[int, int]:
    """Retorna dois valores de dado independentes."""
    return rolar_dado(), rolar_dado()


# REQUISITO: Classe principal que representa cada jogador na partida
class Jogador:
    def __init__(self, nome: str, cor: tuple):
        self.nome = nome
        self.cor = cor          # cor RGB do peão na tela
        self.vida: int = VIDA_INICIAL
        self.posicao: int = 0   # índice da célula atual no tabuleiro
        self.preso: bool = False
        self.vivo: bool = True
        self.vencedor: bool = False

    # REQUISITO: Efeito da célula VERMELHA — perda de vida com eliminação
    def perder_vida(self, pontos: int) -> None:
        """Reduz a vida do jogador. Se chegar a 0, o jogador é eliminado."""
        self.vida = max(0, self.vida - pontos)
        if self.vida == 0:
            self.vivo = False   # eliminação por vida zerada

    # REQUISITO: Efeito da célula VERDE — recuperação de vida
    def ganhar_vida(self, pontos: int) -> None:
        """Aumenta a vida do jogador, respeitando o máximo permitido."""
        self.vida = min(VIDA_MAXIMA, self.vida + pontos)

    # REQUISITO: Movimentação — avança o jogador pelo tabuleiro
    def mover(self, casas: int, total_celulas: int) -> None:
        """Move o jogador 'casas' posições à frente, sem ultrapassar o fim."""
        nova = self.posicao + casas
        self.posicao = min(nova, total_celulas - 1)

    # REQUISITO: Efeito da célula PRETA — penalidade de voltar ao início
    def voltar_inicio(self) -> None:
        """Retorna o jogador à posição inicial do tabuleiro."""
        self.posicao = 0
