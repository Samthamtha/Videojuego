# credits.py
import pygame, sys
WIDTH, HEIGHT = 800, 600
font = pygame.font.SysFont(None, 36)

def show_credits():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # TODO: reemplazar por imagen de créditos si la tienes:
    credits_img = None
    # credits_img = pygame.image.load("assets/images/credits.png")

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                return

        screen.fill((255,255,255))
        title = font.render("CRÉDITOS - Presiona ENTER para volver", True, (0,0,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        if credits_img:
            screen.blit(credits_img, ((WIDTH - credits_img.get_width())//2, 100))
        else:
            lines = [
                "Equipo:",
                "Yo mero - Programador",
                "Integrante 2 - Diseño",
                "Integrante 3 - Sonido"
            ]
            for i,l in enumerate(lines):
                screen.blit(font.render(l, True, (0,0,0)), (100, 120 + i*50))
        pygame.display.flip()
        clock.tick(60)
