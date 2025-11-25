# victory_menu.py
import pygame
import sys

# Colores
BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)
COLOR_BORDER = (130, 200, 70)  # Verde lima

def mostrar_menu_victoria(screen, nivel_actual):
    """
    Muestra el menú de victoria después de completar un nivel.
    
    Parámetros:
        screen: superficie de pygame donde se dibuja
        nivel_actual: string que indica el nivel actual ("level1", "level2", "level3")
    
    Devuelve:
        "reintentar" - Volver a jugar el mismo nivel
        "siguiente" - Ir al siguiente nivel
        "salir" - Volver al menú principal
    """
    
    # Determinar opciones según el nivel
    if nivel_actual == "level3" or nivel_actual == "level_final":
        # Último nivel: no mostrar "Siguiente Nivel"
        OPCIONES = ["Reintentar", "Salir"]
    else:
        # Niveles normales: mostrar todas las opciones
        OPCIONES = ["Siguiente Nivel", "Reintentar", "Salir"]
    
    ancho, alto = screen.get_size()
    
    # Fuentes
    try:
        titulo_font = pygame.font.Font("font/pixel_font.ttf", 84)
        menu_font = pygame.font.Font("font/pixel_font.ttf", 56)
    except:
        titulo_font = pygame.font.SysFont("Arial", 70, bold=True)
        menu_font = pygame.font.SysFont("Arial", 48, bold=True)
    
    # Crear overlay semitransparente (fondo oscuro)
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    # Capturar la pantalla del nivel (fondo)
    fondo_nivel = screen.copy()
    
    seleccion_idx = 0
    
    # Animación
    tiempo_animacion = 0
    # Limpiar eventos previos para evitar selectores residuales
    try:
        pygame.event.clear()
    except Exception:
        pass
    
    # Bucle del menú de victoria
    clock = pygame.time.Clock()
    while True:
        tiempo_animacion += clock.get_time()
        
        # Redibujar fondo y overlay
        screen.blit(fondo_nivel, (0, 0))
        screen.blit(overlay, (0, 0))
        
        # ==================== PANEL DE VICTORIA ====================
        panel_w = 700
        panel_h = 400
        panel_x = ancho // 2 - panel_w // 2
        panel_y = alto // 2 - panel_h // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        # Sombra del panel
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 150), shadow_surface.get_rect(), border_radius=15)
        screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Panel principal (blanco)
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 250), panel_surface.get_rect(), border_radius=15)
        pygame.draw.rect(panel_surface, COLOR_BORDER, panel_surface.get_rect(), 5, border_radius=15)
        screen.blit(panel_surface, panel_rect.topleft)
        
        # ==================== TÍTULO "¡HAS GANADO!" ====================
        titulo_texto = titulo_font.render("¡HAS GANADO!", True, VERDE)
        titulo_rect = titulo_texto.get_rect(centerx=ancho // 2, top=panel_y + 30)
        
        # Efecto de brillo/pulsación en el título
        import math
        escala_pulso = 1.0 + 0.05 * math.sin(tiempo_animacion * 0.003)
        titulo_scaled = pygame.transform.scale(titulo_texto, 
                                              (int(titulo_texto.get_width() * escala_pulso), 
                                               int(titulo_texto.get_height() * escala_pulso)))
        titulo_scaled_rect = titulo_scaled.get_rect(center=titulo_rect.center)
        screen.blit(titulo_scaled, titulo_scaled_rect)
        
        # Línea decorativa
        linea_y = titulo_rect.bottom + 20
        pygame.draw.line(screen, COLOR_BORDER, 
                        (panel_x + 50, linea_y), 
                        (panel_x + panel_w - 50, linea_y), 3)
        
        # ==================== BOTONES DE OPCIONES ====================
        y_inicio_botones = linea_y + 40
        button_height = 60
        button_width = 500
        button_spacing = 20
        
        for i, opcion in enumerate(OPCIONES):
            is_selected = (i == seleccion_idx)
            
            # Posición del botón
            btn_x = ancho // 2 - button_width // 2
            btn_y = y_inicio_botones + i * (button_height + button_spacing)
            btn_rect = pygame.Rect(btn_x, btn_y, button_width, button_height)
            
            # Color del botón
            if is_selected:
                btn_color = COLOR_BORDER
                text_color = BLANCO
                border_width = 4
            else:
                btn_color = (220, 220, 220)
                text_color = (0, 0, 0)
                border_width = 3
            
            # Dibujar botón
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), btn_rect, border_width, border_radius=10)
            
            # Texto del botón
            texto = menu_font.render(opcion.upper(), True, text_color)
            texto_rect = texto.get_rect(center=btn_rect.center)
            screen.blit(texto, texto_rect)
        
        # Instrucción de navegación
        instruccion_font = pygame.font.SysFont(None, 28)
        instruccion_texto = instruccion_font.render("Usa ↑↓ o W/S para navegar, ENTER para seleccionar", True, (150, 150, 150))
        screen.blit(instruccion_texto, (ancho // 2 - instruccion_texto.get_width() // 2, panel_y + panel_h + 20))
        
        pygame.display.flip()
        clock.tick(60)
        
        # ==================== MANEJO DE EVENTOS ====================
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                # Navegación
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    seleccion_idx = (seleccion_idx + 1) % len(OPCIONES)
                
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    seleccion_idx = (seleccion_idx - 1) % len(OPCIONES)
                
                # Selección
                elif evento.key == pygame.K_RETURN:
                    opcion_seleccionada = OPCIONES[seleccion_idx].lower()
                    
                    if "siguiente" in opcion_seleccionada:
                        try:
                            pygame.event.clear()
                        except Exception:
                            pass
                        return "siguiente"
                    elif "reintentar" in opcion_seleccionada:
                        try:
                            pygame.event.clear()
                        except Exception:
                            pass
                        return "reintentar"
                    elif "salir" in opcion_seleccionada:
                        try:
                            pygame.event.clear()
                        except Exception:
                            pass
                        return "salir"


# ==================== FUNCIÓN PARA MENÚ DE DERROTA (GAME OVER) ====================

def mostrar_menu_derrota(screen, idioma="Español"):
    """
    Muestra el menú de derrota con mensajes positivos y alentadores.
    
    Parámetros:
        screen: superficie de pygame donde se dibuja
        idioma: idioma actual del juego ("Español" o "Inglés")
    
    Devuelve:
        "reintentar" - Volver a jugar el nivel
        "salir" - Volver al menú principal
    """
    import random
    from translations import get_text
    
    # Mensajes positivos y alentadores
    mensajes_espanol = [
        "¡Sigue intentando! ¡Tú puedes lograrlo!",
        "¡No te rindas! ¡Vuelve a intentarlo!",
        "¡Cada intento te hace mejor! ¡Sigue adelante!"
    ]
    
    mensajes_ingles = [
        "Keep trying! You can do it!",
        "Don't give up! Try again!",
        "Every attempt makes you better! Keep going!"
    ]
    
    # Seleccionar mensaje aleatorio
    if idioma == "Inglés":
        mensaje_aleatorio = random.choice(mensajes_ingles)
        OPCIONES = ["Retry", "Exit"]
    else:
        mensaje_aleatorio = random.choice(mensajes_espanol)
        OPCIONES = ["Reintentar", "Salir"]
    
    ancho, alto = screen.get_size()
    
    # Fuentes
    try:
        titulo_font = pygame.font.Font("font/pixel_font.ttf", 84)
        menu_font = pygame.font.Font("font/pixel_font.ttf", 56)
    except:
        titulo_font = pygame.font.SysFont("Arial", 70, bold=True)
        menu_font = pygame.font.SysFont("Arial", 48, bold=True)
    
    # Overlay
    overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    # Capturar fondo
    fondo_nivel = screen.copy()
    
    seleccion_idx = 0
    
    # Bucle del menú
    clock = pygame.time.Clock()
    # Limpiar eventos previos al mostrar el menú de derrota
    try:
        pygame.event.clear()
    except Exception:
        pass
    while True:
        # Redibujar fondo y overlay
        screen.blit(fondo_nivel, (0, 0))
        screen.blit(overlay, (0, 0))
        
        # ==================== PANEL DE DERROTA ====================
        panel_w = 700
        panel_h = 450  # Aumentado para acomodar el mensaje positivo
        panel_x = ancho // 2 - panel_w // 2
        panel_y = alto // 2 - panel_h // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        # Sombra
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 150), shadow_surface.get_rect(), border_radius=15)
        screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Panel principal con colores más positivos
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        # Fondo con gradiente amarillo/naranja positivo
        for i in range(panel_h):
            ratio = i / panel_h
            r = int(255 - ratio * 30)
            g = int(220 - ratio * 20)
            b = int(100 - ratio * 50)
            pygame.draw.line(panel_surface, (r, g, b), 
                            (0, i), (panel_w, i))
        pygame.draw.rect(panel_surface, (255, 200, 0), panel_surface.get_rect(), 5, border_radius=15)  # Borde dorado
        screen.blit(panel_surface, panel_rect.topleft)
        
        # ==================== TÍTULO POSITIVO ====================
        if idioma == "Inglés":
            titulo_text = "Keep Going!"
        else:
            titulo_text = "¡Sigue Adelante!"
        
        titulo_texto = titulo_font.render(titulo_text, True, (255, 140, 0))
        titulo_rect = titulo_texto.get_rect(centerx=ancho // 2, top=panel_y + 30)
        screen.blit(titulo_texto, titulo_rect)
        
        # ==================== MENSAJE ALEATORIO POSITIVO ====================
        mensaje_font = pygame.font.Font(None, 42)
        mensaje_surf = mensaje_font.render(mensaje_aleatorio, True, (50, 50, 50))
        mensaje_rect = mensaje_surf.get_rect(centerx=ancho // 2, top=titulo_rect.bottom + 40)
        screen.blit(mensaje_surf, mensaje_rect)
        
        # Línea decorativa
        linea_y = mensaje_rect.bottom + 30
        pygame.draw.line(screen, (255, 180, 0), 
                        (panel_x + 50, linea_y), 
                        (panel_x + panel_w - 50, linea_y), 3)
        
        # ==================== BOTONES ====================
        y_inicio_botones = linea_y + 60
        button_height = 60
        button_width = 500
        button_spacing = 20
        
        for i, opcion in enumerate(OPCIONES):
            is_selected = (i == seleccion_idx)
            
            btn_x = ancho // 2 - button_width // 2
            btn_y = y_inicio_botones + i * (button_height + button_spacing)
            btn_rect = pygame.Rect(btn_x, btn_y, button_width, button_height)
            
            if is_selected:
                # Color verde positivo para el botón seleccionado
                btn_color = (100, 200, 100)
                text_color = BLANCO
                border_width = 4
            else:
                btn_color = (240, 240, 240)
                text_color = (50, 50, 50)
                border_width = 2
            
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), btn_rect, border_width, border_radius=10)
            
            texto = menu_font.render(opcion.upper(), True, text_color)
            texto_rect = texto.get_rect(center=btn_rect.center)
            screen.blit(texto, texto_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        # ==================== EVENTOS ====================
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    seleccion_idx = (seleccion_idx + 1) % len(OPCIONES)
                
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    seleccion_idx = (seleccion_idx - 1) % len(OPCIONES)
                
                elif evento.key == pygame.K_RETURN:
                    # Usar índice en lugar de comparar texto traducido
                    if seleccion_idx == 0:  # Reintentar/Retry
                        try:
                            pygame.event.clear()
                        except Exception:
                            pass
                        return "reintentar"
                    elif seleccion_idx == 1:  # Salir/Exit
                        try:
                            pygame.event.clear()
                        except Exception:
                            pass
                        return "salir"