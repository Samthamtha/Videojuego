import pygame
import sys
from translations import get_text

# --- INICIALIZACIÓN DE FUENTES (CORRECCIÓN DE ERROR) ---
# Se verifica si el módulo de fuentes ha sido inicializado.
if not pygame.font.get_init():
    pygame.font.init() 

# --- CONFIGURACIÓN DE FUENTES Y COLORES ---
# Intenta usar una fuente pixelada si está disponible para mantener el estilo
try:
    # Nota: si usas una fuente custom, asegúrate de que la ruta sea correcta
    FONT_PATH = "font/pixel_font.ttf" 
    FONT_TITLE = pygame.font.Font(FONT_PATH, 64)
    FONT_ETAPA = pygame.font.Font(FONT_PATH, 30)
    FONT_BUTTON = pygame.font.Font(FONT_PATH, 36)
    FONT_DIFF = pygame.font.Font(FONT_PATH, 28)
except:
    # Fuentes por defecto si no se encuentran las custom
    FONT_TITLE = pygame.font.SysFont("Arial", 50, bold=True)
    FONT_ETAPA = pygame.font.SysFont("Arial", 25, bold=True)
    FONT_BUTTON = pygame.font.SysFont("Arial", 30, bold=True)
    FONT_DIFF = pygame.font.SysFont("Arial", 24, bold=True)


# --- COLORES ---
COLOR_BACKGROUND_OVERLAY = (0, 0, 0, 180)  # Negro semi-transparente para contraste
COLOR_TEXT_NORMAL = (255, 255, 255)        # Blanco
COLOR_TEXT_HIGHLIGHT = (255, 255, 0)       # Amarillo brillante
COLOR_TEXT_DARK = (0, 0, 0)                # Negro para texto en botones claros
COLOR_BUTTON_BASE = (130, 200, 70)         # Verde lima base (Botones JUGAR/VOLVER)
COLOR_BUTTON_HIGHLIGHT = (160, 240, 100)   # Verde lima claro (Hover/Selección)
COLOR_PANEL_INFO = (40, 40, 40)            # Fondo de paneles de información
COLOR_CUADRO_SELECCIONADO = (255, 170, 0)  # Naranja/Amarillo para selección de etapa


# --- DATOS DE ETAPAS ---
# IMPORTANTE: Se ha añadido "return_key" para que el bucle principal sepa qué función llamar.
# Se añadió "preview_image" para la imagen de vista previa
ETAPAS = [
    {"short": "ETAPA 1", "long": "LIMPIEZA DEL RÍO", "return_key": "level1", "preview_image": "img/rio.png"},
    {"short": "ETAPA 2", "long": "REPARACIÓN DE OBJETOS", "return_key": "level2", "preview_image": None},
    {"short": "ETAPA 3", "long": "FÁBRICA DE REVALORIZACIÓN", "return_key": "level3", "preview_image": None},
    {"short": "ETAPA FINAL", "long": "BATALLA FINAL", "return_key": "level_final", "preview_image": None},
]
dificultad = ["Principiante", "Intermedio", "Profesional"]
BUTTON_H = 55 # Altura estándar de botones largos
BUTTON_SPACING = 20 # Espacio vertical entre botones

# --- FUNCIONES AUXILIARES DE DIBUJO ---

