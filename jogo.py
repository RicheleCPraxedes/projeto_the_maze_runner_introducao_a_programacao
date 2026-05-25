"""
jogo.py - Máquina de estados do jogo The Maze Runner.
Não depende de Pygame — apenas lógica pura.
"""

from tabuleiro import cor_da_celula, INDICE_FIM, TOTAL_CELULAS, DESCRICAO
from jogador import Jogador, rolar_dado, rolar_dois_dados

# Estados possíveis
ST_SETUP_NOMES   = "setup_nomes"
ST_ROLAGEM_INIT  = "rolagem_init"
ST_AGUARDA_TURNO = "aguarda_turno"
ST_ANIMANDO      = "animando"
ST_EFEITO        = "efeito"
ST_FIM           = "fim"


class EstadoJogo:
    """Contém toda a lógica do jogo, sem nenhum código de renderização."""

    def __init__(self):
        self.jogadores: list[Jogador] = []
        self.estado = ST_SETUP_NOMES
        self.turno_idx: int = 0          # índice do jogador atual
        self.rodada: int = 0
        self.dado_resultado: int = 0
        self.mensagem: str = ""
        self.log: list[str] = []         # histórico de eventos
        self.turno_extra: bool = False

        # Para rolagem inicial
        self._init_rolls: dict[str, int] = {}
        self._init_fase: int = 0         # 0=j1 rola, 1=j2 rola, 2=definido

    # ── Setup ──────────────────────────────────────────────────────────

    def adicionar_jogador(self, nome: str, cor: tuple) -> None:
        self.jogadores.append(Jogador(nome, cor))

    def iniciar_rolagem_inicial(self) -> None:
        self.estado = ST_ROLAGEM_INIT
        self._init_fase = 0
        self._init_rolls = {}
        self._add_log("Cada jogador rola 2 dados para definir quem começa.")

    # ── Rolagem inicial ────────────────────────────────────────────────

    def rolar_inicial(self) -> int:
        """Chamado quando o jogador clica para rolar na fase inicial."""
        j = self.jogadores[self._init_fase]
        d1, d2 = rolar_dois_dados()
        soma = d1 + d2
        self._init_rolls[j.nome] = soma
        self._add_log(f"{j.nome}: {d1}+{d2} = {soma}")
        self._init_fase += 1

        if self._init_fase >= len(self.jogadores):
            self._resolver_ordem_inicial()

        return soma

    def _resolver_ordem_inicial(self) -> None:
        vals = list(self._init_rolls.values())
        if vals[0] == vals[1]:
            self._add_log("Empate! Rolando novamente...")
            self._init_fase = 0
            self._init_rolls = {}
            return

        self.jogadores.sort(
            key=lambda j: self._init_rolls.get(j.nome, 0), reverse=True)
        primeiro = self.jogadores[0].nome
        self._add_log(f"{primeiro} começa com a maior soma!")
        self.turno_idx = 0
        self.rodada = 1
        self.estado = ST_AGUARDA_TURNO
        self._add_log(f"--- Rodada {self.rodada} ---")
        self._add_log(f"Vez de {self.jogadores[0].nome}. Clique em ROLAR.")

    # ── Turno normal ───────────────────────────────────────────────────

    def jogador_atual(self) -> Jogador:
        return self.jogadores[self.turno_idx]

    def rolar_turno(self) -> int:
        """Chamado quando o jogador clica em ROLAR durante seu turno."""
        j = self.jogador_atual()

        # Preso: pula turno
        if j.preso and not self.turno_extra:
            j.preso = False
            self._add_log(f"{j.nome} estava preso — turno pulado!")
            self._proximo_turno()
            return 0

        dado = rolar_dado()
        self.dado_resultado = dado
        self._add_log(f"{j.nome} tirou {dado} no dado.")
        j.mover(dado, TOTAL_CELULAS)
        cor = cor_da_celula(j.posicao)
        self._add_log(f"Avançou para célula {j.posicao} ({cor.upper()}) — {DESCRICAO[cor]}")

        # Chegou ao fim?
        if j.posicao >= INDICE_FIM:
            j.vencedor = True
            self._add_log(f"🏆 {j.nome} chegou ao FIM e VENCEU!")
            self.estado = ST_FIM
            return dado

        # Aplica efeito
        self._aplicar_efeito(j, cor)

        if self.estado != ST_FIM:
            self._proximo_turno()

        return dado

    def _aplicar_efeito(self, j: Jogador, cor: str) -> None:
        if cor == "vermelho":
            j.perder_vida(3)
            if not j.vivo:
                self._add_log(f"💀 {j.nome} foi eliminado!")
                self._checar_fim_por_eliminacao()
        elif cor == "verde":
            j.ganhar_vida(1)
        elif cor == "amarelo":
            j.preso = True
        elif cor == "azul":
            self.turno_extra = True
            self._add_log(f"{j.nome} joga novamente!")
            return   # não avança o turno; deixa o botão ROLAR ativo
        elif cor == "preto":
            j.voltar_inicio()
            self._add_log(f"{j.nome} voltou ao início!")

        self.turno_extra = False

    def _checar_fim_por_eliminacao(self) -> None:
        vivos = [j for j in self.jogadores if j.vivo]
        if len(vivos) <= 1:
            if vivos:
                vivos[0].vencedor = True
                self._add_log(f"🏆 {vivos[0].nome} vence por sobrevivência!")
            else:
                self._add_log("Todos eliminados — empate trágico!")
            self.estado = ST_FIM

    def _proximo_turno(self) -> None:
        if self.estado == ST_FIM:
            return
        self.turno_extra = False
        # Avança para próximo jogador vivo
        for _ in range(len(self.jogadores)):
            self.turno_idx = (self.turno_idx + 1) % len(self.jogadores)
            if self.jogadores[self.turno_idx].vivo:
                break
        # Nova rodada?
        if self.turno_idx == 0:
            self.rodada += 1
            self._add_log(f"--- Rodada {self.rodada} ---")
        j = self.jogador_atual()
        if j.preso:
            self._add_log(f"Vez de {j.nome} — mas está PRESO. Clique em ROLAR para pular.")
        else:
            self._add_log(f"Vez de {j.nome}. Clique em ROLAR.")

    def _add_log(self, msg: str) -> None:
        self.log.append(msg)
        if len(self.log) > 200:
            self.log = self.log[-200:]

    # ── Reinício ───────────────────────────────────────────────────────

    def reiniciar(self) -> None:
        nomes_cores = [(j.nome, j.cor) for j in self.jogadores]
        self.__init__()
        for nome, cor in nomes_cores:
            self.adicionar_jogador(nome, cor)
        self.iniciar_rolagem_inicial()
