"""
main.py - Ponto de entrada do The Maze Runner (interface Pygame).

Execute com:
    python main.py
"""

from interface import Interface


def main() -> None:
    app = Interface()
    app.rodar()


if __name__ == "__main__":
    main()
