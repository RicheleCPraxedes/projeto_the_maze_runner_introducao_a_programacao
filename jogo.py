import pygame
import random
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA, ALTURA = 1000, 500
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("The Maze Runner - O Jogo de Tabuleiro")
relogio = pygame.time.Clock()

# Cores (RGB)
COR_FUNDO = (20, 20, 20)
COR_TABULEIRO = (50, 50, 50)
COR_TEXTO = (255, 255, 255)
COR_BOTAO = (0, 150, 0)
COR_BOTAO_HOVER = (0, 200, 0)

# Cores das Casas Especiais
C_NORMAL = (100, 100, 100)
C_AVANCE = (46, 204, 113)   # Verde
C_RETROCEDE = (231, 76, 60) # Vermelho
C_PRESO = (241, 196, 15)    # Amarelo

# Definição do Tabuleiro (20 casas)
# Efeitos: "normal", "avance" (+2), "retrocede" (-2), "preso" (pula o próximo turno)
CASAS_EFEITOS = ["normal"] * 21
CASAS_EFEITOS[4] = "avance"
CASAS_EFEITOS[8] = "retrocede"
CASAS_EFEITOS[12] = "preso"
CASAS_EFEITOS[15] = "avance"
CASAS_EFEITOS[18] = "retrocede"

# Configurações dos Jogadores
# Posição inicial é 0 (fora ou na primeira casa visual)
jogadores = {
    1: {"nome": "Corredor Vermelho", "pos": 0, "cor": (255, 50, 50), "preso": False, "Y_offset": -15},
    2: {"nome": "Corredor Azul", "pos": 0, "cor": (50, 50, 255), "preso": False, "Y_offset": 15}
}
turno_atual = 1

# Variáveis do Dado e Mensagens
dado_resultado = 0
mensagem_efeito = "Clique em 'Lançar Dado' para começar!"
fim_de_jogo = False

# Fontes
fonte_principal = pygame.font.SysFont("Arial", 24)
fonte_titulo = pygame.font.SysFont("Arial", 36, bold=True)

# Dimensões visuais das casas
LARGURA_CASA = 45
ALTURA_CASA = 80
X_INICIAL = 50
Y_TABULEIRO = 200

def desenhar_tabuleiro():
    for i in range(1, 21):
        # Determina a cor da casa baseado no efeito
        efeito = CASAS_EFEITOS[i]
        if efeito == "avance": cor = C_AVANCE
        elif efeito == "retrocede": cor = C_RETROCEDE
        elif efeito == "preso": cor = C_PRESO
        else: cor = C_NORMAL
        
        x = X_INICIAL + (i - 1) * LARGURA_CASA
        pygame.draw.rect(tela, cor, (x, Y_TABULEIRO, LARGURA_CASA - 5, ALTURA_CASA))
        
        # Número da casa
        txt_num = fonte_principal.render(str(i), True, (0, 0, 0))
        tela.blit(txt_num, (x + 10, Y_TABULEIRO + 25))

