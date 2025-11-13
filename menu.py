import pygame
import sys
import os
import math
import random  # Necesario para la aleatoriedad del glitch
from settings import config_menu, idioma, dificultad, glitch_activado, volumen_musica, volumen_efectos
from credits import show_credits
from translations import get_text

# Variables globales para sonidos (se inicializan en run_menu)
sonido_seleccion = None
sonido_ejecucion = None

# NUEVOS ASSETS DE GLITCH
# Inicializar pygame.mixer antes de cargar sonidos
SOUND_HORROR = None
try:
    pygame.mixer.init()
    #  Sonido de Horror (ahora se detiene automáticamente)
    SOUND_HORROR = pygame.mixer.Sound("sonido/inicio_horror.mp3") 
    SOUND_HORROR.set_volume(0.3) 
except (pygame.error, AttributeError) as e:
    print(f"ADVERTENCIA: No se pudo cargar el sonido 'inicio_horror.mp3'. {e}")
    SOUND_HORROR = None 

# Variables de control para el efecto Glitch
GLITCH_DURATION_SHORT_MS = 300 # Duración normal (rápida)
GLITCH_DURATION_LONG_MIN_MS = 2000 # Duración mínima del glitch extendido (2 segundos)
GLITCH_DURATION_LONG_MAX_MS = 4000 # Duración máxima del glitch extendido (4 segundos)
GLITCH_LONG_CHANCE = 15          # 15% de probabilidad de un glitch largo (en lugar del corto)

GLITCH_COOLDOWN_MS = 5000 # El parpadeo no ocurrirá inmediatamente después de uno
GLITCH_MAX_INTERVAL = 8000 # Máximo tiempo para el próximo parpadeo (8 segundos)

glitch_active = False
glitch_end_time = 0
last_glitch_time = 0
# Intervalo inicial aleatorio para que no sea predecible
next_glitch_interval = random.randint(3000, GLITCH_MAX_INTERVAL) 

# esto pega el menú al borde
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

def check_for_glitch():
    """Decide si es momento de iniciar o terminar el efecto de parpadeo."""
    global glitch_active, glitch_end_time, last_glitch_time, next_glitch_interval
    
    # Importar la configuración actual del glitch
    from settings import glitch_activado
    
    # Si el glitch está desactivado en configuración, no hacer nada
    if not glitch_activado:
        glitch_active = False
        return

    current_time = pygame.time.get_ticks()

    if glitch_active:
        # Si está activo, revisa si debe terminar
        if current_time >= glitch_end_time:
            glitch_active = False
            
            #DETENER EL SONIDO INMEDIATAMENTE y RESTAURAR MÚSICA
            if SOUND_HORROR:
                SOUND_HORROR.stop()
            
            #reanudar la música de fondo a volumen normal
            from settings import volumen_musica
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(volumen_musica) 
            
            # Establecer el nuevo intervalo de espera (tiempo de recarga + un tiempo aleatorio)
            next_glitch_interval = GLITCH_COOLDOWN_MS + random.randint(1000, GLITCH_MAX_INTERVAL - GLITCH_COOLDOWN_MS)
            return # Termina el chequeo

    # Si no está activo, revisa si debe empezar
    if (current_time - last_glitch_time) > next_glitch_interval:
        # Probabilidad de iniciar el glitch (e.g., 50% de probabilidad)
        if random.randint(1, 100) > 50:
            glitch_active = True
            last_glitch_time = current_time
            
            #NUEVA LÓGICA DE DURACIÓN: Largo o Corto
            if random.randint(1, 100) <= GLITCH_LONG_CHANCE:
                # Glitch largo
                duration = random.randint(GLITCH_DURATION_LONG_MIN_MS, GLITCH_DURATION_LONG_MAX_MS)
                print(f"--- GLITCH LARGO INICIADO: {duration}ms ---")
            else:
                # Glitch corto (normal)
                duration = GLITCH_DURATION_SHORT_MS
                
            glitch_end_time = current_time + duration
            
            # Reproducir el sonido de horror
            if SOUND_HORROR:
                # Bajar la música de fondo mientras suena el horror
                pygame.mixer.music.set_volume(0.1) 
                # El sonido se reproducirá y se detendrá cuando termine el glitch
                SOUND_HORROR.play()


