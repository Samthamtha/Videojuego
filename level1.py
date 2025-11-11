# level1.py
import pygame
import sys
import random
from pause import mostrar_menu_pausa

pygame.init()
WIDTH, HEIGHT = 1540, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nivel 1 - Separación de Basura")
clock = pygame.time.Clock()
FPS = 60

# Colores
BLUE = (0,100,255)
DARK_BLUE = (0, 70, 180) 
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,200,0)
DARK_GREEN = (0, 150, 0)
RED = (200,0,0)
DARK_RED = (150, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0) 
GRIS_PANEL = (220, 220, 220)

font = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 28)
font_large = pygame.font.SysFont(None, 48)

# -Carga de imágenes
# tamaños de los elementos del juego
BIN_WIDTH_DEFAULT = 200
BIN_WIDTH_INORGANIC = 220
BIN_HEIGHT = 120
TRASH_SIZE = 80 

# Botes de Basura en su tamaño original
bin_organica = pygame.image.load("img/boteVerde.png").convert_alpha()
bin_organica = pygame.transform.scale(bin_organica, (BIN_WIDTH_DEFAULT, BIN_HEIGHT))
bin_reciclable = pygame.image.load("img/boteazul.png").convert_alpha()
bin_reciclable = pygame.transform.scale(bin_reciclable, (BIN_WIDTH_DEFAULT, BIN_HEIGHT))
bin_inorganico = pygame.image.load("img/boterojo.png").convert_alpha()
bin_inorganico = pygame.transform.scale(bin_inorganico, (BIN_WIDTH_INORGANIC, BIN_HEIGHT)) 

# Basura que cae en su tamaño original
trash_cascara = pygame.image.load("img/Cascara.png").convert_alpha()
trash_cascara = pygame.transform.scale(trash_cascara, (TRASH_SIZE, TRASH_SIZE))
trash_lata = pygame.image.load("img/Lata.png").convert_alpha()
trash_lata = pygame.transform.scale(trash_lata, (TRASH_SIZE, TRASH_SIZE))
trash_botella = pygame.image.load("img/botella.png").convert_alpha() 
trash_botella = pygame.transform.scale(trash_botella, (TRASH_SIZE, TRASH_SIZE))

# --- Imágenes para Simbología que estan redimensionadas solo para el panel
BIN_SIMB_WIDTH = 80
BIN_SIMB_HEIGHT = 50
TRASH_SIMB_SIZE = 40

bin_organica_simb = pygame.transform.scale(bin_organica, (BIN_SIMB_WIDTH, BIN_SIMB_HEIGHT))
bin_reciclable_simb = pygame.transform.scale(bin_reciclable, (BIN_SIMB_WIDTH, BIN_SIMB_HEIGHT))
bin_inorganico_simb = pygame.transform.scale(bin_inorganico, (90, BIN_SIMB_HEIGHT)) 

trash_cascara_simb = pygame.transform.scale(trash_cascara, (TRASH_SIMB_SIZE, TRASH_SIMB_SIZE))
trash_lata_simb = pygame.transform.scale(trash_lata, (TRASH_SIMB_SIZE, TRASH_SIMB_SIZE))
trash_botella_simb = pygame.transform.scale(trash_botella, (TRASH_SIMB_SIZE, TRASH_SIMB_SIZE))


# Mapeo para generar basura
TRASH_MAP = {
    'organica': trash_cascara,
    'reciclable': trash_lata,
    'inorganico': trash_botella 
}
TRASH_TYPES = list(TRASH_MAP.keys())

# Simbología visual para el panel
SIMBOLOGIA_VISUAL = [
    ('RECICLABLE', bin_reciclable_simb, trash_lata_simb, DARK_BLUE),
    ('ORGÁNICA', bin_organica_simb, trash_cascara_simb, DARK_GREEN),
    ('INORGÁNICA', bin_inorganico_simb, trash_botella_simb, DARK_RED),
]


# -Sprites

class Trash(pygame.sprite.Sprite):
    def __init__(self, tipo, x, speed):
        super().__init__()
        self.tipo = tipo
        self.image = pygame.Surface((TRASH_SIZE, TRASH_SIZE), pygame.SRCALPHA)
        self.image.blit(TRASH_MAP.get(tipo), (0, 0)) 
        self.rect = self.image.get_rect(topleft=(x,-40))
        self.speed = speed 

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill() 

class Bin(pygame.sprite.Sprite):
    def __init__(self, tipo, x):
        super().__init__()
        self.tipo = tipo
        width = BIN_WIDTH_INORGANIC if tipo == 'inorganico' else BIN_WIDTH_DEFAULT
        self.image = pygame.Surface((width, BIN_HEIGHT), pygame.SRCALPHA)
        
        if tipo == 'organica':
            self.image.blit(bin_organica, (0, 0))
        elif tipo == 'reciclable':
            self.image.blit(bin_reciclable, (0, 0))
        else: 
            self.image.blit(bin_inorganico, (0, 0))
            
        self.rect = self.image.get_rect(topleft=(x, HEIGHT-130))