def draw_button_long(screen, rect, text, is_active, base_color=COLOR_BUTTON_BASE):
    """Dibuja un botón o panel largo con estilo 3D y texto centrado."""
    
    # Color de fondo (resaltado si está activo)
    color = COLOR_BUTTON_HIGHLIGHT if is_active else base_color
    
    # 1. Dibujar el cuerpo principal
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    # 2. Dibujar borde blanco grueso si está activo (NUEVO)
    if is_active:
        pygame.draw.rect(screen, COLOR_TEXT_NORMAL, rect, 4, border_radius=8)
    else:
        # Borde sutil normal
        pygame.draw.rect(screen, COLOR_TEXT_DARK, rect, 3, border_radius=8)
    
    # 3. Dibujar texto
    text_surface = FONT_BUTTON.render(text, True, COLOR_TEXT_DARK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_stage_quad(screen, rect, text_short, is_selected):
    """Dibuja los cuadros seleccionables de la parte superior (Etapa 1, 2...)."""
    
    # 1. Fondo
    color_fondo = COLOR_CUADRO_SELECCIONADO if is_selected else COLOR_PANEL_INFO
    pygame.draw.rect(screen, color_fondo, rect, border_radius=5)

    # 2. Borde (blanco si está seleccionado)
    borde_color = COLOR_TEXT_NORMAL if is_selected else COLOR_TEXT_DARK
    pygame.draw.rect(screen, borde_color, rect, 3, border_radius=5)
    
    # 3. Dibujar texto corto
    text_color = COLOR_TEXT_DARK if is_selected else COLOR_TEXT_NORMAL
    text_surface = FONT_ETAPA.render(text_short, True, text_color)
    text_rect = text_surface.get_rect(centerx=rect.centerx, centery=rect.centery)
    screen.blit(text_surface, text_rect)

def draw_preview_panel(screen, rect, stage_info, preview_image_path, idioma="Español"):
    """Dibuja el cuadro grande de vista previa con imagen si está disponible."""
    
    # 1. Fondo (simulando un recuadro de vista del nivel)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill((0, 0, 0, 180)) # Negro semi-transparente
    screen.blit(surface, rect.topleft)
    
    # 2. Borde Blanco
    pygame.draw.rect(screen, COLOR_TEXT_NORMAL, rect, 3)

    # 3. Intentar cargar y mostrar la imagen si existe
    if preview_image_path:
        try:
            preview_img = pygame.image.load(preview_image_path).convert()
            # Escalar la imagen para que quepa en el rectángulo con un margen
            img_rect = preview_img.get_rect()
            # Calcular escala manteniendo aspecto
            scale_w = (rect.width - 20) / img_rect.width
            scale_h = (rect.height - 60) / img_rect.height
            scale = min(scale_w, scale_h)
            
            new_width = int(img_rect.width * scale)
            new_height = int(img_rect.height * scale)
            preview_img = pygame.transform.scale(preview_img, (new_width, new_height))
            
            # Centrar la imagen en el rectángulo
            img_x = rect.x + (rect.width - new_width) // 2
            img_y = rect.y + 40  # Dejar espacio arriba para el texto
            screen.blit(preview_img, (img_x, img_y))
            
            # Texto arriba de la imagen
            text_line1 = FONT_ETAPA.render(get_text("VISTA PREVIA:", idioma), True, COLOR_TEXT_NORMAL)
            screen.blit(text_line1, (rect.x + 15, rect.y + 10))
            
        except pygame.error as e:
            print(f"Error al cargar imagen de vista previa '{preview_image_path}': {e}")
            # Si falla, mostrar texto como antes
            draw_preview_text_fallback(screen, rect, stage_info, idioma)
    else:
        # Si no hay imagen, mostrar texto
        draw_preview_text_fallback(screen, rect, stage_info, idioma)

def draw_preview_text_fallback(screen, rect, stage_info, idioma="Español"):
    """Dibuja texto de vista previa cuando no hay imagen."""
    text_line1 = FONT_ETAPA.render(get_text("VISTA PREVIA:", idioma), True, COLOR_TEXT_NORMAL)
    screen.blit(text_line1, (rect.x + 15, rect.y + 15))
    
    # Ajustar el texto largo para que quepa bien en el panel de previsualización
    text_line2 = FONT_BUTTON.render(stage_info, True, COLOR_TEXT_HIGHLIGHT)
    text_line2_rect = text_line2.get_rect(center=(rect.centerx, rect.centery + 20))
    screen.blit(text_line2, text_line2_rect)


def draw_difficulty_control(screen, rect, difficulty, is_active):
    """Dibuja la barra de selección de dificultad con flechas simuladas."""
    
    color_fondo = COLOR_BUTTON_HIGHLIGHT if is_active else COLOR_BUTTON_BASE
    
    # 1. Fondo
    pygame.draw.rect(screen, color_fondo, rect, border_radius=8)
    
    # 2. Borde blanco grueso si está activo (NUEVO)
    if is_active:
        pygame.draw.rect(screen, COLOR_TEXT_NORMAL, rect, 4, border_radius=8)
    else:
        pygame.draw.rect(screen, COLOR_TEXT_DARK, rect, 3, border_radius=8)
    
    # 3. Texto de dificultad
    texto = f"<< {difficulty} >>"
    text_surface = FONT_DIFF.render(texto, True, COLOR_TEXT_DARK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


# La función debe recibir dificultad e idioma para mantener la consistencia con main.py
def run_level_select(screen, dificultad_actual, idioma): 
    # La inicialización de fuentes ya se hizo arriba.
    
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()
    
    # --- Cargar imagen de fondo y Overlay ---
    background_image = None
    try:
        # Cargar la imagen de fondo de la nutria y escalarla al tamaño de la pantalla
        background_image = pygame.image.load("img/pibble_fondo2.png").convert()
        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    except pygame.error as e:
        # Si la imagen no carga, solo imprimimos el error y usamos el fondo oscuro
        print(f"Error al cargar la imagen de fondo 'img/pibble_fondo2.png': {e}")
        
    # Overlay semi-transparente MUY LIGERO para dar contraste (Negro al 15%)
    overlay = pygame.Surface((screen_width, screen_height)).convert_alpha()
    overlay.fill(COLOR_TEXT_DARK) 
    overlay.set_alpha(40)  # Reducido de 180 a 40 para ver mejor el fondo 

    # --- ESTADO DE NAVEGACIÓN ---
    # Manejo de la dificultad inicial
    try:
        selected_difficulty_index = dificultad.index(dificultad_actual)
    except ValueError:
        selected_difficulty_index = 1 
    
    selected_etapa_index = 0
    # 0: JUGAR, 1: DIFICULTAD, 2: VOLVER
    selected_main_button = 0 
    
    
    # --- POSICIONAMIENTO DE LA UI (Calculado dinámicamente) ---
    
    # Título "SELECCIONA LA ETAPA"
    title_text = get_text("SELECCIONA LA ETAPA", idioma)
    title_surface = FONT_TITLE.render(title_text, True, COLOR_TEXT_HIGHLIGHT)
    title_rect = title_surface.get_rect(centerx=screen_width // 2, top=40)

    # Cuadros de etapa (arriba) - MÁS GRANDES
    ETAPA_W, ETAPA_H = 200, 150  # Aumentado de 150x120 a 200x150
    ETAPA_SPACING = 35  # Aumentado de 30 a 35
    total_etapa_width = len(ETAPAS) * ETAPA_W + (len(ETAPAS) - 1) * ETAPA_SPACING
    
    # Ajustamos la posición X para que todo el contenido esté centrado
    start_content_x = screen_width // 2 - total_etapa_width // 2 
    
    etapa_rects = []
    for i in range(len(ETAPAS)):
        rect = pygame.Rect(start_content_x + i * (ETAPA_W + ETAPA_SPACING), title_rect.bottom + 30, ETAPA_W, ETAPA_H)
        etapa_rects.append(rect)
    
    # Área principal de contenido (preview y opciones)
    CONTENT_Y = etapa_rects[0].bottom + 40
    
    # Vista Previa (Izquierda) - MÁS GRANDE
    PREVIEW_W, PREVIEW_H = 450, 320  # Aumentado de 350x250 a 450x320
    preview_rect = pygame.Rect(start_content_x, CONTENT_Y, PREVIEW_W, PREVIEW_H)
    
    # Área de Opciones (Derecha)
    OPTIONS_X = preview_rect.right + 30
    # Ajuste del ancho para que el contenido sea simétrico con el inicio del contenido
    OPTIONS_W = (screen_width - OPTIONS_X) - (start_content_x - 10) 
    
    # Panel de Información (Nombre largo de la etapa) - MÁS ALTO
    info_panel_h = 60  # Aumentado de 45 a 60
    info_panel_y = CONTENT_Y
    info_panel_rect = pygame.Rect(OPTIONS_X, info_panel_y, OPTIONS_W, info_panel_h)
    
    # Botón JUGAR - MÁS ALTO
    JUGAR_Y = info_panel_rect.bottom + BUTTON_H // 2 
    jugar_rect = pygame.Rect(OPTIONS_X, JUGAR_Y, OPTIONS_W, BUTTON_H + 10)  # +10 más alto
    
    # Botón DIFICULTAD - MÁS ALTO
    DIFICULTAD_Y = jugar_rect.bottom + BUTTON_SPACING
    dificultad_rect = pygame.Rect(OPTIONS_X, DIFICULTAD_Y, OPTIONS_W, BUTTON_H + 10)  # +10 más alto
    
    # Botón VOLVER - MÁS ALTO
    VOLVER_Y = dificultad_rect.bottom + BUTTON_SPACING
    volver_rect = pygame.Rect(OPTIONS_X, VOLVER_Y, OPTIONS_W, BUTTON_H + 10)  # +10 más alto
    
    # Lista de rectángulos de botones principales para la navegación vertical
    main_button_rects = [jugar_rect, dificultad_rect, volver_rect]

    # -----------------------------------------------------------
    # --- BUCLE PRINCIPAL ---
    # -----------------------------------------------------------
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego", dificultad[selected_difficulty_index], idioma
            
            elif event.type == pygame.KEYDOWN:
                
                # --- NAVEGACIÓN VERTICAL (UP/DOWN & W/S) ---
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_main_button = (selected_main_button - 1) % len(main_button_rects)
                
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_main_button = (selected_main_button + 1) % len(main_button_rects)
                
                # --- NAVEGACIÓN HORIZONTAL (LEFT/RIGHT & A/D) ---
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if selected_main_button == 1: # Si estamos en Dificultad
                        # Cambia dificultad: Mueve hacia la izquierda (dificultad más fácil)
                        selected_difficulty_index = (selected_difficulty_index - 1) % len(dificultad)
                    else: # Si estamos en JUGAR o VOLVER, cambia la etapa
                        # Cambia etapa: Mueve hacia la izquierda
                        selected_etapa_index = (selected_etapa_index - 1) % len(ETAPAS)
                
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if selected_main_button == 1: # Si estamos en Dificultad
                        # Cambia dificultad: Mueve hacia la derecha (dificultad más avanzada)
                        selected_difficulty_index = (selected_difficulty_index + 1) % len(dificultad)
                    else: # Si estamos en JUGAR o VOLVER, cambia la etapa
                        # Cambia etapa: Mueve hacia la derecha
                        selected_etapa_index = (selected_etapa_index + 1) % len(ETAPAS)

                # --- SELECCIÓN (ENTER) ---
                elif event.key == pygame.K_RETURN:
                    dificultad_salida = dificultad[selected_difficulty_index]
                    
                    if selected_main_button == 0: # JUGAR
                        # Asegurar que se detenga la música antes de iniciar el nivel
                        if pygame.mixer.get_init():
                             pygame.mixer.music.stop()
                        
                        # AHORA RETORNAMOS LA CLAVE DE RETORNO para el nivel
                        return ETAPAS[selected_etapa_index]["return_key"], dificultad_salida, idioma
                    
                    elif selected_main_button == 2: # VOLVER
                        return "menu", dificultad_salida, idioma
        
        # --- LÓGICA DE DIBUJO ---
        
        # 1. Dibujar fondo (imagen o fallback) y Overlay
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((10, 10, 30)) # Azul oscuro
        screen.blit(overlay, (0, 0))

        # 2. Dibujar TÍTULO
        screen.blit(title_surface, title_rect)
        
        # 3. Dibujar CUADROS DE ETAPA (ARRIBA)
        etapa_actual = ETAPAS[selected_etapa_index]
        for i, etapa_data in enumerate(ETAPAS):
            is_selected = (i == selected_etapa_index)
            # Traducir el nombre corto de la etapa
            etapa_short_traducido = get_text(etapa_data["short"], idioma)
            draw_stage_quad(screen, etapa_rects[i], etapa_short_traducido, is_selected)
        
        # 4. Dibujar VISTA PREVIA (IZQUIERDA) - Ahora con imagen
        draw_preview_panel(screen, preview_rect, etapa_actual["long"], etapa_actual.get("preview_image"), idioma)

        # 5. Dibujar PANEL DE INFORMACIÓN (Solo el nombre del nivel, sin "ETAPA X:")
        etapa_nombre_traducido = get_text(etapa_actual['long'], idioma)
        draw_button_long(screen, info_panel_rect, 
                         etapa_nombre_traducido,  # CAMBIADO: Solo muestra el nombre traducido
                         False, 
                         (180, 180, 180)) # Color gris claro para panel informativo

        # 6. Dibujar Botones JUGAR, DIFICULTAD, VOLVER
        
        # Botón JUGAR
        draw_button_long(screen, jugar_rect, get_text("JUGAR", idioma), selected_main_button == 0)
        
        # Botón DIFICULTAD
        draw_difficulty_control(screen, dificultad_rect, 
                                dificultad[selected_difficulty_index], 
                                selected_main_button == 1)
        
        # Botón VOLVER
        draw_button_long(screen, volver_rect, get_text("VOLVER", idioma), selected_main_button == 2)

        pygame.display.flip()
        clock.tick(60)
    
    # Fallback
    return "menu", dificultad[selected_difficulty_index], idioma