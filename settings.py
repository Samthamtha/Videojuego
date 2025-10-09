# settings.py
import pygame
import sys

# Colores globales
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

# Valores configurables
idioma = "Español"
dificultad = "Normal"

# Función para mostrar menú de configuración
def config_menu(screen):
    global idioma, dificultad
    # Crear fuente **después de inicializar Pygame**
    font = pygame.font.SysFont(None, 40)
    options = ["Idioma", "Dificultad", "Volver"]
    selected_option = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Cambiar idioma
                        idioma = "Inglés" if idioma == "Español" else "Español"
                    elif selected_option == 1:  # Cambiar dificultad
                        if dificultad == "Fácil":
                            dificultad = "Normal"
                        elif dificultad == "Normal":
                            dificultad = "Difícil"
                        else:
                            dificultad = "Fácil"
                    elif selected_option == 2:  # Volver
                        return

        # Dibujar menú
        screen.fill(WHITE)
        title = font.render("CONFIGURACIÓN", True, BLACK)
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))
        for i, option in enumerate(options):
            color = RED if i == selected_option else BLACK
            text = font.render(option, True, color)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 200 + i*50))

        info = font.render(f"Idioma: {idioma} | Dificultad: {dificultad}", True, BLACK)
        screen.blit(info, (screen.get_width()//2 - info.get_width()//2, 500))

        pygame.display.flip()
        clock.tick(60)
