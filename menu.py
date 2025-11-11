# menu.py
import pygame
import sys
import os
import math
from settings import config_menu, idioma, dificultad
from credits import show_credits

pygame.mixer.init()
pygame.mixer.music.load('sonido/inicio_musica.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# 🔊 Cargar sonidos de botones
try:
    sonido_seleccion = pygame.mixer.Sound("sonido/boton_selec.mp3")
    sonido_ejecucion = pygame.mixer.Sound("sonido/boton_ejec.mp3")
except pygame.error as e:
    print(f"Error al cargar sonidos de botones: {e}")
    sonido_seleccion = None
    sonido_ejecucion = None

# pegar el menú al borde
LEFT_ALIGN_X = 50
OVERLAY_COLOR = (0, 0, 0)
OVERLAY_ALPHA = 100
BREATH_AMPLITUDE = 5
BREATH_SPEED = 0.005
LOGO_BREATH_SPEED_MULTIPLIER = 1.0


def cargar_frames_desde_carpeta(carpeta):
    frames = []
    if not os.path.exists(carpeta):
        print(f" Carpeta no encontrada: {carpeta}")
        return frames

    for archivo in sorted(os.listdir(carpeta)):
        if archivo.endswith((".png", ".jpg")):
            ruta = os.path.join(carpeta, archivo)
            imagen = pygame.image.load(ruta).convert_alpha()
            frames.append(imagen)
    return frames


def run_menu(screen, dificultad, idioma):
    if not pygame.font.get_init():
        pygame.font.init()

    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()
    main_menu_options = ["Iniciar Juego", "Configuración", "Créditos", "Salir"]
    selected_option = 0

    BUTTON_WIDTH = 500
    BUTTON_HEIGHT = 60

    BUTTON_FILES = {
        "Iniciar Juego": "img/boton.png",
        "Configuración": "img/boton2.png",
        "Créditos": "img/boton4.png",
        "Salir": "img/boton3.png"
    }

    BUTTON_SELECTED_FILES = {
        "Iniciar Juego": "img/boton_selected.png",
        "Configuración": "img/boton2_selected.png",
        "Créditos": "img/boton4_selected.png",
        "Salir": "img/boton3_selected.png"
    }

    button_images = {}
    button_selected_images = {}

    for text, path in BUTTON_FILES.items():
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (BUTTON_WIDTH, BUTTON_HEIGHT))
            button_images[text] = img
        except pygame.error as e:
            print(f"Error al cargar la imagen NORMAL del botón '{text}' en {path}: {e}")
            button_images[text] = None

    for text, path in BUTTON_SELECTED_FILES.items():
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (BUTTON_WIDTH, BUTTON_HEIGHT))
            button_selected_images[text] = img
        except pygame.error as e:
            print(f"Advertencia: No se pudo cargar la imagen SELECCIONADA del botón '{text}' en {path}: {e}")
            button_selected_images[text] = button_images.get(text)

    fondo = pygame.image.load("img/fondoinicio.png").convert()
    fondo = pygame.transform.scale(fondo, (screen.get_width(), screen.get_height()))

    titulo_img = pygame.image.load("img/logo.png").convert_alpha()
    titulo_img = pygame.transform.scale(titulo_img, (400, 200))
    rect_titulo_original = titulo_img.get_rect(topleft=(LEFT_ALIGN_X, 10))

    pibble_cargado = False
    try:
        pibble_img_original = pygame.image.load("img/pibble.png").convert_alpha()
        NEW_HEIGHT = screen.get_height() - 100
        ratio = pibble_img_original.get_width() / pibble_img_original.get_height()
        NEW_WIDTH = int(NEW_HEIGHT * ratio)
        pibble_img_original = pygame.transform.scale(pibble_img_original, (NEW_WIDTH, NEW_HEIGHT))
        pibble_x_original = screen.get_width() - NEW_WIDTH - 50
        pibble_y_original = screen.get_height() // 2 - NEW_HEIGHT // 2
        pibble_rect_original = pibble_img_original.get_rect(topleft=(pibble_x_original, pibble_y_original))
        pibble_cargado = True
    except pygame.error:
        pibble_cargado = False

    overlay = pygame.Surface((screen.get_width(), screen.get_height())).convert_alpha()
    overlay.fill(OVERLAY_COLOR)
    overlay.set_alpha(OVERLAY_ALPHA)

    current_time = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(main_menu_options)
                    if sonido_seleccion:
                        sonido_seleccion.play()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(main_menu_options)
                    if sonido_seleccion:
                        sonido_seleccion.play()
                elif event.key == pygame.K_RETURN:
                    if sonido_ejecucion:
                        sonido_ejecucion.play()
                    opcion = main_menu_options[selected_option]
                    if opcion == "Iniciar Juego":
                        return "jugar", dificultad, idioma
                    elif opcion == "Configuración":
                        config_menu(screen)
                    elif opcion == "Créditos":
                        show_credits(screen)
                    elif opcion == "Salir":
                        return "salir", dificultad, idioma

        current_time += clock.get_time()
        screen.blit(fondo, (0, 0))
        screen.blit(overlay, (0, 0))

        logo_offset = BREATH_AMPLITUDE * math.sin(current_time * BREATH_SPEED * LOGO_BREATH_SPEED_MULTIPLIER)
        rect_titulo_animado = rect_titulo_original.copy()
        rect_titulo_animado.y = rect_titulo_original.y + logo_offset
        screen.blit(titulo_img, rect_titulo_animado)

        if pibble_cargado:
            pibble_offset = BREATH_AMPLITUDE * math.sin(current_time * BREATH_SPEED)
            pibble_rect_animado = pibble_rect_original.copy()
            pibble_rect_animado.y = pibble_rect_original.y + pibble_offset
            screen.blit(pibble_img_original, pibble_rect_animado)

        Y_GAP = 35
        TOTAL_BUTTONS_HEIGHT = (BUTTON_HEIGHT * 4) + (Y_GAP * 3)

        if pibble_cargado:
            OFFSET_DOWN = 50
            BOTONES_Y_INICIO_CENTRO = (pibble_rect_original.centery + OFFSET_DOWN) - TOTAL_BUTTONS_HEIGHT // 2
            MIN_Y_START = rect_titulo_original.bottom + 30
            if BOTONES_Y_INICIO_CENTRO < MIN_Y_START:
                BOTONES_Y_INICIO_CENTRO = MIN_Y_START
        else:
            BOTONES_Y_INICIO_CENTRO = rect_titulo_original.bottom + 80

        def mostrar_boton(frames, texto, y, seleccionado=False, ancho=BUTTON_WIDTH, alto=BUTTON_HEIGHT):
            BUTTON_X = LEFT_ALIGN_X
            img = button_selected_images.get(texto) if seleccionado else button_images.get(texto)
            if img:
                rect = img.get_rect(topleft=(BUTTON_X, y - alto // 2))
                screen.blit(img, rect)
            else:
                color = (200, 0, 0) if texto == main_menu_options[selected_option] else (0, 0, 0)
                text = font.render(texto, True, color)
                rect = text.get_rect(center=(BUTTON_X + ancho // 2, y))
                screen.blit(text, rect)

        Y_1 = BOTONES_Y_INICIO_CENTRO + BUTTON_HEIGHT // 2
        Y_2 = Y_1 + BUTTON_HEIGHT + Y_GAP
        Y_3 = Y_2 + BUTTON_HEIGHT + Y_GAP
        Y_4 = Y_3 + BUTTON_HEIGHT + Y_GAP

        mostrar_boton(None, "Iniciar Juego", Y_1, seleccionado=(selected_option == 0))
        mostrar_boton(None, "Configuración", Y_2, seleccionado=(selected_option == 1))
        mostrar_boton(None, "Créditos", Y_3, seleccionado=(selected_option == 2))
        mostrar_boton(None, "Salir", Y_4, seleccionado=(selected_option == 3))

        pygame.display.flip()
        clock.tick(60)
