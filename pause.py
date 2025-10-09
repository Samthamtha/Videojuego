# pause.py
import pygame, sys

def mostrar_menu_pausa(VENTANA, ANCHO, ALTO):
    BLANCO = (255, 255, 255)
    ROJO = (200, 50, 50)
    AZUL = (50, 100, 200)
    fuente = pygame.font.SysFont("Arial", 35)
    clock = pygame.time.Clock()

    def dibujar_texto(texto, fuente, color, superficie, x, y):
        render = fuente.render(texto, True, color)
        rect = render.get_rect(center=(x, y))
        superficie.blit(render, rect)
        return rect  

    boton_reanudar = boton_reiniciar = boton_salir = pygame.Rect(0,0,0,0)
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_reanudar.collidepoint(evento.pos):
                    return "reanudar"
                if boton_reiniciar.collidepoint(evento.pos):
                    return "reiniciar"
                if boton_salir.collidepoint(evento.pos):
                    return "salir"

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return "reanudar"
                if evento.key == pygame.K_q:
                    return "salir"

        overlay = pygame.Surface((ANCHO, ALTO))
        overlay.set_alpha(180)
        overlay.fill(AZUL)
        VENTANA.blit(overlay, (0, 0))

        dibujar_texto("MENÚ DE PAUSA", fuente, BLANCO, VENTANA, ANCHO//2, 150)
        boton_reanudar = dibujar_texto("Reanudar (R)", fuente, ROJO, VENTANA, ANCHO//2, 250)
        boton_reiniciar = dibujar_texto("Reiniciar", fuente, ROJO, VENTANA, ANCHO//2, 320)
        boton_salir = dibujar_texto("Salir (Q)", fuente, ROJO, VENTANA, ANCHO//2, 390)

        pygame.display.flip()
        clock.tick(60)
