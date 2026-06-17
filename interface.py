"""
interface.py - Interface gráfica Pygame do The Maze Runner.

RESPONSABILIDADE: Toda a camada visual do jogo — tela de setup, tabuleiro,
                  painel lateral, animação do dado, log de eventos e botões.
"""

import pygame
import sys
from tabuleiro import (CELULAS, GRID_POS, CORES_RGB, TEXTO_COR,
                       TOTAL_CELULAS, cor_da_celula)
from jogador import VIDA_MAXIMA
from jogo import EstadoJogo, ST_SETUP_NOMES, ST_ROLAGEM_INIT, ST_AGUARDA_TURNO, ST_FIM

# ── Dimensões da janela ────────────────────────────────────────────────
LARGURA   = 1100
ALTURA    = 780
FPS       = 60

# Tabuleiro
COLS      = 10
ROWS      = 6
CEL_W     = 72
CEL_H     = 72
CEL_GAP   = 4
TAB_X     = 20
TAB_Y     = 20

# Painel lateral (à direita do tabuleiro)
PAINEL_X  = TAB_X + COLS * (CEL_W + CEL_GAP) + 20
PAINEL_W  = LARGURA - PAINEL_X - 10

# REQUISITO: Paleta de cores da interface
BG        = (15,  15,  25)
PAINEL_BG = (25,  25,  40)
BORDA     = (60,  60,  90)
BRANCO    = (240, 240, 240)
CINZA     = (140, 140, 160)
AMARELO   = (255, 215,   0)
VERMELHO  = (210,  50,  50)
VERDE_UI  = ( 50, 200,  80)
AZUL_UI   = ( 60, 140, 255)

# Cores dos peões dos dois jogadores
COR_J1 = (255,  80,  80)
COR_J2 = ( 80, 180, 255)


def _pixel(col: int, row: int) -> tuple[int, int]:
    """Converte posição do grid (col, row) para pixel (canto superior esquerdo)."""
    x = TAB_X + col * (CEL_W + CEL_GAP)
    y = TAB_Y + row * (CEL_H + CEL_GAP)
    return x, y


def _centro(col: int, row: int) -> tuple[int, int]:
    """Retorna o pixel do centro de uma célula do grid."""
    px, py = _pixel(col, row)
    return px + CEL_W // 2, py + CEL_H // 2


# REQUISITO: Componente de botão clicável com efeito de hover
class Botao:
    def __init__(self, x, y, w, h, texto, cor_fundo=AZUL_UI, cor_texto=BRANCO):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.cor_fundo = cor_fundo
        self.cor_hover = tuple(min(255, c + 40) for c in cor_fundo)
        self.cor_texto = cor_texto
        self.ativo = True

    def desenhar(self, surf: pygame.Surface, fonte: pygame.font.Font) -> None:
        mx, my = pygame.mouse.get_pos()
        cor = self.cor_hover if (self.rect.collidepoint(mx, my) and self.ativo) else self.cor_fundo
        if not self.ativo:
            cor = (60, 60, 70)
        pygame.draw.rect(surf, cor, self.rect, border_radius=10)
        pygame.draw.rect(surf, BORDA, self.rect, 2, border_radius=10)
        txt = fonte.render(self.texto, True, self.cor_texto if self.ativo else CINZA)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def clicado(self, evento: pygame.event.Event) -> bool:
        """Retorna True se este botão foi clicado com o botão esquerdo do mouse."""
        return (self.ativo
                and evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
                and self.rect.collidepoint(evento.pos))


