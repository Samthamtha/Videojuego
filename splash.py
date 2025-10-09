# splash.py
import pygame
import sys
import time

WIDTH, HEIGHT = 800, 600

def run_splash(idioma):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Splash - Nombre del Juego")
    font = pygame.font.SysFont(None, 80)
    clock = pygame.time.Clock()

    # TODO: Si tienes un video o animación, reemplazar este loop por la reproducción del video
    start_time = time.time()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                return idioma  # salta splash al presionar una tecla

        screen.fill((10, 30, 60))
        text = font.render("NOMBRE DEL JUEGO", True, (255, 255, 255))
        sub = pygame.font.SysFont(None, 28).render("Presiona cualquier tecla", True, (200,200,200))
        screen.blit(text, ((WIDTH - text.get_width())//2, (HEIGHT - text.get_height())//2 - 20))
        screen.blit(sub, ((WIDTH - sub.get_width())//2, (HEIGHT - text.get_height())//2 + 60))

        pygame.display.flip()
        clock.tick(60)

        # opcional: finalizar automáticamente tras X segundos
        if time.time() - start_time > 6:
            return idioma
