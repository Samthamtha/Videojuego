import pygame
import sys
import random
import math
from pause import mostrar_menu_pausa
from victory_menu import mostrar_menu_victoria, mostrar_menu_derrota
import tutorial_nivel1
from translations import get_text

pygame.init()
WIDTH, HEIGHT = 1540, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nivel 1 - Separación de Basura")
clock = pygame.time.Clock()
FPS = 60

# Colores
BLUE = (0,100,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
DARK_GREEN = (0, 150, 0)
DARK_RED = (150, 0, 0)
DARK_BLUE = (0,70,180)
ORANGE = (255,165,0)
GRAY = (200,200,200)
LIGHT_GRAY = (220,220,220)
ACCENT_YELLOW = (255, 220, 0) # Nuevo color para alerta

# Tamaños
BIN_WIDTH_DEFAULT = 200
BIN_WIDTH_INORGANIC = 220
BIN_HEIGHT = 120
TRASH_SIZE = 80 
DANGER_SIZE = 100 # Tamaño para peligros (Tronco/Bomba)
ICON_BOX_SIZE = 72  # Tamaño del cuadrado de simbología (fondo blanco)
ICON_SMALL_SIZE = 28  # Tamaño del ícono de bote dentro del cuadro

# Botes de Basura
bin_organica = pygame.image.load("img/boteVerde.png").convert_alpha()
bin_organica = pygame.transform.scale(bin_organica, (BIN_WIDTH_DEFAULT, BIN_HEIGHT))
bin_reciclable = pygame.image.load("img/boteazul.png").convert_alpha()
bin_reciclable = pygame.transform.scale(bin_reciclable, (BIN_WIDTH_DEFAULT, BIN_HEIGHT))
bin_inorganico = pygame.image.load("img/boterojo.png").convert_alpha()
bin_inorganico = pygame.transform.scale(bin_inorganico, (BIN_WIDTH_INORGANIC, BIN_HEIGHT)) 

# Basura de Clasificación
trash_cascara = pygame.image.load("img/Cascara.png").convert_alpha()
trash_cascara = pygame.transform.scale(trash_cascara, (TRASH_SIZE, TRASH_SIZE))
trash_lata = pygame.image.load("img/Lata.png").convert_alpha()
trash_lata = pygame.transform.scale(trash_lata, (TRASH_SIZE, TRASH_SIZE))
trash_botella = pygame.image.load("img/botella.png").convert_alpha() 
trash_botella = pygame.transform.scale(trash_botella, (TRASH_SIZE, TRASH_SIZE))

TRASH_MAP = {
    'organica': trash_cascara,
    'reciclable': trash_lata,
    'inorganico': trash_botella 
}
TRASH_TYPES = list(TRASH_MAP.keys())

# --- Íconos para la simbología (usar las mismas imágenes, escaladas) ---
icon_organica = pygame.transform.scale(trash_cascara, (ICON_BOX_SIZE - 16, ICON_BOX_SIZE - 16))
icon_reciclable = pygame.transform.scale(trash_lata, (ICON_BOX_SIZE - 16, ICON_BOX_SIZE - 16))
icon_inorganico = pygame.transform.scale(trash_botella, (ICON_BOX_SIZE - 16, ICON_BOX_SIZE - 16))

# Pequeños botes para superponer en la esquina del cuadro (ayuda visual)
bin_icon_organica = pygame.transform.scale(bin_organica, (ICON_SMALL_SIZE, ICON_SMALL_SIZE))
bin_icon_reciclable = pygame.transform.scale(bin_reciclable, (ICON_SMALL_SIZE, ICON_SMALL_SIZE))
bin_icon_inorganico = pygame.transform.scale(bin_inorganico, (ICON_SMALL_SIZE, ICON_SMALL_SIZE))

# --- Objetos Peligrosos (Tronco y Bomba) ---
try:
    danger_tronco = pygame.image.load("img/Tronco.png").convert_alpha()
    danger_tronco = pygame.transform.scale(danger_tronco, (DANGER_SIZE, DANGER_SIZE))
except pygame.error:
    print("Advertencia: No se encontró img/Tronco.png. Usando fallback.")
    danger_tronco = pygame.Surface((DANGER_SIZE, DANGER_SIZE), pygame.SRCALPHA)
    danger_tronco.fill(DARK_RED)
    pygame.draw.rect(danger_tronco, BLACK, danger_tronco.get_rect(), 2)
    
try:
    danger_bomba = pygame.image.load("img/bomba.png").convert_alpha()
    danger_bomba = pygame.transform.scale(danger_bomba, (DANGER_SIZE, DANGER_SIZE))
except pygame.error:
    print("Advertencia: No se encontró img/bomba.png. Usando fallback.")
    danger_bomba = pygame.Surface((DANGER_SIZE, DANGER_SIZE), pygame.SRCALPHA)
    danger_bomba.fill((0, 0, 0))
    pygame.draw.circle(danger_bomba, (255, 0, 0), (DANGER_SIZE//2, DANGER_SIZE//2), DANGER_SIZE//2 - 5)

DANGER_MAP = {
    'tronco': danger_tronco,
    'bomba': danger_bomba
}
DANGER_TYPES = list(DANGER_MAP.keys())

# --- Personaje: Gato que lanza peligros ---
try:
    cat_thrower_img = pygame.image.load("img/gato_malo.png").convert_alpha()
    cat_thrower_img = pygame.transform.scale(cat_thrower_img, (200, 160))
except pygame.error:
    print("Advertencia: No se encontró img/gato_malo.png. Usando fallback.")
    cat_thrower_img = pygame.Surface((200, 160), pygame.SRCALPHA)
    cat_thrower_img.fill((120, 120, 120))
    pygame.draw.rect(cat_thrower_img, BLACK, cat_thrower_img.get_rect(), 3)


# Waypoints del río
RIVER_CENTER_WAYPOINTS = [
    (770, 200), (760, 280), (780, 360), (770, 440),
    (780, 520), (770, 600), (770, 680), (770, 750),
]

# Trayectoria del gato (recorre la orilla izquierda del río)
CAT_WAYPOINTS = [
    (600, 150), (540, 230), (570, 320),
    (520, 420), (590, 500), (650, 380),
    (630, 260)
]

def get_path_length(waypoints):
    if len(waypoints) < 2:
        return 1
    return sum(math.sqrt((waypoints[i+1][0] - waypoints[i][0])**2 +
                         (waypoints[i+1][1] - waypoints[i][1])**2)
               for i in range(len(waypoints) - 1))

def get_position_on_path(progress, waypoints, offset_x=0):
    if progress >= 1.0:
        return waypoints[-1][0] + offset_x, waypoints[-1][1]
    if progress <= 0.0:
        return waypoints[0][0] + offset_x, waypoints[0][1]
    num_segments = len(waypoints) - 1
    segment_length = 1.0 / num_segments
    segment_index = int(progress / segment_length)
    if segment_index >= num_segments:
        segment_index = num_segments - 1
    local_progress = (progress - segment_index * segment_length) / segment_length
    p1 = waypoints[segment_index]
    p2 = waypoints[segment_index + 1]
    x = p1[0] + (p2[0] - p1[0]) * local_progress + offset_x
    y = p1[1] + (p2[1] - p1[1]) * local_progress
    return x, y

class Trash(pygame.sprite.Sprite):
    def __init__(self, tipo, speed):
        super().__init__()
        self.tipo = tipo  # 'organica', 'reciclable', 'inorganico'
        self.es_peligro = False
        self.base_size = TRASH_SIZE
        self.current_size = int(self.base_size * 0.4)
        self.original_image = TRASH_MAP.get(tipo)
        self.image = pygame.transform.scale(self.original_image, (self.current_size, self.current_size))
        self.offset_x = random.randint(-30, 30)
        start_pos = RIVER_CENTER_WAYPOINTS[0]
        self.rect = self.image.get_rect(center=(start_pos[0] + self.offset_x, start_pos[1]))
        self.speed = speed
        self.progress = 0.0
        self.path_length = sum(math.sqrt((RIVER_CENTER_WAYPOINTS[i+1][0] - RIVER_CENTER_WAYPOINTS[i][0])**2 +
                                          (RIVER_CENTER_WAYPOINTS[i+1][1] - RIVER_CENTER_WAYPOINTS[i][1])**2)
                               for i in range(len(RIVER_CENTER_WAYPOINTS) - 1))
    
    def update(self):
        self.progress += self.speed / self.path_length
        if self.progress >= 1.0:
            self.kill()
        else:
            new_pos = get_position_on_path(self.progress, RIVER_CENTER_WAYPOINTS, self.offset_x)
            scale = 0.4 + 0.6 * self.progress
            new_size = int(self.base_size * scale)
            if abs(new_size - self.current_size) > 2:
                self.current_size = new_size
                self.image = pygame.transform.scale(self.original_image, (self.current_size, self.current_size))
            self.rect = self.image.get_rect(center=new_pos)

class Peligro(Trash):
    def __init__(self, tipo, speed):
        # Llama a __init__ de Trash pero con un tipo dummy 'organica' para inicializar variables
        super().__init__('organica', speed)
        self.tipo = tipo  # 'tronco' o 'bomba'
        self.es_peligro = True
        self.base_size = DANGER_SIZE
        self.original_image = DANGER_MAP.get(tipo)
        
        self.current_size = int(self.base_size * 0.4)
        self.image = pygame.transform.scale(self.original_image, (self.current_size, self.current_size))
        # Recalcula el rect con la nueva imagen y tamaño
        start_pos = RIVER_CENTER_WAYPOINTS[0]
        self.rect = self.image.get_rect(center=(start_pos[0] + self.offset_x, start_pos[1]))


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
        self.rect = self.image.get_rect(topleft=(x, HEIGHT - 130))

class PlayerBar:
    def __init__(self, x):
        self.botes = pygame.sprite.Group()
        self.botes.add(Bin('organica', x))
        self.botes.add(Bin('reciclable', x + 250))
        self.botes.add(Bin('inorganico', x + 500))
        self.rect = pygame.Rect(x, HEIGHT - 130, 720, 120)
    
    def move(self, dx):
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        bote_list = self.botes.sprites()
        bote_list[0].rect.x = self.rect.x
        bote_list[1].rect.x = self.rect.x + 250
        bote_list[2].rect.x = self.rect.x + 500
    
    def draw(self, surf):
        self.botes.draw(surf)

class CatThrower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_idle = cat_thrower_img
        self.image_throw = pygame.transform.rotate(cat_thrower_img, -8)
        self.image = self.image_idle
        self.throw_timer = 0
        first_wp = CAT_WAYPOINTS[0] if CAT_WAYPOINTS else (0, 0)
        self.rect = self.image.get_rect(midbottom=(first_wp[0], first_wp[1]))
        self.path_progress = 0.0
        self.path_direction = 1
        self.walk_speed = 140  # pixeles por segundo
        self.path_length = get_path_length(CAT_WAYPOINTS)

    def trigger_throw(self):
        self.throw_timer = 20

    def update(self, dt):
        prev_midbottom = self.rect.midbottom
        if self.throw_timer > 0:
            self.throw_timer -= 1
            next_image = self.image_throw
        else:
            next_image = self.image_idle

        if self.image != next_image:
            self.image = next_image
            self.rect = self.image.get_rect(midbottom=prev_midbottom)

        self._update_walk(dt)

    def _update_walk(self, dt):
        if not CAT_WAYPOINTS or self.path_length <= 0:
            return
        progress_delta = (self.walk_speed * dt) / self.path_length
        self.path_progress += progress_delta * self.path_direction

        if self.path_progress >= 1.0:
            self.path_progress = 1.0
            self.path_direction = -1
        elif self.path_progress <= 0.0:
            self.path_progress = 0.0
            self.path_direction = 1

        new_pos = get_position_on_path(self.path_progress, CAT_WAYPOINTS)
        self.rect.midbottom = (new_pos[0], new_pos[1])

def run_level1(dificultad, idioma, screen):
    global WIDTH, HEIGHT, clock, FPS
    # --- Config dificultad ---
    # Ajuste de spawn rate para que aparezcan pocos peligros
    dificultad_lower = dificultad.lower()
    if dificultad_lower in ["principiante"]:
        trash_speed = 1.4
        spawn_rate = 150
        danger_spawn_rate = 450
        danger_pool = ['tronco']
    elif dificultad_lower in ["profesional"]:
        trash_speed = 3
        spawn_rate = 100
        danger_spawn_rate = 300
        danger_pool = ['tronco', 'tronco', 'tronco', 'tronco', 'bomba']
    else:  # Intermedio: 360 ticks (6 segundos) por peligro
        trash_speed = 2.2
        spawn_rate = 120
        danger_spawn_rate = 360
        danger_pool = ['tronco']

    # Se mantiene la misma meta y puntuación
    PUNTOS = 25
    TIEMPO_TOTAL = 70
    tiempo_restante = TIEMPO_TOTAL
    METAS = {'reciclable': 4, 'organica': 2, 'inorganico': 2}
    CONTADOR = {'reciclable': 0, 'organica': 0, 'inorganico': 0}
    juego_finalizado = False
    danger_penalty_display = 0  # Contador para mostrar la penalización por peligro

    # --- Fondo ---
    try:
        fondo = pygame.image.load("img/rio.png").convert()
        fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
    except pygame.error:
        fondo = pygame.Surface((WIDTH, HEIGHT))
        fondo.fill(BLUE)

    # --- Tutorial ---
    resultado_tutorial = tutorial_nivel1.mostrar_tutorial(screen, fondo)
    if resultado_tutorial == "salir_juego":
        return "salir_juego"

    # --- Sprites ---
    all_sprites = pygame.sprite.Group()
    trashes = pygame.sprite.Group()
    player = PlayerBar(WIDTH // 2 - 360)
    all_sprites.add(player.botes)
    cat_thrower = CatThrower()
    spawn_timer = 0
    danger_timer = 0
    font = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 28)
    font_danger = pygame.font.SysFont(None, 24)  # Fuente más pequeña para el texto de peligro

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- Actualización juego ---
        if not juego_finalizado:
            tiempo_restante -= dt
            if PUNTOS <= 0 or tiempo_restante <= 0:
                PUNTOS = max(PUNTOS, 0)
                tiempo_restante = max(tiempo_restante, 0)
                juego_finalizado = True
            if all(CONTADOR[tipo] >= METAS[tipo] for tipo in METAS):
                juego_finalizado = True
        
        # Actualizar contador de penalización
        if danger_penalty_display > 0:
            danger_penalty_display -= 1

        # --- Eventos ---
        skip = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.event.clear()
                accion = mostrar_menu_pausa(screen, HEIGHT, WIDTH, idioma)
                if accion == "reanudar":
                    skip = True
                    break
                elif accion == "reiniciar":
                    return "reiniciar"
                elif accion == "salir":
                    return "salir_menu"
        if skip:
            continue

        cat_thrower.update(dt)

        keys = pygame.key.get_pressed()
        dx = 0
        if not juego_finalizado:
            # --- Movimiento del Jugador ---
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -8
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 8
            player.move(dx)
            
            # --- Aparición de Basura de Clasificación ---
            spawn_timer += 1
            spawned_this_cycle = False
            if spawn_timer >= spawn_rate:
                tipo = random.choice(TRASH_TYPES)
                t = Trash(tipo, trash_speed)
                all_sprites.add(t)
                trashes.add(t)
                spawn_timer = 0
                spawned_this_cycle = True
                
            # --- Aparición de Peligros (Tronco/Bomba) ---
            danger_timer += 1
            if danger_timer >= danger_spawn_rate and not spawned_this_cycle:
                # Selección condicionada por dificultad (bombas sólo a partir de profesional)
                danger_type = random.choice(danger_pool)
                d = Peligro(danger_type, trash_speed)
                all_sprites.add(d)
                trashes.add(d)
                danger_timer = 0
                cat_thrower.trigger_throw()

            trashes.update()
            
            # --- Detección de Colisiones ---
            for trash in trashes:
                for bin in player.botes:
                    if trash.rect.colliderect(bin.rect):
                        
                        if trash.es_peligro:
                            if trash.tipo == 'tronco':
                                PUNTOS -= 1  # Penalización por Tronco: -1 Puntos
                                danger_penalty_display = 60  # Muestra el mensaje por 1 segundo (60 frames)
                                print("¡Peligro! Colisión con Tronco. -1 Puntos.")
                            elif trash.tipo == 'bomba':
                                PUNTOS = 0  # Penalización por Bomba: Derrota Inmediata
                                juego_finalizado = True
                                print("¡GAME OVER! Colisión con BOMBA.")
                        
                        elif trash.tipo == bin.tipo and CONTADOR[trash.tipo] < METAS[trash.tipo]:
                            CONTADOR[trash.tipo] += 1  # Clasificación Correcta: +1 a la Meta
                            print(f"¡Correcto! Recolectaste {trash.tipo}. Meta: {CONTADOR[trash.tipo]}/{METAS[trash.tipo]}")
                        
                        else:
                            PUNTOS -= 1  # Clasificación Incorrecta: -1 Punto
                            print(f"¡Error! Clasificación incorrecta. -1 Punto.")
                        
                        trash.kill()
                        break 
                        
            # --- Eliminación de basura que sale de la pantalla ---
            # Si la basura normal o el peligro pasan la línea inferior sin ser tocados
            for trash in trashes.copy(): 
                if trash.rect.top > HEIGHT:
                    # La basura normal que no se atrapa se elimina sin penalización
                    # Los peligros que se escapan también se eliminan sin penalización
                    trash.kill()
            

        # --- DIBUJO ---
        screen.blit(fondo,(0,0))
        screen.blit(cat_thrower.image, cat_thrower.rect)
        trashes.draw(screen)
        player.draw(screen) 
        
        # --- Simbología vertical izquierda (cuadrados blancos con imágenes) ---
        SYM_X = 10
        SYM_Y = 10
        SYM_WIDTH = ICON_BOX_SIZE + 24
        SYM_GAP = 12
        # Altura total basada en 3 iconos apilados
        SYM_HEIGHT = ICON_BOX_SIZE * 3 + SYM_GAP * 2 + 20
        sym_rect = pygame.Rect(SYM_X, SYM_Y, SYM_WIDTH, SYM_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, sym_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, sym_rect, 2, border_radius=8)

        # Dibujar cada cuadro blanco con la imagen centrada y un pequeño ícono de bote
        types = [('organica', icon_organica, bin_icon_organica),
                 ('reciclable', icon_reciclable, bin_icon_reciclable),
                 ('inorganico', icon_inorganico, bin_icon_inorganico)]
        icon_x = SYM_X + 12
        icon_y = SYM_Y + 10
        for tipo, icon_img, bin_icon in types:
            box_rect = pygame.Rect(icon_x, icon_y, ICON_BOX_SIZE, ICON_BOX_SIZE)
            pygame.draw.rect(screen, WHITE, box_rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=6)
            # Centrar el ícono de basura dentro del cuadro
            img_rect = icon_img.get_rect(center=box_rect.center)
            screen.blit(icon_img, img_rect)
            # Dibujar el pequeño bote en la esquina inferior derecha del cuadro
            bin_rect = bin_icon.get_rect()
            bin_rect.bottomright = (box_rect.right - 6, box_rect.bottom - 6)
            screen.blit(bin_icon, bin_rect)
            # Etiqueta simple a la derecha del cuadro
            label = get_text({'organica':'ORGÁNICA','reciclable':'RECICLABLE','inorganico':'INORGÁNICA'}[tipo], idioma)
            label_s = font_small.render(label, True, BLACK)
            screen.blit(label_s, (box_rect.right + 8, box_rect.y + (ICON_BOX_SIZE - label_s.get_height())//2))
            icon_y += ICON_BOX_SIZE + SYM_GAP

        # --- Panel izquierdo de referencias y metas (HUD) ---
        # Movemos el panel a la derecha para evitar solapamiento con la simbología.
        PANEL_WIDTH = 300
        PANEL_HEIGHT = 360
        panel_rect=pygame.Rect(110,10,PANEL_WIDTH,PANEL_HEIGHT)
        pygame.draw.rect(screen,LIGHT_GRAY,panel_rect,border_radius=8)
        pygame.draw.rect(screen,BLACK,panel_rect,3,border_radius=8)
        
        # Título
        titulo_surf = font.render(get_text("OBJETIVOS DE RECOLECCIÓN", idioma), True, BLACK)
        # Centramos el título dentro del nuevo ancho
        titulo_x = panel_rect.x + (PANEL_WIDTH - titulo_surf.get_width()) // 2
        screen.blit(titulo_surf, (titulo_x, panel_rect.y + 10))

        # Subtítulo (Mi Puntuación)
        subtitulo_surf = font_small.render(get_text("MI PUNTUACIÓN DE RECICLAJE", idioma), True, (50, 50, 50))
        subtitulo_x = panel_rect.x + (PANEL_WIDTH - subtitulo_surf.get_width()) // 2
        screen.blit(subtitulo_surf, (subtitulo_x, panel_rect.y + 45))

        y_off=75 # Iniciar más abajo para dejar espacio al subtítulo
        for tipo in ['reciclable','organica','inorganico']:
            color={'organica':DARK_GREEN,'reciclable':DARK_BLUE,'inorganico':DARK_RED}[tipo]
            
            # Etiqueta de la basura (RECICLABLE, ORGÁNICA, INORGÁNICA)
            label_map = {'reciclable': get_text("RECICLABLE", idioma), 'organica': get_text("ORGÁNICA", idioma), 'inorganico': get_text("INORGÁNICA", idioma)}
            label = label_map.get(tipo, tipo.upper())
            label_surf = font_small.render(f"[{label}]", True, color)
            screen.blit(label_surf, (panel_rect.x + 10, panel_rect.y + y_off))

            # Texto de la meta (0/4)
            goal_surf=font_small.render(f"{CONTADOR[tipo]}/{METAS[tipo]}",True,BLACK)
            # Dibujamos la meta a la derecha del panel
            screen.blit(goal_surf, (panel_rect.right - 10 - goal_surf.get_width(), panel_rect.y + y_off))
            
            # Barra de progreso
            barra_x = panel_rect.x + 10
            barra_w = PANEL_WIDTH - 20 
            barra_h = 20
            barra_rect=pygame.Rect(barra_x, panel_rect.y + y_off + 25, barra_w, barra_h)
            
            progreso=CONTADOR[tipo]/METAS[tipo] if METAS[tipo] > 0 else 0
            pygame.draw.rect(screen,GRAY,barra_rect)
            pygame.draw.rect(screen,color,(barra_rect.x,barra_rect.y,int(barra_rect.width*progreso),barra_rect.height))
            pygame.draw.rect(screen,BLACK,barra_rect,2)
            y_off+=85 # Aumentar el espaciado para la siguiente meta

        # --- Indicador de Peligros ---
        if danger_penalty_display > 0:
            # Creamos un pequeño banner para la alerta
            text_alert = get_text("¡PELIGRO! Tronco: -2 PUNTOS", idioma)
            alert_surf = font_danger.render(text_alert, True, BLACK)
            
            alert_w = alert_surf.get_width() + 20
            alert_h = alert_surf.get_height() + 10
            alert_x = (WIDTH // 2) - (alert_w // 2)
            alert_y = 100
            
            alert_rect = pygame.Rect(alert_x, alert_y, alert_w, alert_h)
            
            # Dibujar fondo amarillo brillante
            pygame.draw.rect(screen, ACCENT_YELLOW, alert_rect, border_radius=6)
            pygame.draw.rect(screen, DARK_RED, alert_rect, 3, border_radius=6)
            
            # Dibujar el texto
            screen.blit(alert_surf, (alert_x + 10, alert_y + 5))

        # --- Puntos y tiempo (HUD Superior Derecho) ---
        # Puntos
        puntos_surf=font.render(f"{get_text('PUNTOS', idioma)}: {PUNTOS}",True,BLACK)
        puntos_rect=puntos_surf.get_rect(topright=(WIDTH-20,20))
        pygame.draw.rect(screen, LIGHT_GRAY, (puntos_rect.x - 10, puntos_rect.y - 5, puntos_rect.width + 20, puntos_rect.height + 10), border_radius=6)
        pygame.draw.rect(screen, BLACK, (puntos_rect.x - 10, puntos_rect.y - 5, puntos_rect.width + 20, puntos_rect.height + 10), 2, border_radius=6)
        screen.blit(puntos_surf, puntos_rect)
        
        # Tiempo
        tiempo_surf=font.render(f"{get_text('Tiempo', idioma)}: {int(tiempo_restante)}s",True,BLACK)
        screen.blit(tiempo_surf,(WIDTH-200,60))
        
        # Barra de tiempo
        barra_x,barra_y,barra_w,barra_h=WIDTH-300,95,280,25
        pygame.draw.rect(screen,GRAY,(barra_x,barra_y,barra_w,barra_h),border_radius=6)
        tiempo_progreso=tiempo_restante/TIEMPO_TOTAL
        if tiempo_progreso>0.6: color_tiempo=(0,200,0)
        elif tiempo_progreso>0.3: color_tiempo=(255,200,0)
        else: color_tiempo=(200,0,0)
        pygame.draw.rect(screen,color_tiempo,(barra_x+2,barra_y+2,int((barra_w-4)*tiempo_progreso),barra_h-4),border_radius=6)
        pygame.draw.rect(screen,BLACK,(barra_x,barra_y,barra_w,barra_h),2,border_radius=6)
        
        # --- Finalización ---
        if juego_finalizado:
            # Revisa la condición de derrota
            if PUNTOS <= 0 and tiempo_restante > 0: # Derrota por puntos (incluye bomba o por fallar muchas veces)
                accion=mostrar_menu_derrota(screen)
            elif tiempo_restante <= 0 and not all(CONTADOR[tipo]>=METAS[tipo] for tipo in METAS): # Derrota por tiempo
                accion=mostrar_menu_derrota(screen)
            else: # Victoria (cumplió todas las metas)
                accion=mostrar_menu_victoria(screen,"level1")
                
            if accion=="siguiente": return "siguiente"
            elif accion=="reintentar": return "reiniciar"
            elif accion=="salir": return "salir_menu"

        pygame.display.flip()
    return "siguiente"

if __name__=="__main__":
    accion=run_level1("Intermedio","Español",screen)
    print(f"Resultado: {accion}")
    pygame.quit(); sys.exit()