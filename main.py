# main.py
import pygame
import sys
from menu import run_menu
from level_select import run_level_select
from level1 import run_level1

def main():
    pygame.init()  # Inicializar pygame antes de cualquier fuente o pantalla
    screen = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("Juego del Río")

    # Valores iniciales
    dificultad = "Normal"
    idioma = "Español"

    while True:
        # Menú principal
        accion, dificultad, idioma = run_menu(screen, dificultad, idioma)

        if accion == "jugar":
            # Selección de nivel
            nivel = run_level_select(screen)
            
            # Solo manejaremos el primer nivel por ahora
            if nivel == "Nivel 1":
                run_level1(dificultad, idioma, screen)

        elif accion == "salir":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