# REQUISITO: Componente de campo de texto para entrada do nome dos jogadores
class CaixaTexto:
    """Campo de entrada de texto simples com suporte a placeholder."""
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = ""
        self.placeholder = placeholder
        self.ativo = False

    def handle_event(self, evento: pygame.event.Event) -> None:
        """Processa cliques (ativa/desativa) e digitação."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.ativo = self.rect.collidepoint(evento.pos)
        if evento.type == pygame.KEYDOWN and self.ativo:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif evento.unicode.isprintable() and len(self.texto) < 16:
                self.texto += evento.unicode

    def desenhar(self, surf: pygame.Surface, fonte: pygame.font.Font) -> None:
        cor_borda = AMARELO if self.ativo else BORDA
        pygame.draw.rect(surf, (35, 35, 55), self.rect, border_radius=8)
        pygame.draw.rect(surf, cor_borda, self.rect, 2, border_radius=8)
        exibir = self.texto if self.texto else self.placeholder
        cor = BRANCO if self.texto else CINZA
        txt = fonte.render(exibir, True, cor)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + (self.rect.h - txt.get_height()) // 2))


class Interface:
    # REQUISITO: Inicialização do Pygame e criação da janela
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("The Maze Runner")
        self.clock = pygame.time.Clock()

        # Fontes usadas em diferentes tamanhos
        self.fonte_titulo = pygame.font.SysFont("consolas", 26, bold=True)
        self.fonte_grande = pygame.font.SysFont("consolas", 18, bold=True)
        self.fonte_media  = pygame.font.SysFont("consolas", 14)
        self.fonte_pequena= pygame.font.SysFont("consolas", 12)

        # Instância da lógica do jogo (sem Pygame)
        self.jogo = EstadoJogo()

        # ── Widgets da tela de setup ──────────────────────────────────
        cx = LARGURA // 2
        self.cx1 = CaixaTexto(cx - 180, 400, 360, 44, "Nome do Jogador 1")
        self.cx2 = CaixaTexto(cx - 180, 480, 360, 44, "Nome do Jogador 2")
        self.btn_iniciar = Botao(cx - 100, 560, 200, 48, "INICIAR JOGO", VERDE_UI, (10,10,10))

        # ── Botões do jogo principal ──────────────────────────────────
        self.btn_rolar = Botao(PAINEL_X + 20, 600, PAINEL_W - 40, 52, "🎲  ROLAR DADO", AZUL_UI)
        self.btn_reiniciar = Botao(PAINEL_X + 20, 660, PAINEL_W - 40, 44, "↺  JOGAR NOVAMENTE", (80, 60, 130))

        # ── Animação do dado ──────────────────────────────────────────
        self.dado_anim_frames = 0
        self.dado_valor_exibido = 0
        self.dado_valor_final = 0

        # ── Scroll do log ─────────────────────────────────────────────
        self.log_scroll = 0

    # ── Loop principal ─────────────────────────────────────────────────

    # REQUISITO: Loop principal — mantém o jogo rodando continuamente
    def rodar(self) -> None:
        """
        Loop principal do Pygame. Executa enquanto o jogo estiver aberto.
        A cada frame:
          1. Limita FPS com clock.tick
          2. Processa todos os eventos (teclado, mouse, fechar janela)
          3. Atualiza animações
          4. Desenha a tela atual
          5. Exibe o frame (display.flip)
        """
        while True:                             # loop infinito — sai só pelo evento QUIT
            dt = self.clock.tick(FPS)           # limita a 60 fps e retorna delta-time
            eventos = pygame.event.get()
            for ev in eventos:
                # REQUISITO: Finalização — fecha o jogo ao fechar a janela
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()              # encerra o processo corretamente
                self._handle_evento(ev)

            self._atualizar(dt)
            self._desenhar()
            pygame.display.flip()           # envia o frame para a tela

    # ── Eventos ────────────────────────────────────────────────────────

    # REQUISITO: Tratamento de eventos — distribuído por estado do jogo
    def _handle_evento(self, ev: pygame.event.Event) -> None:
        """
        Roteia cada evento para o handler correto conforme o estado atual.
        Isso garante que botões só respondam no momento certo do jogo.
        """
        estado = self.jogo.estado

        if estado == ST_SETUP_NOMES:
            # Fase de cadastro: campos de texto e botão iniciar
            self.cx1.handle_event(ev)
            self.cx2.handle_event(ev)
            if self.btn_iniciar.clicado(ev):
                n1 = self.cx1.texto.strip() or "Jogador 1"
                n2 = self.cx2.texto.strip() or "Jogador 2"
                self.jogo.adicionar_jogador(n1, COR_J1)
                self.jogo.adicionar_jogador(n2, COR_J2)
                self.jogo.iniciar_rolagem_inicial()

        elif estado == ST_ROLAGEM_INIT:
            # REQUISITO: Rolagem inicial — cada jogador clica uma vez
            if self.btn_rolar.clicado(ev):
                self.jogo.rolar_inicial()
                # Pega o valor da última rolagem para animar o dado
                fase_atual = min(self.jogo._init_fase, len(self.jogo.jogadores) - 1)
                valor = self.jogo._init_rolls.get(
                    self.jogo.jogadores[fase_atual].nome, 0)
                self._iniciar_anim_dado(valor)

        elif estado == ST_AGUARDA_TURNO:
            # REQUISITO: Turno de jogo — clique rola o dado e avança o estado
            if self.btn_rolar.clicado(ev):
                resultado = self.jogo.rolar_turno()
                if resultado:
                    self._iniciar_anim_dado(resultado)

        elif estado == ST_FIM:
            # REQUISITO: Reinício — volta ao começo com os mesmos jogadores
            if self.btn_reiniciar.clicado(ev):
                self.jogo.reiniciar()
                self.log_scroll = 0

        # Scroll com mouse no log de eventos
        if ev.type == pygame.MOUSEWHEEL:
            self.log_scroll = max(0, self.log_scroll - ev.y * 2)

    # ── Animação do dado ───────────────────────────────────────────────

    def _iniciar_anim_dado(self, valor_final: int) -> None:
        """Dispara 20 frames de animação aleatória antes de mostrar o valor real."""
        self.dado_anim_frames = 20
        self.dado_valor_final = valor_final

    def _atualizar(self, dt: int) -> None:
        """Atualiza o estado de animações a cada frame."""
        import random
        if self.dado_anim_frames > 0:
            self.dado_anim_frames -= 1
            self.dado_valor_exibido = random.randint(1, 6)  # número "chacoalhando"
        else:
            self.dado_valor_exibido = self.dado_valor_final  # mostra o resultado final

        # Auto-scroll: mantém o log sempre exibindo as mensagens mais recentes
        self.log_scroll = max(0, len(self.jogo.log) - 14)

    # ── Desenho principal ──────────────────────────────────────────────

    def _desenhar(self) -> None:
        """Limpa a tela e desenha o frame atual conforme o estado do jogo."""
        self.tela.fill(BG)

        if self.jogo.estado == ST_SETUP_NOMES:
            self._desenhar_setup()
        else:
            self._desenhar_tabuleiro()
            self._desenhar_painel()

        # Borda decorativa ao redor da janela inteira
        pygame.draw.rect(self.tela, BORDA, pygame.Rect(0, 0, LARGURA, ALTURA), 2)

    # ── Tela de setup ──────────────────────────────────────────────────

    # REQUISITO: Tela inicial — cadastro de nomes e legenda de células
    def _desenhar_setup(self) -> None:
        """
        Desenha a tela de configuração antes do jogo começar.

        CORREÇÃO DE BUG: A legenda de cores e os campos de nome
        estavam sobrepostos. Solução: a legenda começa em y=200 e
        termina em ~y=356. Os campos de texto foram movidos para
        y=400 e y=480 (abaixo da legenda) para não sobrepor.
        """
        cx = LARGURA // 2

        # Título do jogo
        t = self.fonte_titulo.render("⚡  THE MAZE RUNNER", True, AMARELO)
        self.tela.blit(t, t.get_rect(center=(cx, 120)))
        sub = self.fonte_media.render("Dois jogadores — chegar ao FIM vivo!", True, CINZA)
        self.tela.blit(sub, sub.get_rect(center=(cx, 155)))

        # Subtítulo da legenda
        leg_titulo = self.fonte_media.render("LEGENDA DAS CÉLULAS:", True, BRANCO)
        self.tela.blit(leg_titulo, leg_titulo.get_rect(center=(cx, 185)))

        # Legenda de cores (começa em y=200, cada item ocupa 26px → termina em ~356)
        legenda = [
            ("BRANCO",   CORES_RGB["branco"],   "Espaço neutro"),
            ("VERMELHO", CORES_RGB["vermelho"],  "Perde 3 vidas"),
            ("VERDE",    CORES_RGB["verde"],     "Ganha 1 vida"),
            ("AMARELO",  CORES_RGB["amarelo"],   "Perde 1 turno"),
            ("AZUL",     CORES_RGB["azul"],      "Joga novamente"),
            ("PRETO",    CORES_RGB["preto"],     "Volta ao início"),
        ]
        ly = 200
        for nome, cor, desc in legenda:
            pygame.draw.rect(self.tela, cor, (cx - 180, ly, 22, 22), border_radius=4)
            pygame.draw.rect(self.tela, BORDA, (cx - 180, ly, 22, 22), 1, border_radius=4)
            txt = self.fonte_pequena.render(f"{nome} — {desc}", True, CINZA)
            self.tela.blit(txt, (cx - 150, ly + 4))
            ly += 26
        # ly está agora em ~356 — campos de nome ficam abaixo

        # Labels dos campos (posicionados ABAIXO da legenda — bug corrigido)
        l1 = self.fonte_media.render("Jogador 1 (vermelho):", True, COR_J1)
        self.tela.blit(l1, (cx - 180, 375))
        l2 = self.fonte_media.render("Jogador 2 (azul):", True, COR_J2)
        self.tela.blit(l2, (cx - 180, 455))

        self.cx1.desenhar(self.tela, self.fonte_media)
        self.cx2.desenhar(self.tela, self.fonte_media)
        self.btn_iniciar.desenhar(self.tela, self.fonte_grande)

    # ── Tabuleiro ──────────────────────────────────────────────────────

    # REQUISITO: Renderização do tabuleiro e posição dos peões
    def _desenhar_tabuleiro(self) -> None:
        """
        Desenha todas as células do tabuleiro e os peões dos jogadores.
        Destaca com borda amarela a célula onde está o jogador do turno atual.
        """
        jogadores = self.jogo.jogadores

        for idx, cor_nome in enumerate(CELULAS):
            col, row = GRID_POS[idx]
            px, py = _pixel(col, row)
            cor_rgb = CORES_RGB[cor_nome]

            # Verifica se esta célula deve ser destacada (jogador atual)
            destacar = False
            if self.jogo.estado == ST_AGUARDA_TURNO:
                j = self.jogo.jogador_atual()
                if j.posicao == idx:
                    destacar = True

            # Fundo da célula
            pygame.draw.rect(self.tela, cor_rgb,
                             (px, py, CEL_W, CEL_H), border_radius=8)

            if destacar:
                pygame.draw.rect(self.tela, AMARELO,
                                 (px - 2, py - 2, CEL_W + 4, CEL_H + 4),
                                 3, border_radius=10)
            else:
                pygame.draw.rect(self.tela, BORDA,
                                 (px, py, CEL_W, CEL_H), 1, border_radius=8)

            # Rótulo com o efeito da célula
            label = {
                "inicio": "INI", "fim": "FIM",
                "branco": "", "vermelho": "-3♥",
                "verde": "+1♥", "amarelo": "⏸",
                "azul": "↻", "preto": "↩",
            }.get(cor_nome, "")
            if label:
                tc = TEXTO_COR[cor_nome]
                txt = self.fonte_pequena.render(label, True, tc)
                self.tela.blit(txt, txt.get_rect(center=(px + CEL_W//2, py + CEL_H//2)))

            # Número do índice da célula (canto superior esquerdo)
            num = self.fonte_pequena.render(str(idx), True,
                                            tuple(min(255, c + 80) for c in cor_rgb)
                                            if cor_nome == "preto" else (0,0,0))
            self.tela.blit(num, (px + 4, py + 4))

        # REQUISITO: Renderização dos peões no tabuleiro
        offsets = [(-12, 0), (12, 0)]   # deslocamento lateral para não sobrepor
        for ji, j in enumerate(jogadores):
            if not j.vivo:
                continue    # não desenha peão de jogador eliminado
            col, row = GRID_POS[j.posicao]
            cx_p, cy_p = _centro(col, row)
            ox, oy = offsets[ji]
            # Sombra do peão
            pygame.draw.circle(self.tela, (0, 0, 0),
                                (cx_p + ox + 2, cy_p + oy + 2 + 10), 10)
            # Corpo do peão
            pygame.draw.circle(self.tela, j.cor, (cx_p + ox, cy_p + oy), 12)
            pygame.draw.circle(self.tela, BRANCO, (cx_p + ox, cy_p + oy), 12, 2)
            # Inicial do nome sobre o peão
            ini = self.fonte_pequena.render(j.nome[0].upper(), True, (10, 10, 10))
            self.tela.blit(ini, ini.get_rect(center=(cx_p + ox, cy_p + oy)))

    # ── Painel lateral ─────────────────────────────────────────────────

    # REQUISITO: Painel lateral — informações do jogo em tempo real
    def _desenhar_painel(self) -> None:
        """Desenha o painel lateral com título, cards dos jogadores, dado e log."""
        pygame.draw.rect(self.tela, PAINEL_BG,
                         (PAINEL_X, 0, PAINEL_W, ALTURA), border_radius=12)
        pygame.draw.rect(self.tela, BORDA,
                         (PAINEL_X, 0, PAINEL_W, ALTURA), 2, border_radius=12)

        y = 15
        # Título do painel
        t = self.fonte_grande.render("MAZE RUNNER", True, AMARELO)
        self.tela.blit(t, t.get_rect(centerx=PAINEL_X + PAINEL_W // 2, y=y))
        y += 30

        # Número da rodada atual
        if self.jogo.rodada:
            r = self.fonte_media.render(f"Rodada {self.jogo.rodada}", True, CINZA)
            self.tela.blit(r, r.get_rect(centerx=PAINEL_X + PAINEL_W // 2, y=y))
        y += 28

        pygame.draw.line(self.tela, BORDA,
                         (PAINEL_X + 10, y), (PAINEL_X + PAINEL_W - 10, y))
        y += 10

        # Cards dos jogadores (vida, posição, status)
        for ji, j in enumerate(self.jogo.jogadores):
            y = self._desenhar_card_jogador(j, ji, y)
            y += 8

        pygame.draw.line(self.tela, BORDA,
                         (PAINEL_X + 10, y), (PAINEL_X + PAINEL_W - 10, y))
        y += 10

        # Animação do dado (exibida apenas quando há valor para mostrar)
        if self.dado_valor_exibido:
            self._desenhar_dado(PAINEL_X + PAINEL_W // 2, y + 45)
            y += 100

        # Log de eventos
        self._desenhar_log(y)

        # Botões contextuais (variam conforme o estado)
        estado = self.jogo.estado
        if estado == ST_ROLAGEM_INIT:
            fase = self.jogo._init_fase
            if fase < len(self.jogo.jogadores):
                nome = self.jogo.jogadores[fase].nome
                self.btn_rolar.texto = f"🎲  {nome} — ROLAR 2 DADOS"
            self.btn_rolar.ativo = True
            self.btn_rolar.desenhar(self.tela, self.fonte_grande)

        elif estado == ST_AGUARDA_TURNO:
            j = self.jogo.jogador_atual()
            self.btn_rolar.texto = f"🎲  {j.nome} — ROLAR"
            self.btn_rolar.ativo = True
            self.btn_rolar.desenhar(self.tela, self.fonte_grande)

        elif estado == ST_FIM:
            # REQUISITO: Tela de fim — mostra botão para reiniciar
            self.btn_reiniciar.desenhar(self.tela, self.fonte_grande)

    def _desenhar_card_jogador(self, j, ji: int, y: int) -> int:
        """Desenha o card de status de um jogador (nome, vida, posição, status)."""
        px = PAINEL_X + 12
        pw = PAINEL_W - 24

        # Destaque visual para o jogador do turno atual
        eh_vez = (self.jogo.estado == ST_AGUARDA_TURNO and
                  self.jogo.jogador_atual() == j)
        cor_card = (35, 50, 70) if eh_vez else (30, 30, 48)
        borda_card = j.cor if eh_vez else BORDA

        pygame.draw.rect(self.tela, cor_card,
                         (px, y, pw, 80), border_radius=8)
        pygame.draw.rect(self.tela, borda_card,
                         (px, y, pw, 80), 2, border_radius=8)

        # Bolinha miniatura do peão
        pygame.draw.circle(self.tela, j.cor, (px + 20, y + 22), 12)
        pygame.draw.circle(self.tela, BRANCO, (px + 20, y + 22), 12, 2)
        ini = self.fonte_pequena.render(j.nome[0].upper(), True, (10,10,10))
        self.tela.blit(ini, ini.get_rect(center=(px + 20, y + 22)))

        # Nome do jogador
        cor_nome = AMARELO if eh_vez else BRANCO
        nome_txt = self.fonte_grande.render(j.nome, True, cor_nome)
        self.tela.blit(nome_txt, (px + 38, y + 8))

        # Status textual (vencedor, eliminado, preso, vez)
        status = ""
        if not j.vivo:
            status = "💀 ELIMINADO"
        elif j.vencedor:
            status = "🏆 VENCEDOR!"
        elif j.preso:
            status = "🔒 PRESO"
        elif eh_vez:
            status = "← SUA VEZ"
        if status:
            s = self.fonte_pequena.render(status, True, CINZA)
            self.tela.blit(s, (px + 38, y + 30))

        # Posição no tabuleiro
        pos_txt = self.fonte_pequena.render(f"Pos: {j.posicao}", True, CINZA)
        self.tela.blit(pos_txt, (px + 38, y + 46))

        # REQUISITO: Barra de vida visual
        bx = px + 12
        by = y + 62
        bw = pw - 24
        bh = 10
        pygame.draw.rect(self.tela, (50, 50, 60), (bx, by, bw, bh), border_radius=4)
        vida_pct = j.vida / VIDA_MAXIMA
        cor_vida = (VERDE_UI if vida_pct > 0.5
                    else AMARELO if vida_pct > 0.25 else VERMELHO)
        pygame.draw.rect(self.tela, cor_vida,
                         (bx, by, int(bw * vida_pct), bh), border_radius=4)
        vida_txt = self.fonte_pequena.render(f"♥ {j.vida}/{VIDA_MAXIMA}", True, BRANCO)
        self.tela.blit(vida_txt, (bx + bw + 4, by - 1))

        return y + 86

    def _desenhar_dado(self, cx: int, cy: int) -> None:
        """Desenha o quadrado do dado com o valor atual (animado ou final)."""
        v = self.dado_valor_exibido
        if not v:
            return
        dw = 64
        pygame.draw.rect(self.tela, BRANCO,
                         (cx - dw//2, cy - dw//2, dw, dw), border_radius=10)
        pygame.draw.rect(self.tela, BORDA,
                         (cx - dw//2, cy - dw//2, dw, dw), 2, border_radius=10)
        num = self.fonte_titulo.render(str(v), True, (20, 20, 30))
        self.tela.blit(num, num.get_rect(center=(cx, cy)))

    # REQUISITO: Log de eventos — histórico rolável das ações do jogo
    def _desenhar_log(self, y_inicio: int) -> None:
        """Exibe as últimas mensagens do log. Suporta scroll com a roda do mouse."""
        log_area_h = 580 - y_inicio
        log_linhas = self.jogo.log
        scroll = min(self.log_scroll, max(0, len(log_linhas) - 14))
        visiveis = log_linhas[scroll: scroll + 18]

        pygame.draw.rect(self.tela, (20, 20, 35),
                         (PAINEL_X + 10, y_inicio, PAINEL_W - 20, log_area_h),
                         border_radius=6)

        y = y_inicio + 6
        for linha in visiveis:
            if y + 16 > y_inicio + log_area_h:
                break
            # Coloração da linha conforme o tipo de evento
            if "VENCEU" in linha or "vence" in linha or "🏆" in linha:
                cor = AMARELO
            elif "eliminado" in linha or "💀" in linha or "perde" in linha.lower():
                cor = VERMELHO
            elif "Rodada" in linha:
                cor = AZUL_UI
            elif "joga novamente" in linha or "↻" in linha:
                cor = AZUL_UI
            elif "Preso" in linha or "preso" in linha or "⏸" in linha:
                cor = (230, 180, 0)
            else:
                cor = CINZA
            # Quebra linhas longas em duas partes de até 38 chars cada
            max_c = 38
            if len(linha) <= max_c:
                partes = [linha]
            else:
                partes = [linha[:max_c], "  " + linha[max_c:max_c*2]]
            for parte in partes:
                if y + 16 > y_inicio + log_area_h:
                    break
                txt = self.fonte_pequena.render(parte, True, cor)
                self.tela.blit(txt, (PAINEL_X + 14, y))
                y += 15