"""
jogador.py - Classe Jogador e funções de dado.
"""

import random

VIDA_MAXIMA = 10
VIDA_INICIAL = 10


def rolar_dado(faces: int = 6) -> int:
    return random.randint(1, faces)


def rolar_dois_dados() -> tuple[int, int]:
    return rolar_dado(), rolar_dado()


class Jogador:
    def __init__(self, nome: str, cor: tuple):
        self.nome = nome
        self.cor = cor          # cor RGB do peão
        self.vida: int = VIDA_INICIAL
        self.posicao: int = 0
        self.preso: bool = False
        self.vivo: bool = True
        self.vencedor: bool = False

    def perder_vida(self, pontos: int) -> None:
        self.vida = max(0, self.vida - pontos)
        if self.vida == 0:
            self.vivo = False

    def ganhar_vida(self, pontos: int) -> None:
        self.vida = min(VIDA_MAXIMA, self.vida + pontos)

    def mover(self, casas: int, total_celulas: int) -> None:
        nova = self.posicao + casas
        self.posicao = min(nova, total_celulas - 1)

    def voltar_inicio(self) -> None:
        self.posicao = 0
