"""
jogo.py - Máquina de estados do jogo The Maze Runner.

RESPONSABILIDADE: Toda a lógica de regras do jogo (turnos, efeitos de células,
                  condições de vitória/eliminação) sem nenhum código gráfico.
"""

from tabuleiro import cor_da_celula, INDICE_FIM, TOTAL_CELULAS, DESCRICAO
from jogador import Jogador, rolar_dado, rolar_dois_dados

# REQUISITO: Estados possíveis do jogo (máquina de estados finitos)
ST_SETUP_NOMES   = "setup_nomes"    # tela inicial de cadastro de nomes
ST_ROLAGEM_INIT  = "rolagem_init"   # rolagem para definir quem começa
ST_AGUARDA_TURNO = "aguarda_turno"  # esperando o jogador clicar em Rolar
ST_ANIMANDO      = "animando"       # reservado para futuras animações
ST_EFEITO        = "efeito"         # reservado para expansão de efeitos
ST_FIM           = "fim"            # jogo encerrado (vitória ou eliminação)


class EstadoJogo:
    """
    Contém toda a lógica do jogo, sem nenhum código de renderização.
    A interface (interface.py) lê os atributos desta classe para saber
    o que desenhar, e chama os métodos públicos para avançar o jogo.
    """

    # REQUISITO: Inicialização — cria o estado inicial limpo
    def __init__(self):
        self.jogadores: list[Jogador] = []
        self.estado = ST_SETUP_NOMES    # começa na tela de nomes
        self.turno_idx: int = 0         # índice do jogador atual
        self.rodada: int = 0
        self.dado_resultado: int = 0
        self.mensagem: str = ""
        self.log: list[str] = []        # histórico de eventos exibido na tela
        self.turno_extra: bool = False  # True quando célula AZUL foi ativada

        # Controle interno da fase de rolagem inicial
        self._init_rolls: dict[str, int] = {}
        self._init_fase: int = 0        # 0=j1 rola, 1=j2 rola, 2=definido

    # ── Setup ──────────────────────────────────────────────────────────

    # REQUISITO: Cadastro de jogadores antes do início da partida
    def adicionar_jogador(self, nome: str, cor: tuple) -> None:
        """Cria um novo Jogador e o adiciona à lista."""
        self.jogadores.append(Jogador(nome, cor))

    def iniciar_rolagem_inicial(self) -> None:
        """Transita para a fase em que cada jogador rola para ver quem começa."""
        self.estado = ST_ROLAGEM_INIT
        self._init_fase = 0
        self._init_rolls = {}
        self._add_log("Rolagem inicial: quem tira mais começa.")

    # ── Rolagem inicial ────────────────────────────────────────────────

    # REQUISITO: Loop de rolagem inicial — cada jogador rola uma vez;
    # em caso de empate o loop recomeça até haver um vencedor.
    def rolar_inicial(self) -> int:
        """
        Chamado quando o jogador clica em ROLAR na fase inicial.
        Cada clique avança a fase de um jogador por vez.
        Retorna a soma dos dados rolados.
        """
        j = self.jogadores[self._init_fase]
        d1, d2 = rolar_dois_dados()
        soma = d1 + d2
        self._init_rolls[j.nome] = soma
        self._add_log(f"{j.nome}: {d1}+{d2} = {soma}")
        self._init_fase += 1

        # Todos os jogadores rolaram? Resolve a ordem
        if self._init_fase >= len(self.jogadores):
            self._resolver_ordem_inicial()

        return soma

    def _resolver_ordem_inicial(self) -> None:
        """Define quem joga primeiro. Em empate, repete a rolagem."""
        vals = list(self._init_rolls.values())
        if vals[0] == vals[1]:
            # REQUISITO: Tratamento de empate na rolagem inicial
            self._add_log("Empate! Rolando novamente...")
            self._init_fase = 0
            self._init_rolls = {}
            return  # aguarda novos cliques sem mudar o estado

        # Ordena jogadores pela soma (maior primeiro)
        self.jogadores.sort(
            key=lambda j: self._init_rolls.get(j.nome, 0), reverse=True)
        primeiro = self.jogadores[0].nome
        self._add_log(f"{primeiro} começa com a maior soma!")

        # REQUISITO: Início do jogo — transita para o primeiro turno
        self.turno_idx = 0
        self.rodada = 1
        self.estado = ST_AGUARDA_TURNO
        self._add_log(f"--- Rodada {self.rodada} ---")
        self._add_log(f"Vez de {self.jogadores[0].nome}. Clique em ROLAR.")

    # ── Turno normal ───────────────────────────────────────────────────

    def jogador_atual(self) -> Jogador:
        """Retorna o objeto Jogador de quem está jogando agora."""
        return self.jogadores[self.turno_idx]

    # REQUISITO: Loop principal do jogo — executado a cada clique em ROLAR
    def rolar_turno(self) -> int:
        """
        Processa um turno completo:
          1. Verifica se o jogador está preso (célula amarela)
          2. Rola o dado e move o jogador
          3. Aplica o efeito da célula de destino
          4. Verifica condição de vitória (chegou ao FIM)
          5. Passa para o próximo jogador

        Retorna o valor do dado (0 se o turno foi pulado por prisão).
        """
        j = self.jogador_atual()

        # REQUISITO: Efeito da célula AMARELA — perde 1 turno (preso)
        if j.preso and not self.turno_extra:
            j.preso = False
            self._add_log(f"{j.nome} estava preso — turno pulado!")
            self._proximo_turno()
            return 0  # retorna 0 para indicar que não houve rolagem

        # REQUISITO: Movimentação — rola dado e avança o jogador
        dado = rolar_dado()
        self.dado_resultado = dado
        self._add_log(f"{j.nome} tirou {dado} no dado.")
        j.mover(dado, TOTAL_CELULAS)
        cor = cor_da_celula(j.posicao)
        self._add_log(f"{j.nome} tirou {dado} → cel {j.posicao} ({cor.upper()})")
        self._add_log(f"  Efeito: {DESCRICAO[cor]}")

        # REQUISITO: Condição de vitória — chegou à célula FIM
        if j.posicao >= INDICE_FIM:
            j.vencedor = True
            self._add_log(f"🏆 {j.nome} chegou ao FIM e VENCEU!")
            self.estado = ST_FIM   # encerra o loop principal do jogo
            return dado

        # REQUISITO: Efeito das células — aplica a ação da célula de destino
        self._aplicar_efeito(j, cor)

        # Passa para o próximo turno (a menos que o estado seja ST_FIM)
        if self.estado != ST_FIM:
            self._proximo_turno()

        return dado

    # REQUISITO: Efeito das células — lógica de cada tipo de célula especial
    def _aplicar_efeito(self, j: Jogador, cor: str) -> None:
        """
        Aplica o efeito da célula em que o jogador parou:
          VERMELHO → perde 3 vidas (pode ser eliminado)
          VERDE    → recupera 1 vida
          AMARELO  → fica preso (perde próximo turno)
          AZUL     → ganha turno extra (joga de novo)
          PRETO    → volta para a posição 0 (início)
        """
        if cor == "vermelho":
            j.perder_vida(3)
            if not j.vivo:
                self._add_log(f"💀 {j.nome} foi eliminado!")
                self._checar_fim_por_eliminacao()

        elif cor == "verde":
            j.ganhar_vida(1)

        elif cor == "amarelo":
            j.preso = True   # será resolvido no começo do próximo turno

        elif cor == "azul":
            # REQUISITO: Turno extra (célula AZUL) — não avança o turno
            self.turno_extra = True
            self._add_log(f"{j.nome} joga novamente!")
            return   # sai sem chamar _proximo_turno

        elif cor == "preto":
            j.voltar_inicio()
            self._add_log(f"{j.nome} voltou ao início!")

        self.turno_extra = False

    # REQUISITO: Condição de fim por eliminação — verifica sobreviventes
    def _checar_fim_por_eliminacao(self) -> None:
        """Encerra o jogo se restar 1 ou 0 jogadores vivos."""
        vivos = [j for j in self.jogadores if j.vivo]
        if len(vivos) <= 1:
            if vivos:
                vivos[0].vencedor = True
                self._add_log(f"🏆 {vivos[0].nome} vence por sobrevivência!")
            else:
                self._add_log("Todos eliminados — empate trágico!")
            self.estado = ST_FIM

    # REQUISITO: Controle de turnos — avança para o próximo jogador vivo
    def _proximo_turno(self) -> None:
        """
        Passa o turno ao próximo jogador ativo.
        Pula jogadores eliminados (vivo=False).
        Incrementa o contador de rodada quando volta ao índice 0.
        """
        if self.estado == ST_FIM:
            return   # jogo encerrado, não avança mais

        self.turno_extra = False

        # Percorre a lista ciclicamente até achar um jogador vivo
        for _ in range(len(self.jogadores)):
            self.turno_idx = (self.turno_idx + 1) % len(self.jogadores)
            if self.jogadores[self.turno_idx].vivo:
                break

        # Nova rodada ao voltar ao índice 0
        if self.turno_idx == 0:
            self.rodada += 1
            self._add_log(f"--- Rodada {self.rodada} ---")

        j = self.jogador_atual()
        if j.preso:
            self._add_log(f"Vez de {j.nome} [PRESO — clique p/ pular]")
        else:
            self._add_log(f"Vez de {j.nome}. Clique em ROLAR.")

    def _add_log(self, msg: str) -> None:
        """Adiciona uma mensagem ao histórico. Limita a 200 entradas."""
        self.log.append(msg)
        if len(self.log) > 200:
            self.log = self.log[-200:]

    # REQUISITO: Finalização e reinício — reinicia o jogo mantendo os jogadores
    def reiniciar(self) -> None:
        """
        Reinicia o estado do jogo preservando nomes e cores dos jogadores.
        Volta direto para a fase de rolagem inicial.
        """
        nomes_cores = [(j.nome, j.cor) for j in self.jogadores]
        self.__init__()                         # reseta todos os atributos
        for nome, cor in nomes_cores:
            self.adicionar_jogador(nome, cor)   # reinsere os mesmos jogadores
        self.iniciar_rolagem_inicial()           # começa nova partida