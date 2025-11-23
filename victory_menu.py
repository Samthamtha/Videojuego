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

def mostrar_menu_derrota(screen):
    """
    Muestra el menú de derrota/game over.
    
    Parámetros:
        screen: superficie de pygame donde se dibuja
    
    Devuelve:
        "reintentar" - Volver a jugar el nivel
        "salir" - Volver al menú principal
    """
    
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
        panel_h = 400
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
        
        # Panel principal
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 250), panel_surface.get_rect(), border_radius=15)
        pygame.draw.rect(panel_surface, (200, 0, 0), panel_surface.get_rect(), 5, border_radius=15)  # Borde rojo
        screen.blit(panel_surface, panel_rect.topleft)
        
        # ==================== TÍTULO "GAME OVER" ====================
        titulo_texto = titulo_font.render("GAME OVER", True, (200, 0, 0))
        titulo_rect = titulo_texto.get_rect(centerx=ancho // 2, top=panel_y + 30)
        screen.blit(titulo_texto, titulo_rect)
        
        # Línea decorativa
        linea_y = titulo_rect.bottom + 20
        pygame.draw.line(screen, (200, 0, 0), 
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
                btn_color = (200, 0, 0)
                text_color = BLANCO
                border_width = 4
            else:
                btn_color = (220, 220, 220)
                text_color = (0, 0, 0)
                border_width = 3
            
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
                    opcion_seleccionada = OPCIONES[seleccion_idx].lower()
                    
                    if "reintentar" in opcion_seleccionada:
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