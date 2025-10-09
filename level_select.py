import pygame
import sys

def run_level_select(screen):
    # Crear fuente **después de init**
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    selected_option = 0
    options = ["Nivel 1", "Nivel 2", "Nivel 3", "Volver"]

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
                    return options[selected_option]  # Retorna la opción seleccionada

        screen.fill((255, 255, 255))
        title = font.render("SELECCIONA EL NIVEL", True, (0,0,0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        for i, option in enumerate(options):
            color = (200,0,0) if i == selected_option else (0,0,0)
            text = font.render(option, True, color)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 200 + i*50))

        pygame.display.flip()
        clock.tick(60)