class PlayerBar:
    def __init__(self, x):
        self.botes = pygame.sprite.Group()
        self.botes.add(Bin('organica', x))
        self.botes.add(Bin('reciclable', x + 250)) 
        self.botes.add(Bin('inorganico', x + 500))
        # El ancho total de la barra de botes es de aproximadamente 720px (200 + 50 + 200 + 50 + 220)
        self.rect = pygame.Rect(x, HEIGHT-130, 720, 120)

    def move(self, dx):
        self.rect.x += dx
        
        # Estas restricciones limitan el movimiento de la barra a la pantalla (0 a WIDTH)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            
        bote_list = self.botes.sprites()
        bote_list[0].rect.x = self.rect.x 
        bote_list[1].rect.x = self.rect.x + 250 
        bote_list[2].rect.x = self.rect.x + 500 

    def draw(self, surface):
        self.botes.draw(surface)

# Función principal
def run_level1(dificultad, idioma, screen):
    global WIDTH, HEIGHT, clock, FPS

    # Ajuste de velocidad (vertical) y tasa de generación (horizontal)
    if dificultad.lower() == "fácil" or dificultad.lower() == "facil":
        trash_speed = 2  
        spawn_rate = 180 
    elif dificultad.lower() == "difícil" or dificultad.lower() == "dificil":
        trash_speed = 4  
        spawn_rate = 120 
    else: # Normal
        trash_speed = 3  
        spawn_rate = 150 

    # Variables de Estado del Juego
    PUNTOS = 20 
    TIEMPO_TOTAL = 60.0 
    tiempo_restante = TIEMPO_TOTAL
    
    METAS = {
        'reciclable': 4, 
        'organica': 2,   
        'inorganico': 2  
    }
    CONTADOR = {
        'reciclable': 0,
        'organica': 0,
        'inorganico': 0
    }
    
    juego_finalizado = False
    
    # Fondo
    try:
        fondo = pygame.image.load("img/rio.png").convert()
        fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
    except pygame.error:
        fondo = pygame.Surface((WIDTH, HEIGHT))
        fondo.fill(BLUE)

    all_sprites = pygame.sprite.Group()
    trashes = pygame.sprite.Group()

    player = PlayerBar(WIDTH // 2 - 360) 
    all_sprites.add(player.botes)

    spawn_timer = 0

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0 
        
        # Lógica de Juego Finalizado / Tiempo / Puntos
        if not juego_finalizado:
            tiempo_restante -= delta_time
            
            if PUNTOS <= 0 or tiempo_restante <= 0: 
                PUNTOS = max(0, PUNTOS)
                tiempo_restante = max(0, tiempo_restante)
                juego_finalizado = True
            
            if all(CONTADOR[tipo] >= METAS[tipo] for tipo in METAS):
                 juego_finalizado = True

        skip_event_processing = False 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego" 

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.event.clear()
                accion = mostrar_menu_pausa(screen, HEIGHT, WIDTH) 

                if accion == "reanudar":
                    skip_event_processing = True
                    break 
                elif accion == "reiniciar":
                    return "reiniciar" 
                elif accion == "salir":
                    return "salir_menu" 

        if skip_event_processing:
            continue

        # Lógica de juego solo si no ha finalizado
        if not juego_finalizado:
            # Movimiento
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -8
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 8
            player.move(dx)

            # Generar basura
            spawn_timer += 1
            if spawn_timer >= spawn_rate:
                tipo = random.choice(TRASH_TYPES) 
                # rango: 550 a 990. Esto reduce el espacio de caída a una zona más manejable
                trash = Trash(tipo, random.randint(550, 990), trash_speed) 
                all_sprites.add(trash)
                trashes.add(trash)
                spawn_timer = 0

            # Actualizar basura
            trashes.update()

            # Colisiones
            for trash in trashes:
                colision_detectada = False
                for bin in player.botes:
                    if trash.rect.colliderect(bin.rect):
                        colision_detectada = True
                        
                        if trash.tipo == bin.tipo:
                            # BASURA CORRECTA
                            if CONTADOR[trash.tipo] < METAS[trash.tipo]:
                                CONTADOR[trash.tipo] += 1
                        else:
                            # BASURA INCORRECTA: RESTA PUNTO
                            PUNTOS -= 1
                            
                        trash.kill()
                        break
                
        #Dibujo y renderizado 
        screen.blit(fondo, (0, 0))
        
        # Dibuja la simbología de Botes que es un panel vertical a la izquierda)
        PANEL_SIMB_ANCHO = 200
        PANEL_SIMB_ALTO = 300
        x_simb = 20
        y_simb = HEIGHT // 2 - PANEL_SIMB_ALTO // 2
        
        panel_simbologia_rect = pygame.Rect(x_simb, y_simb, PANEL_SIMB_ANCHO, PANEL_SIMB_ALTO)
        pygame.draw.rect(screen, GRIS_PANEL, panel_simbologia_rect, 0, 5) 
        pygame.draw.rect(screen, BLACK, panel_simbologia_rect, 2, 5) 

        text_title_simb = font.render("REFERENCIA", True, BLACK)
        screen.blit(text_title_simb, (x_simb + PANEL_SIMB_ANCHO // 2 - text_title_simb.get_width() // 2, y_simb + 10))

        # Dibuja imágenes de simbología
        y_pos = y_simb + 50
        for tipo, img_bote, img_trash, color in SIMBOLOGIA_VISUAL:
            
            # se muestra el bote
            x_bote = x_simb + 10
            screen.blit(img_bote, (x_bote, y_pos))
            
            # pues aqui muestra la flecha que seria el símbolo de relación
            flecha_texto = font.render("->", True, BLACK)
            screen.blit(flecha_texto, (x_bote + img_bote.get_width() + 5, y_pos + 10))
            
            # aqui se muestra la basura Basura
            x_trash = x_bote + img_bote.get_width() + flecha_texto.get_width() + 10
            screen.blit(img_trash, (x_trash, y_pos + 5))
            
            y_pos += 80 


        # 2. muestra los puntos en la esquina superior izquierda, fuera del panel
        text_points = font_large.render(f"PUNTOS: {PUNTOS}", True, RED if PUNTOS <= 5 else BLACK)
        screen.blit(text_points, (20, 20))

        # Dibuja metas de mecolección que es un panel - Superior Central
        panel_meta_rect = pygame.Rect(WIDTH // 2 - 200, 20, 400, 150)
        pygame.draw.rect(screen, YELLOW, panel_meta_rect, 0, 5) 
        pygame.draw.rect(screen, BLACK, panel_meta_rect, 2, 5) 

        text_title_meta = font.render("OBJETIVOS DE RECOLECCIÓN", True, BLACK)
        screen.blit(text_title_meta, (panel_meta_rect.x + panel_meta_rect.width // 2 - text_title_meta.get_width() // 2, panel_meta_rect.y + 10))

        # muestra las metas de recoleccion de la basura
        y_pos_meta = panel_meta_rect.y + 40
        for tipo, meta in METAS.items():
            color = BLUE if tipo == 'reciclable' else (GREEN if tipo == 'organica' else RED)
            texto_meta = font.render(f"[{tipo.upper()}]: {CONTADOR[tipo]} / {meta}", True, color)
            screen.blit(texto_meta, (panel_meta_rect.x + 20, y_pos_meta))
            y_pos_meta += 30

        # en esta parte pues se pone la barra de Tiempo que se encuentra arriba a la derecha
        BARRA_TIEMPO_ANCHO = 300
        BARRA_TIEMPO_ALTO = 25
        x_barra_tiempo = WIDTH - BARRA_TIEMPO_ANCHO - 20
        y_barra_tiempo = 20
        
        pygame.draw.rect(screen, DARK_RED, (x_barra_tiempo, y_barra_tiempo, BARRA_TIEMPO_ANCHO, BARRA_TIEMPO_ALTO), 3)
        progreso_ancho = int((tiempo_restante / TIEMPO_TOTAL) * BARRA_TIEMPO_ANCHO)
        pygame.draw.rect(screen, ORANGE, (x_barra_tiempo, y_barra_tiempo, progreso_ancho, BARRA_TIEMPO_ALTO))
        
        texto_tiempo = font.render(f"Tiempo: {int(tiempo_restante)}s", True, BLACK)
        screen.blit(texto_tiempo, (x_barra_tiempo + BARRA_TIEMPO_ANCHO - texto_tiempo.get_width() - 10, y_barra_tiempo + BARRA_TIEMPO_ALTO + 5))
        
        
        all_sprites.draw(screen)
        player.draw(screen)
        trashes.draw(screen)


        # Aqui serian los mensajes de finalización y de game over
        if juego_finalizado:
            mensaje = ""
            victoria = all(CONTADOR[tipo] >= METAS[tipo] for tipo in METAS)
            
            if victoria:
                mensaje = "¡NIVEL COMPLETADO! Meta de recolección alcanzada."
                color = GREEN
            elif PUNTOS <= 0:
                mensaje = "¡GAME OVER! Se acabaron los puntos."
                color = RED
            elif tiempo_restante <= 0:
                mensaje = "¡GAME OVER! Se acabó el tiempo."
                color = RED
                
            if mensaje:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150)) 
                screen.blit(overlay, (0, 0))
                
                text_gameover = font_large.render(mensaje, True, color)
                rect_gameover = text_gameover.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(text_gameover, rect_gameover)
                
                pygame.display.flip()
                pygame.time.wait(3000)
                return "siguiente" if victoria else "salir_menu"

        pygame.display.flip()
        
    return "siguiente" 

# --- Ejecutar nivel solo ---
if __name__ == "__main__":
    accion = run_level1("Normal", "Español", screen)
    print(f"Resultado de la prueba: {accion}")
    pygame.quit()
    sys.exit()