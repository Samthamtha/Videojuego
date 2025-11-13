import pygame
import sys
import math

WIDTH, HEIGHT = 1540, 785 

def show_credits(screen):
    clock = pygame.time.Clock()

    # Inicializar fuentes
    if not pygame.font.get_init():
        pygame.font.init()
    
    # Cargar fuentes personalizadas o usar por defecto
    try:
        title_font = pygame.font.Font("font/pixel_font.ttf", 72)
        name_font = pygame.font.Font("font/pixel_font.ttf", 36)
        subtitle_font = pygame.font.Font("font/pixel_font.ttf", 28)
        return_font = pygame.font.Font("font/pixel_font.ttf", 32)
    except:
        title_font = pygame.font.SysFont("Arial", 60, bold=True)
        name_font = pygame.font.SysFont("Arial", 32, bold=True)
        subtitle_font = pygame.font.SysFont("Arial", 24)
        return_font = pygame.font.SysFont("Arial", 28)
    
    # Colores modernos
    COLOR_TITLE = (255, 255, 0)  # Amarillo
    COLOR_NAME = (255, 255, 255)  # Blanco
    COLOR_SUBTITLE = (200, 200, 200)  # Gris claro
    COLOR_BORDER = (130, 200, 70)  # Verde lima
    
    # Cargar fondo
    try:
        fondo = pygame.image.load("img/pibble_fondo4.png").convert()
        fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Error al cargar fondo: {e}")
        fondo = pygame.Surface((WIDTH, HEIGHT))
        fondo.fill((20, 20, 50))
    
    # Overlay semi-transparente para contraste
    overlay = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
    overlay.fill((0, 0, 0))
    overlay.set_alpha(120)
    
    # Cargar logo de la facultad
    try:
        logo_fie = pygame.image.load("img/LOGO_FIE.png").convert_alpha()
        logo_fie = pygame.transform.scale(logo_fie, (150, 150))
    except pygame.error as e:
        print(f"Error al cargar logo FIE: {e}")
        logo_fie = None
    
    # Datos del equipo con nombres completos
    equipo = [
        ("Iara Samantha", "Guzmán Lizama", "img/samiC.png"),
        ("Álvaro Alberto", "Guerrero García", "img/alvaroC.png"),
        ("Brian Sebastián", "Silvestre", "img/brianC.png"),
        ("Romario", "Vázquez Contreras", "img/romarioC.png")
    ]

    # Dimensiones de las imágenes (más grandes y con efecto de tarjeta)
    img_width, img_height = 220, 220
    imagenes_cargadas = []
    
    for nombre, apellido, archivo in equipo:
        try:
            img = pygame.image.load(archivo).convert_alpha()
            img = pygame.transform.scale(img, (img_width, img_height))
            imagenes_cargadas.append(img)
        except pygame.error as e:
            print(f"Error al cargar imagen {archivo}: {e}")
            # Placeholder si falla
            placeholder_img = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
            pygame.draw.rect(placeholder_img, (60, 60, 60), placeholder_img.get_rect(), border_radius=15)
            pygame.draw.circle(placeholder_img, (150, 150, 150), 
                             (img_width // 2, img_height // 2), 60)
            imagenes_cargadas.append(placeholder_img)

    # Variables de animación
    animation_time = 0
    
    # Bucle Principal de Créditos
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return 

        animation_time += clock.get_time()
        
        # Dibujar fondo y overlay
        screen.blit(fondo, (0, 0))
        screen.blit(overlay, (0, 0))
        
        # ==================== TÍTULO "DESARROLLADORES" ====================
        title_text = "DESARROLLADORES"
        title_surface = title_font.render(title_text, True, COLOR_TITLE)
        title_rect = title_surface.get_rect(centerx=WIDTH // 2, top=40)
        
        # Efecto de respiración suave en el título
        title_offset = 3 * math.sin(animation_time * 0.002)
        title_rect.y += title_offset
        screen.blit(title_surface, title_rect)
        
        # Línea decorativa bajo el título
        line_y = title_rect.bottom + 15
        pygame.draw.line(screen, COLOR_BORDER, 
                        (WIDTH // 2 - 200, line_y), 
                        (WIDTH // 2 + 200, line_y), 4)
        
        # ==================== TARJETAS DE DESARROLLADORES ====================
        num_integrantes = len(equipo)
        card_spacing = 40
        card_padding = 20
        
        # Calcular ancho total
        total_content_width = (img_width * num_integrantes) + (card_spacing * (num_integrantes - 1))
        start_x = (WIDTH - total_content_width) // 2
        
        # Posición vertical
        cards_y = 220
        
        current_x = start_x
        
        for i, (nombre, apellido, archivo) in enumerate(equipo):
            # Efecto de flotación individual para cada tarjeta
            float_offset = 8 * math.sin((animation_time * 0.003) + (i * 0.5))
            card_y = cards_y + float_offset
            
            # Fondo de la tarjeta (efecto de tarjeta con sombra)
            card_rect = pygame.Rect(current_x - 15, card_y - 15, 
                                   img_width + 30, img_height + 120)
            
            # Sombra de la tarjeta
            shadow_rect = card_rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect(), border_radius=15)
            screen.blit(shadow_surface, shadow_rect.topleft)
            
            # Tarjeta principal (BLANCA)
            card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(card_surface, (255, 255, 255, 240), card_surface.get_rect(), border_radius=15)
            pygame.draw.rect(card_surface, COLOR_BORDER, card_surface.get_rect(), 3, border_radius=15)
            screen.blit(card_surface, card_rect.topleft)
            
            # Imagen del desarrollador (circular)
            img_x = current_x
            img_y = card_y
            
            # Crear máscara circular para la imagen
            mask_surface = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
            pygame.draw.circle(mask_surface, (255, 255, 255), 
                             (img_width // 2, img_height // 2), img_width // 2)
            
            # Aplicar máscara circular a la imagen
            temp_img = imagenes_cargadas[i].copy()
            temp_img.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(temp_img, (img_x, img_y))
            
            # Borde circular alrededor de la imagen
            pygame.draw.circle(screen, COLOR_BORDER, 
                             (img_x + img_width // 2, img_y + img_height // 2), 
                             img_width // 2, 4)
            
            # Nombres (centrados bajo la imagen)
            name_y = img_y + img_height + 15
            
            # Nombre (primera línea) - NEGRO para contraste con fondo blanco
            texto_nombre = name_font.render(nombre, True, (0, 0, 0))
            name_x = current_x + (img_width - texto_nombre.get_width()) // 2
            screen.blit(texto_nombre, (name_x, name_y))
            
            # Apellido (segunda línea) - GRIS OSCURO
            texto_apellido = subtitle_font.render(apellido, True, (80, 80, 80))
            apellido_x = current_x + (img_width - texto_apellido.get_width()) // 2
            screen.blit(texto_apellido, (apellido_x, name_y + 40))
            
            # Mover a la siguiente posición
            current_x += img_width + card_spacing
        
        # ==================== LOGO DE LA FACULTAD ====================
        if logo_fie:
            logo_x = 30
            logo_y = HEIGHT - 180
            
            # Fondo BLANCO para el logo
            logo_bg_rect = pygame.Rect(logo_x - 10, logo_y - 10, 170, 170)
            logo_bg_surface = pygame.Surface((logo_bg_rect.width, logo_bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(logo_bg_surface, (255, 255, 255, 240), logo_bg_surface.get_rect(), border_radius=10)
            pygame.draw.rect(logo_bg_surface, COLOR_BORDER, logo_bg_surface.get_rect(), 3, border_radius=10)
            screen.blit(logo_bg_surface, logo_bg_rect.topleft)
            
            screen.blit(logo_fie, (logo_x, logo_y))
        
        # ==================== MENSAJE DE VOLVER ====================
        # Efecto de parpadeo suave
        alpha_value = int(200 + 55 * math.sin(animation_time * 0.005))
        
        return_text = "PRESIONA ENTER PARA VOLVER"
        return_surface = return_font.render(return_text, True, COLOR_NAME)
        return_surface.set_alpha(alpha_value)
        return_rect = return_surface.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 40)
        
        # Fondo del botón de volver
        button_bg_rect = return_rect.inflate(40, 20)
        pygame.draw.rect(screen, (130, 200, 70, 100), button_bg_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_BORDER, button_bg_rect, 3, border_radius=10)
        
        screen.blit(return_surface, return_rect)

        pygame.display.flip()
        clock.tick(60)

# Para probar el archivo credits.py individualmente
if __name__ == "__main__":
    pygame.init()
    test_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Créditos del Juego")
    show_credits(test_screen)
    pygame.quit()
    sys.exit()