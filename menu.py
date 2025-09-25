# menu.py
import pygame
import sys
from settings import config_menu, idioma, dificultad

def credits_menu(screen):
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        screen.fill((255, 255, 255))
        title = font.render("CRÉDITOS", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        text1 = font.render("Juego desarrollado por:", True, (0,0,0))
        text2 = font.render("Tu Nombre Aquí", True, (200,0,0))
        screen.blit(text1, (screen.get_width()//2 - text1.get_width()//2, 200))
        screen.blit(text2, (screen.get_width()//2 - text2.get_width()//2, 260))

        back_text = font.render("Presiona ENTER para volver", True, (0,0,0))
        screen.blit(back_text, (screen.get_width()//2 - back_text.get_width()//2, 500))

        pygame.display.flip()
        clock.tick(60)

def run_menu(screen, dificultad, idioma):
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()
    main_menu_options = ["Iniciar Juego", "Configuración", "Créditos", "Salir"]
    selected_option = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(main_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(main_menu_options)
                elif event.key == pygame.K_RETURN:
                    opcion = main_menu_options[selected_option]
                    if opcion == "Iniciar Juego":
                        return "jugar", dificultad, idioma
                    elif opcion == "Configuración":
                        config_menu(screen)
                    elif opcion == "Créditos":
                        credits_menu(screen)
                    elif opcion == "Salir":
                        return "salir", dificultad, idioma

        # Dibujar menú
        screen.fill((255, 255, 255))
        title = font.render("MENÚ PRINCIPAL", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        for i, option in enumerate(main_menu_options):
            color = (200,0,0) if i == selected_option else (0,0,0)
            text = font.render(option, True, color)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 200 + i*60))

        pygame.display.flip()
        clock.tick(60)
