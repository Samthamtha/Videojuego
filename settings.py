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

# ==================== VARIABLES GLOBALES DE CONFIGURACIÓN ====================
idioma = "Español"  # Valores: "Español" o "Inglés" (por implementar)
volumen_musica = 0.6  # Rango: 0.0 a 1.0
volumen_efectos = 1.0  # Rango: 0.0 a 1.0
glitch_activado = True  # True = Glitch ON, False = Glitch OFF

# Colores
COLOR_TEXT_NORMAL = (255, 255, 255)  # Blanco
COLOR_TEXT_HIGHLIGHT = (255, 255, 0)  # Amarillo
COLOR_TEXT_DARK = (0, 0, 0)  # Negro
COLOR_BUTTON_BASE = (130, 200, 70)  # Verde lima
COLOR_BUTTON_HIGHLIGHT = (160, 240, 100)  # Verde lima claro
COLOR_PANEL = (40, 40, 40)  # Gris oscuro para paneles

# ==================== FUNCIONES AUXILIARES ====================

def draw_button(screen, rect, text, is_selected, font):
    """Dibuja un botón estilo menu con borde blanco si está seleccionado."""
    color = COLOR_BUTTON_HIGHLIGHT if is_selected else COLOR_BUTTON_BASE
    
    # Fondo del botón
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    # Borde (blanco si seleccionado, negro si no)
    border_color = COLOR_TEXT_NORMAL if is_selected else COLOR_TEXT_DARK
    border_width = 4 if is_selected else 3
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
    
    # Texto centrado
    text_surface = font.render(text, True, COLOR_TEXT_DARK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_slider(screen, rect, value, label, is_selected, font):
    """Dibuja un control deslizante para volumen con flechas << valor >>"""
    color = COLOR_BUTTON_HIGHLIGHT if is_selected else COLOR_BUTTON_BASE
    
    # Fondo
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    # Borde
    border_color = COLOR_TEXT_NORMAL if is_selected else COLOR_TEXT_DARK
    border_width = 4 if is_selected else 3
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
    
    # Texto con flechas
    percentage = int(value * 100)
    text = f"<< {label}: {percentage}% >>"
    text_surface = font.render(text, True, COLOR_TEXT_DARK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_toggle(screen, rect, value, label, is_selected, font):
    """Dibuja un botón de activar/desactivar (ON/OFF)."""
    color = COLOR_BUTTON_HIGHLIGHT if is_selected else COLOR_BUTTON_BASE
    
    # Fondo
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    # Borde
    border_color = COLOR_TEXT_NORMAL if is_selected else COLOR_TEXT_DARK
    border_width = 4 if is_selected else 3
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
    
    # Texto
    estado = "ON" if value else "OFF"
    text = f"{label}: {estado}"
    text_surface = font.render(text, True, COLOR_TEXT_DARK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_option_selector(screen, rect, options, current_index, is_selected, font):
    """Dibuja un selector de opciones con flechas << opción >>"""
    color = COLOR_BUTTON_HIGHLIGHT if is_selected else COLOR_BUTTON_BASE
    
    # Fondo
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    # Borde
    border_color = COLOR_TEXT_NORMAL if is_selected else COLOR_TEXT_DARK
    border_width = 4 if is_selected else 3
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
    
    # Texto con flechas
    text = f"<< {options[current_index]} >>"
    text_surface = font.render(text, True, COLOR_TEXT_DARK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# ==================== MENÚ DE CONFIGURACIÓN ====================

def config_menu(idioma, dificultad, screen):
    """Muestra el menú de configuración con todas las opciones."""
    global volumen_musica, volumen_efectos, glitch_activado
    
    # Cargar sonidos de botones
    try:
        sonido_seleccion = pygame.mixer.Sound("sonido/boton_selec.mp3")
        sonido_ejecucion = pygame.mixer.Sound("sonido/boton_ejec.mp3")
        sonido_seleccion.set_volume(volumen_efectos)
        sonido_ejecucion.set_volume(volumen_efectos)
    except pygame.error as e:
        print(f"Error al cargar sonidos: {e}")
        sonido_seleccion = None
        sonido_ejecucion = None
    
    # Inicializar fuentes
    if not pygame.font.get_init():
        pygame.font.init()
    
    try:
        font_title = pygame.font.Font("font/pixel_font.ttf", 64)
        font_option = pygame.font.Font("font/pixel_font.ttf", 32)
    except:
        font_title = pygame.font.SysFont("Arial", 50, bold=True)
        font_option = pygame.font.SysFont("Arial", 28, bold=True)
    
    # Cargar fondo
    try:
        fondo = pygame.image.load("img/pibble_fondo3.png").convert()
        fondo = pygame.transform.scale(fondo, screen.get_size())
    except pygame.error as e:
        print(f"Error al cargar fondo: {e}")
        fondo = pygame.Surface(screen.get_size())
        fondo.fill((20, 20, 50))
    
    # Overlay semi-transparente
    overlay = pygame.Surface(screen.get_size()).convert_alpha()
    overlay.fill((0, 0, 0))
    overlay.set_alpha(100)
    
    clock = pygame.time.Clock()
    
    # Opciones del menú (índices)
    # 0: Idioma, 1: Volumen Música, 2: Volumen Efectos, 3: Glitch, 4: Volver
    selected_option = 0
    num_options = 5
    
    # Valores de idioma
    idiomas = ["Español", "Inglés"]
    idioma_index = idiomas.index(idioma)
    
    # Dimensiones
    screen_width, screen_height = screen.get_size()
    BUTTON_WIDTH = 600
    BUTTON_HEIGHT = 70
    BUTTON_SPACING = 20
    
    # Posiciones
    title_y = 50
    start_y = 200
    
    # Crear rectángulos
    rects = []
    for i in range(num_options):
        y = start_y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
        rect = pygame.Rect(
            screen_width // 2 - BUTTON_WIDTH // 2,
            y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        rects.append(rect)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                # Navegación vertical
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_option = (selected_option - 1) % num_options
                    if sonido_seleccion:
                        sonido_seleccion.play()
                
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_option = (selected_option + 1) % num_options
                    if sonido_seleccion:
                        sonido_seleccion.play()
                
                # Navegación horizontal (cambiar valores)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if selected_option == 0:  # Idioma
                        idioma_index = (idioma_index - 1) % len(idiomas)
                        idioma = idiomas[idioma_index]
                    
                    elif selected_option == 1:  # Volumen Música
                        volumen_musica = max(0.0, volumen_musica - 0.1)
                        pygame.mixer.music.set_volume(volumen_musica)
                    
                    elif selected_option == 2:  # Volumen Efectos
                        volumen_efectos = max(0.0, volumen_efectos - 0.1)
                        if sonido_seleccion:
                            sonido_seleccion.set_volume(volumen_efectos)
                        if sonido_ejecucion:
                            sonido_ejecucion.set_volume(volumen_efectos)
                    
                    elif selected_option == 3:  # Glitch
                        glitch_activado = not glitch_activado
                    
                    if sonido_seleccion:
                        sonido_seleccion.play()
                
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if selected_option == 0:  # Idioma
                        idioma_index = (idioma_index + 1) % len(idiomas)
                        idioma = idiomas[idioma_index]
                    
                    elif selected_option == 1:  # Volumen Música
                        volumen_musica = min(1.0, volumen_musica + 0.1)
                        pygame.mixer.music.set_volume(volumen_musica)
                    
                    elif selected_option == 2:  # Volumen Efectos
                        volumen_efectos = min(1.0, volumen_efectos + 0.1)
                        if sonido_seleccion:
                            sonido_seleccion.set_volume(volumen_efectos)
                        if sonido_ejecucion:
                            sonido_ejecucion.set_volume(volumen_efectos)
                    
                    elif selected_option == 3:  # Glitch
                        glitch_activado = not glitch_activado
                    
                    if sonido_seleccion:
                        sonido_seleccion.play()
                
                # Confirmar/Volver
                elif event.key == pygame.K_RETURN:
                    if selected_option == 4:  # Volver
                        if sonido_ejecucion:
                            sonido_ejecucion.play()
                        running = False
                    else:
                        if sonido_ejecucion:
                            sonido_ejecucion.play()
        
        # ==================== DIBUJO ====================
        
        # Fondo
        screen.blit(fondo, (0, 0))
        screen.blit(overlay, (0, 0))
        
        # Título
        title_text = "CONFIGURACIÓN"
        title_surface = font_title.render(title_text, True, COLOR_TEXT_HIGHLIGHT)
        title_rect = title_surface.get_rect(centerx=screen_width // 2, top=title_y)
        screen.blit(title_surface, title_rect)
        
        # Opción 0: Idioma
        draw_option_selector(screen, rects[0], idiomas, idioma_index, 
                           selected_option == 0, font_option)
        
        # Opción 1: Volumen Música
        draw_slider(screen, rects[1], volumen_musica, "MÚSICA", 
                   selected_option == 1, font_option)
        
        # Opción 2: Volumen Efectos
        draw_slider(screen, rects[2], volumen_efectos, "EFECTOS", 
                   selected_option == 2, font_option)
        
        # Opción 3: Glitch ON/OFF
        draw_toggle(screen, rects[3], glitch_activado, "GLITCH", 
                   selected_option == 3, font_option)
        
        # Opción 4: Volver
        draw_button(screen, rects[4], "VOLVER", selected_option == 4, font_option)
        
        pygame.display.flip()
        clock.tick(60)
    font = pygame.font.SysFont(None, 40)
    options = ["Idioma", "Dificultad", "Volver"]
    selected_option = 0
    clock = pygame.time.Clock()


    pygame.display.flip()
    clock.tick(60)
