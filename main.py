"""
main.py - Ponto de entrada do The Maze Runner (interface Pygame).

RESPONSABILIDADE: Inicialização do programa — instancia a Interface e
                  chama o loop principal.

Execute com:
    python main.py   (Linux/Mac)
    py main.py       (Windows)

────────────────────────────────────────────────────────
DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL
────────────────────────────────────────────────────────
Este projeto utilizou ferramentas de I.A. generativa
(Claude - Anthropic) como auxílio no desenvolvimento.
A I.A. foi utilizada para:
  • Identificar e corrigir bugs visuais na tela inicial
  • Revisar a lógica dos loops para garantir estabilidade
  • Adicionar comentários explicativos aos requisitos
  • Sugerir melhorias de organização do código

Todo o código foi revisado, compreendido e validado
pelos integrantes do grupo antes de ser incorporado
ao projeto.
────────────────────────────────────────────────────────

DIVISÃO DE TAREFAS DO GRUPO:
  Jogador N — jogador.py  : [Nome do integrante]
  Jogador N — tabuleiro.py: [Nome do integrante]
  Jogador N — jogo.py     : [Nome do integrante]
  Jogador N — interface.py: [Nome do integrante]
  Jogador N — main.py     : [Nome do integrante]
"""

# REQUISITO: Importação do módulo de interface gráfica
from interface import Interface


# REQUISITO: Função principal — inicializa e executa o jogo
def main() -> None:
    """Cria a instância da Interface e inicia o loop principal."""
    app = Interface()
    app.rodar()     # loop principal — só retorna quando a janela é fechada


# REQUISITO: Guarda de execução — garante que main() só roda quando
# este arquivo é executado diretamente (não quando importado)
if __name__ == "__main__":
    main()