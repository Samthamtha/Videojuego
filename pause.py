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

    # Crear la superficie semitransparente (overlay)
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))

    # Capturar la pantalla anterior
    fondo_nivel = screen.copy()

    # Título
    titulo_texto = menu_font.render(get_text("MENÚ DE PAUSA", idioma), True, BLANCO)

    menu_x_centro = ancho // 2
    menu_y_inicio = alto // 3

    seleccion_idx = 0

    # Bucle del Menú de Pausa
    while True:

        # Redibujar la escena de fondo y el overlay
        screen.blit(fondo_nivel, (0, 0))
        screen.blit(s, (0, 0))

        # Mostrar título Centrado
        screen.blit(titulo_texto, (menu_x_centro - titulo_texto.get_width() // 2, menu_y_inicio - 80))

        # ----------------------------------------------------------------------
        # DIBUJO DE OPCIONES Y VOLUMEN
        # ----------------------------------------------------------------------
        for i, opcion in enumerate(OPCIONES):
            color = SELECT_COLOR if i == seleccion_idx else TEXT_COLOR

            texto_renderizar = opcion

            # Dibujar el indicador de Volumen si es la opción actual
            if "Volumen" in opcion:
                barra_llena = int(volumen_actual / 10)
                barra_vacia = 10 - barra_llena

                barra_str = f"[{'|' * barra_llena}{'.' * barra_vacia}] {volumen_actual}%"
                texto_renderizar = f"{opcion}: {barra_str}"

            texto = menu_font.render(texto_renderizar, True, color)

            # Dibujar Opciones Centradas
            screen.blit(texto, (menu_x_centro - texto.get_width() // 2, menu_y_inicio + i * 70))

        pygame.display.flip()

        # ----------------------------------------------------------------------
        # MANEJO DE EVENTOS
        # ----------------------------------------------------------------------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.KEYDOWN:

                # *** NAVEGACIÓN (UP/DOWN/W/S) ***
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    seleccion_idx = (seleccion_idx + 1) % len(OPCIONES)
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    seleccion_idx = (seleccion_idx - 1) % len(OPCIONES)

                # *** CONTROL DE VOLUMEN (Si la opción "Volumen" está seleccionada) ***
                elif "Volumen" in OPCIONES[seleccion_idx]:
                    volumen_modificado = False

                    if evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                        # Bajar volumen 5%
                        volumen_actual = max(0, volumen_actual - 5)
                        volumen_modificado = True

                    elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                        # Subir volumen 5%
                        volumen_actual = min(100, volumen_actual + 5)
                        volumen_modificado = True

                    if volumen_modificado:
                        # Aplicar el nuevo volumen a Pygame inmediatamente
                        try:
                            pygame.mixer.music.set_volume(volumen_actual / 100)
                        except pygame.error:
                            pass

                # *** SELECCIÓN DE OPCIÓN (ENTER) ***
                elif evento.key == pygame.K_RETURN:
                    opcion_seleccionada = OPCIONES[seleccion_idx].lower()

                    if "reanudar" in opcion_seleccionada:
                        return "reanudar"
                    elif "reiniciar" in opcion_seleccionada:
                        return "reiniciar"
                    # CLAVE: Devolvemos "salir_menu" para que no haya ambigüedad con otras cadenas.
                    elif "salir" in opcion_seleccionada:
                        return "salir"

                # *** SALIR RÁPIDO (ESCAPE/R/E) ***
                elif evento.key == pygame.K_ESCAPE or evento.key == pygame.K_r:
                    return "reanudar"
                elif evento.key == pygame.K_e:
                    return "reiniciar"