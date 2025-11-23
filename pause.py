# pause.py - CORREGIDO
import pygame
import sys
from translations import get_text

# Definición de Colores
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

# Constantes del Menú
TEXT_COLOR = BLANCO
SELECT_COLOR = ROJO
# Nueva lista de opciones (se traducirá dentro de la función)
OPCIONES_KEYS = ["Reanudar", "Volumen", "Reiniciar", "Salir"]

def mostrar_menu_pausa(screen, alto, ancho, idioma="Español"):
    """
    Muestra el menú de pausa sobre la pantalla actual.
    Parámetros:
        screen: superficie de pygame donde se dibuja.
        alto: alto de la ventana (int).
        ancho: ancho de la ventana (int).
        idioma: idioma actual del juego ("Español" o "Inglés").
    Devuelve:
        "reanudar", "reiniciar", "salir"
    """
    # Traducir opciones según el idioma
    OPCIONES = [get_text(key, idioma) for key in OPCIONES_KEYS]
    # 1. OBTENER VOLUMEN INICIAL (0-100)
    try:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            volumen_actual = round(pygame.mixer.music.get_volume() * 100)
        else:
            volumen_actual = 30
    except pygame.error:
        volumen_actual = 30

    volumen_actual = max(0, min(100, volumen_actual))

    menu_font = pygame.font.Font(None, 74)

    # Crear overlay y panel centrado para un look más estético
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    fondo_nivel = screen.copy()

    titulo_texto = menu_font.render(get_text("MENÚ DE PAUSA", idioma), True, BLANCO)
    titulo_shadow = menu_font.render(get_text("MENÚ DE PAUSA", idioma), True, (20, 20, 20))

    panel_w, panel_h = 760, 480
    panel_x = ancho // 2 - panel_w // 2
    panel_y = alto // 2 - panel_h // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    seleccion_idx = 0

    # Precompute spacing
    option_start_y = panel_y + 140
    option_spacing = 72

    # Bucle del Menú de Pausa
    while True:
        # Redibujar fondo con overlay
        screen.blit(fondo_nivel, (0, 0))
        screen.blit(overlay, (0, 0))

        # Panel principal (semi-opaque, con borde)
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        # fondo del panel
        pygame.draw.rect(panel_surf, (18, 24, 40, 230), panel_surf.get_rect(), border_radius=24)
        # borde suave
        pygame.draw.rect(panel_surf, (255, 255, 255, 20), panel_surf.get_rect(), width=2, border_radius=24)

        # header band
        header_rect = pygame.Rect(20, 18, panel_w - 40, 88)
        pygame.draw.rect(panel_surf, (148, 0, 211, 220), header_rect, border_radius=18)
        # title shadow + title
        header_center_x = panel_w // 2
        panel_surf.blit(titulo_shadow, (header_center_x - titulo_shadow.get_width() // 2 + 3, 26 + 3))
        panel_surf.blit(titulo_texto, (header_center_x - titulo_texto.get_width() // 2, 26))

        # Draw options inside panel_surf
        for i, opcion in enumerate(OPCIONES):
            y = 140 + i * option_spacing
            is_selected = (i == seleccion_idx)

            # highlight background for selected option
            if is_selected:
                highlight_rect = pygame.Rect(40, y - 8, panel_w - 80, option_spacing - 8)
                pygame.draw.rect(panel_surf, (255, 215, 0, 40), highlight_rect, border_radius=12)

            # small decorative icon circle
            icon_x = 70
            pygame.draw.circle(panel_surf, (255, 230, 80) if is_selected else (200, 200, 200), (icon_x, y + 12), 14)

            # render text
            text_color = (10, 10, 12) if is_selected else (230, 230, 230)
            texto_render = opcion

            # Volume option shows a graphical slider
            if "Volumen" in opcion:
                texto_render = opcion
                text_surf = pygame.font.Font(None, 36).render(texto_render, True, text_color)
                panel_surf.blit(text_surf, (110, y))

                # slider
                slider_x = 320
                slider_w = panel_w - slider_x - 60
                slider_h = 16
                slider_y = y + 18
                # background track
                pygame.draw.rect(panel_surf, (100, 100, 100), (slider_x, slider_y, slider_w, slider_h), border_radius=8)
                # filled
                filled_w = int((volumen_actual / 100.0) * slider_w)
                pygame.draw.rect(panel_surf, (255, 215, 0), (slider_x, slider_y, filled_w, slider_h), border_radius=8)
                # knob
                knob_x = slider_x + filled_w
                pygame.draw.circle(panel_surf, (255, 255, 255), (knob_x, slider_y + slider_h // 2), 10)
            else:
                text_surf = pygame.font.Font(None, 42).render(texto_render, True, text_color)
                panel_surf.blit(text_surf, (110, y))

        # blit panel
        screen.blit(panel_surf, (panel_x, panel_y))

        # footer hint
        hint_font = pygame.font.Font(None, 28)
        hint = hint_font.render(get_text("Usa ↑/↓ para moverte, ENTER para seleccionar", idioma), True, (200, 200, 200))
        screen.blit(hint, (panel_x + (panel_w - hint.get_width()) // 2, panel_y + panel_h - 44))

        pygame.display.flip()

        # MANEJO DE EVENTOS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.KEYDOWN:
                # navegación
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    seleccion_idx = (seleccion_idx + 1) % len(OPCIONES)
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    seleccion_idx = (seleccion_idx - 1) % len(OPCIONES)

                # control de volumen cuando la opción volumen está seleccionada
                elif "Volumen" in OPCIONES[seleccion_idx]:
                    volumen_modificado = False
                    if evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                        volumen_actual = max(0, volumen_actual - 5)
                        volumen_modificado = True
                    elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                        volumen_actual = min(100, volumen_actual + 5)
                        volumen_modificado = True
                    if volumen_modificado:
                        try:
                            pygame.mixer.music.set_volume(volumen_actual / 100)
                        except pygame.error:
                            pass

                elif evento.key == pygame.K_RETURN:
                    opcion_seleccionada = OPCIONES[seleccion_idx].lower()
                    if "reanudar" in opcion_seleccionada:
                        return "reanudar"
                    elif "reiniciar" in opcion_seleccionada:
                        return "reiniciar"
                    elif "salir" in opcion_seleccionada:
                        return "salir"

                elif evento.key == pygame.K_ESCAPE or evento.key == pygame.K_r:
                    return "reanudar"
                elif evento.key == pygame.K_e:
                    return "reiniciar"