def run_menu(screen, dificultad, idioma):
    """Función principal del menú con efecto glitch."""
    
    # INICIALIZACIÓN DE VARIABLES Y ASSETS DEL MENÚ
    global glitch_active, sonido_seleccion, sonido_ejecucion
    
    # Inicializar mixer si no está inicializado
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Advertencia: No se pudo inicializar el mezclador de sonido. {e}")
    
    # Cargar sonidos de botones (solo si no están cargados)
    if sonido_seleccion is None or sonido_ejecucion is None:
        try:
            # Importar volumen_efectos dentro de la función para evitar conflictos
            from settings import volumen_efectos
            sonido_seleccion = pygame.mixer.Sound("sonido/boton_selec.mp3")
            sonido_ejecucion = pygame.mixer.Sound("sonido/boton_ejec.mp3")
            sonido_seleccion.set_volume(volumen_efectos)
            sonido_ejecucion.set_volume(volumen_efectos)
        except pygame.error as e:
            print(f"Error al cargar sonidos de botones: {e}")
            sonido_seleccion = None
            sonido_ejecucion = None

    if not pygame.font.get_init():
        pygame.font.init()

    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()
    # Opciones del menú traducidas
    main_menu_options = [
        get_text("Iniciar Juego", idioma),
        get_text("Configuración", idioma),
        get_text("Créditos", idioma),
        get_text("Salir", idioma)
    ]
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

    #CARGA DE FONDOS (NORMAL y GLITCH)
    try:
        fondo_normal = pygame.image.load("img/fondoinicio.png").convert() # Fondo original
        fondo_normal = pygame.transform.scale(fondo_normal, (screen.get_width(), screen.get_height()))
        
        fondo_glitch = pygame.image.load("img/fondo_inicio2.png").convert() # Fondo de glitch
        fondo_glitch = pygame.transform.scale(fondo_glitch, (screen.get_width(), screen.get_height()))
    except pygame.error as e:
        print(f"ERROR al cargar un fondo: {e}")
        fondo_normal = pygame.Surface((screen.get_width(), screen.get_height()))
        fondo_normal.fill((50, 50, 100))
        fondo_glitch = pygame.Surface((screen.get_width(), screen.get_height()))
        fondo_glitch.fill((100, 0, 0))

    titulo_img = pygame.image.load("img/logo.png").convert_alpha()
    titulo_img = pygame.transform.scale(titulo_img, (400, 200))
    rect_titulo_original = titulo_img.get_rect(topleft=(LEFT_ALIGN_X, 10))

    # CARGA DE PERSONAJES (PIBBLE y GLITCH)
    pibble_cargado = False
    try:
        pibble_img_normal = pygame.image.load("img/pibble.png").convert_alpha() # Imagen original (pibble)
        pibble_img_glitch = pygame.image.load("img/bat_cat.png").convert_alpha() # Imagen de glitch (bad_cat)

        NEW_HEIGHT = screen.get_height() - 100
        ratio = pibble_img_normal.get_width() / pibble_img_normal.get_height()
        NEW_WIDTH = int(NEW_HEIGHT * ratio)
        
        # Redimensionar ambas imágenes del personaje al mismo tamaño
        pibble_img_normal = pygame.transform.scale(pibble_img_normal, (NEW_WIDTH, NEW_HEIGHT))
        pibble_img_glitch = pygame.transform.scale(pibble_img_glitch, (NEW_WIDTH, NEW_HEIGHT))
        
        pibble_x_original = screen.get_width() - NEW_WIDTH - 50
        pibble_y_original = screen.get_height() // 2 - NEW_HEIGHT // 2
        pibble_rect_original = pibble_img_normal.get_rect(topleft=(pibble_x_original, pibble_y_original))
        pibble_cargado = True
    except pygame.error as e:
        print(f"ERROR al cargar imágenes de personaje: {e}")
        pibble_cargado = False

    overlay = pygame.Surface((screen.get_width(), screen.get_height())).convert_alpha()
    overlay.fill(OVERLAY_COLOR)
    overlay.set_alpha(OVERLAY_ALPHA)

    current_time = 0

    # BUCLE PRINCIPAL DEL MENÚ
    while True:
        
        # Ejecutar el chequeo de Glitch
        check_for_glitch()

        # Procesar Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Solo permitir interacción si el glitch no está activo
            elif event.type == pygame.KEYDOWN and not glitch_active:
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
                    # Comparar con las claves originales (no traducidas) para la lógica
                    opcion_key = None
                    if opcion == get_text("Iniciar Juego", idioma):
                        opcion_key = "Iniciar Juego"
                    elif opcion == get_text("Configuración", idioma):
                        opcion_key = "Configuración"
                    elif opcion == get_text("Créditos", idioma):
                        opcion_key = "Créditos"
                    elif opcion == get_text("Salir", idioma):
                        opcion_key = "Salir"
                    
                    if opcion_key == "Iniciar Juego":
                        return "jugar", dificultad, idioma
                    elif opcion_key == "Configuración":
                        resultado = config_menu(idioma, dificultad, screen)
                        if resultado:
                            idioma, dificultad = resultado
                            # Actualizar opciones del menú con el nuevo idioma
                            main_menu_options = [
                                get_text("Iniciar Juego", idioma),
                                get_text("Configuración", idioma),
                                get_text("Créditos", idioma),
                                get_text("Salir", idioma)
                            ]
                        # Actualizar volúmenes después de salir de configuración
                        from settings import volumen_musica, volumen_efectos
                        pygame.mixer.music.set_volume(volumen_musica)
                        if sonido_seleccion:
                            sonido_seleccion.set_volume(volumen_efectos)
                        if sonido_ejecucion:
                            sonido_ejecucion.set_volume(volumen_efectos)
                    elif opcion_key == "Créditos":
                        show_credits(screen)
                    elif opcion_key == "Salir":
                        return "salir", dificultad, idioma

        # Lógica de Dibujo
        
        #  Determinar qué fondo usar
        fondo_a_usar = fondo_glitch if glitch_active else fondo_normal
        screen.blit(fondo_a_usar, (0, 0))
        
        #Usar overlay (opcional: cambiar overlay durante glitch)
        if glitch_active:
            overlay_glitch = pygame.Surface((screen.get_width(), screen.get_height())).convert_alpha()
            overlay_glitch.fill((255, 0, 0)) # Rojo durante el glitch
            overlay_glitch.set_alpha(150) # Más opaco
            screen.blit(overlay_glitch, (0, 0))
        else:
            screen.blit(overlay, (0, 0)) # Overlay normal

        current_time += clock.get_time()

        # Dibujar Título (no cambia en el glitch)
        logo_offset = BREATH_AMPLITUDE * math.sin(current_time * BREATH_SPEED * LOGO_BREATH_SPEED_MULTIPLIER)
        rect_titulo_animado = rect_titulo_original.copy()
        rect_titulo_animado.y = rect_titulo_original.y + logo_offset
        screen.blit(titulo_img, rect_titulo_animado)

        #Dibujar Personaje (cambia en el glitch)
        if pibble_cargado:
            personaje_a_usar = pibble_img_glitch if glitch_active else pibble_img_normal
            pibble_offset = BREATH_AMPLITUDE * math.sin(current_time * BREATH_SPEED)
            pibble_rect_animado = pibble_rect_original.copy()
            pibble_rect_animado.y = pibble_rect_original.y + pibble_offset
            screen.blit(personaje_a_usar, pibble_rect_animado)

        # Dibujar Botones (los botones seleccionados cambian de color)
        Y_GAP = 35
        BUTTON_X = LEFT_ALIGN_X
        
        if pibble_cargado:
            TOTAL_BUTTONS_HEIGHT = (BUTTON_HEIGHT * 4) + (Y_GAP * 3)
            OFFSET_DOWN = 50
            BOTONES_Y_INICIO_CENTRO = (pibble_rect_original.centery + OFFSET_DOWN) - TOTAL_BUTTONS_HEIGHT // 2
            MIN_Y_START = rect_titulo_original.bottom + 30
            if BOTONES_Y_INICIO_CENTRO < MIN_Y_START:
                BOTONES_Y_INICIO_CENTRO = MIN_Y_START
        else:
            BOTONES_Y_INICIO_CENTRO = rect_titulo_original.bottom + 80

        def mostrar_boton(frames, texto, y, seleccionado=False, ancho=BUTTON_WIDTH, alto=BUTTON_HEIGHT):
            
            # Si el glitch está activo, todos los botones se ven normales y el texto es rojo
            is_selected_visual = seleccionado and not glitch_active
            
            img = button_selected_images.get(texto) if is_selected_visual else button_images.get(texto)
            
            if img:
                rect = img.get_rect(topleft=(BUTTON_X, y - alto // 2))
                screen.blit(img, rect)
                # La imagen ya debe contener el texto del botón.
            else:
                # Si no hay imagen de botón, dibujar solo el texto como respaldo
                color_texto = (255, 255, 255) # Blanco por defecto
                if glitch_active:
                    color_texto = (255, 0, 0) # Rojo durante el glitch
                elif is_selected_visual:
                    color_texto = (255, 255, 0) # Amarillo si está seleccionado y no hay glitch
                
                text_surface = font.render(texto, True, color_texto)
                text_rect = text_surface.get_rect(center=(BUTTON_X + ancho // 2, y))
                screen.blit(text_surface, text_rect)

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