def desenhar_jogadores():
    for j_id, dados in jogadores.items():
        pos = dados["pos"]
        if pos > 0: # Só desenha se já tiver entrado no tabuleiro
            x = X_INICIAL + (pos - 1) * LARGURA_CASA + (LARGURA_CASA // 2) - 2
            y = Y_TABULEIRO + (ALTURA_CASA // 2) + dados["Y_offset"]
            pygame.draw.circle(tela, dados["cor"], (x, y), 12)

def rodar_turno():
    global dado_resultado, turno_atual, mensagem_efeito, fim_de_jogo
    
    jogador = jogadores[turno_atual]
    
    # Verifica se o jogador está preso (pulando a vez)
    if j_id_preso := jogador["preso"]:
        mensagem_efeito = f"{jogador['nome']} estava preso e perdeu a vez!"
        jogador["preso"] = False
        proximo_turno()
        return

    # 1. Rola o dado (1 a 6)
    dado_resultado = random.randint(1, 6)
    
    # 2. Anda as casas
    jogador["pos"] += dado_resultado
    mensagem_efeito = f"{jogador['nome']} tirou {dado_resultado} e moveu para a casa {jogador['pos']}."

    # Verifica condição de vitória imediata antes de aplicar efeitos ruins
    if jogador["pos"] >= 20:
        jogador["pos"] = 20
        mensagem_efeito = f"FIM DE JOGO! {jogador['nome']} escapou do Labirinto!"
        fim_de_jogo = True
        return

    # 3. Aplica o efeito da casa atual
    efeito = CASAS_EFEITOS[jogador["pos"]]
    if efeito == "avance":
        jogador["pos"] += 2
        mensagem_efeito += " Casa Especial! Avançou mais 2 casas."
    elif efeito == "retrocede":
        jogador["pos"] = max(1, jogador["pos"] - 2)
        mensagem_efeito += " Emboscada! Voltou 2 casas."
    elif efeito == "preso":
        jogador["preso"] = True
        mensagem_efeito += " Portas Fechadas! Ficará 1 turno sem jogar."

    # Garante que não passou do limite após efeitos
    if jogador["pos"] >= 20:
        jogador["pos"] = 20
        mensagem_efeito = f"FIM DE JOGO! {jogador['nome']} escapou do Labirinto!"
        fim_de_jogo = True
        return

    # 4. Passa o turno
    proximo_turno()

def proximo_turno():
    global turno_atual
    if not fim_de_jogo:
        turno_atual = 2 if turno_atual == 1 else 1

# Loop Principal do Jogo
while True:
    tela.fill(COR_FUNDO)
    
    # Captura de Eventos
    mouse_pos = pygame.mouse.get_pos()
    btn_rect = pygame.Rect(400, 350, 200, 50)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if btn_rect.collidepoint(mouse_pos) and not fim_de_jogo:
                rodar_turno()

    # Desenhar Elementos da Interface
    desenhar_tabuleiro()
    desenhar_jogadores()
    
    # Títulos e Textos Informativos
    txt_titulo = fonte_titulo.render("THE MAZE RUNNER: CORRIDA PELO LABIRINTO", True, COR_TEXTO)
    tela.blit(txt_titulo, (220, 30))
    
    # Informações do turno
    cor_turno = jogadores[turno_atual]["cor"]
    txt_turno = fonte_principal.render(f"Turno de: {jogadores[turno_atual]['nome']}", True, cor_turno)
    if not fim_de_jogo:
        tela.blit(txt_turno, (400, 110))
    
    # Mostrador do Dado e Eventos
    txt_dado = fonte_principal.render(f"Último Dado: {dado_resultado if dado_resultado > 0 else '-'}", True, COR_TEXTO)
    tela.blit(txt_dado, (430, 150))
    
    txt_msg = fonte_principal.render(mensagem_efeito, True, COR_TEXTO)
    tela.blit(txt_msg, (100, 300))
    
    # Legenda de Cores
    pygame.draw.rect(tela, C_AVANCE, (50, 430, 20, 20))
    tela.blit(fonte_principal.render("Avance 2 casas", True, COR_TEXTO), (80, 425))
    
    pygame.draw.rect(tela, C_RETROCEDE, (300, 430, 20, 20))
    tela.blit(fonte_principal.render("Volte 2 casas", True, COR_TEXTO), (330, 425))
    
    pygame.draw.rect(tela, C_PRESO, (550, 430, 20, 20))
    tela.blit(fonte_principal.render("Prende por 1 turno", True, COR_TEXTO), (580, 425))

    # Desenhar o Botão de Jogar Dado
    if not fim_de_jogo:
        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(tela, COR_BOTAO_HOVER, btn_rect, border_radius=10)
        else:
            pygame.draw.rect(tela, COR_BOTAO, btn_rect, border_radius=10)
            
        txt_btn = fonte_principal.render("Lançar Dado", True, COR_TEXTO)
        tela.blit(txt_btn, (440, 360))
    else:
        txt_reiniciar = fonte_titulo.render("Parabéns ao vencedor!", True, (0, 255, 0))
        tela.blit(txt_reiniciar, (330, 350))

    pygame.display.flip()
    relogio.tick(30)
