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
ACCENT_YELLOW = (255, 220, 0)

# Tamaños
BIN_WIDTH_DEFAULT = 200
BIN_WIDTH_INORGANIC = 220
BIN_HEIGHT = 120
TRASH_SIZE = 80
DANGER_SIZE = 100
ICON_BOX_SIZE = 64        # simbología pequeña
ICON_SMALL_SIZE = 24      # botes pequeños

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

# Íconos para simbología
icon_organica   = pygame.transform.scale(trash_cascara, (ICON_BOX_SIZE - 20, ICON_BOX_SIZE - 20))
icon_reciclable = pygame.transform.scale(trash_lata,     (ICON_BOX_SIZE - 20, ICON_BOX_SIZE - 20))
icon_inorganico = pygame.transform.scale(trash_botella,  (ICON_BOX_SIZE - 20, ICON_BOX_SIZE - 20))

# Pequeños botes para la simbología
bin_icon_organica   = pygame.transform.scale(bin_organica,   (ICON_SMALL_SIZE, ICON_SMALL_SIZE))
bin_icon_reciclable = pygame.transform.scale(bin_reciclable, (ICON_SMALL_SIZE, ICON_SMALL_SIZE))
bin_icon_inorganico = pygame.transform.scale(bin_inorganico, (ICON_SMALL_SIZE, ICON_SMALL_SIZE))

# Objetos Peligrosos (Tronco y Bomba)
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

# Personaje: Gato que lanza peligros
try:
    cat_thrower_img = pygame.image.load("img/gato_malo.png").convert_alpha()
    cat_thrower_img = pygame.transform.scale(cat_thrower_img, (200, 160))
except pygame.error:
    print("Advertencia: No se encontró img/gato_malo.png. Usando fallback.")
    cat_thrower_img = pygame.Surface((200, 160), pygame.SRCALPHA)
    cat_thrower_img.fill((120, 120, 120))
    pygame.draw.rect(cat_thrower_img, BLACK, cat_thrower_img.get_rect(), 3)

# Waypoints del río (solo para la basura)
RIVER_CENTER_WAYPOINTS = [
    (770, 200), (760, 280), (780, 360), (770, 440),
    (780, 520), (770, 600), (770, 680), (770, 750),
]

def get_path_length(waypoints):
    if len(waypoints) < 2:
        return 1
    return sum(
        math.dist(waypoints[i], waypoints[i+1])
        for i in range(len(waypoints)-1)
    )

def get_position_on_path(progress, waypoints, offset_x=0):
    n = len(waypoints)
    if n < 2:
        return waypoints[0]
    if progress <= 0:
        return waypoints[0][0] + offset_x, waypoints[0][1]
    if progress >= 1:
        return waypoints[-1][0] + offset_x, waypoints[-1][1]

    segment = progress * (n - 1)
    i = int(segment)
    t = segment - i

    x1, y1 = waypoints[i]
    x2, y2 = waypoints[i + 1]

    x = x1 + (x2 - x1) * t + offset_x
    y = y1 + (y2 - y1) * t
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
        self.path_length = get_path_length(RIVER_CENTER_WAYPOINTS)

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
        super().__init__('organica', speed)
        self.tipo = tipo  # 'tronco' o 'bomba'
        self.es_peligro = True
        self.base_size = DANGER_SIZE
        self.original_image = DANGER_MAP.get(tipo)

        self.current_size = int(self.base_size * 0.4)
        self.image = pygame.transform.scale(self.original_image, (self.current_size, self.current_size))
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

# ===============================
# GATO QUE SE MUEVE SOLO EN X
# ===============================
class CatThrower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_idle = cat_thrower_img
        self.image_throw = pygame.transform.rotate(cat_thrower_img, -8)
        self.image = self.image_idle
        self.throw_timer = 0

        # límites de movimiento horizontal
        self.x_min = 550       # puedes ajustar estos valores si lo quieres más a la izquierda/derecha
        self.x_max = 1000
        self.y = 230           # altura donde va el ovni

        self.speed = 180       # pixeles por segundo
        self.direction = 1     # 1 derecha, -1 izquierda

        start_x = (self.x_min + self.x_max) // 2
        self.rect = self.image.get_rect(midbottom=(start_x, self.y))

    def trigger_throw(self):
        self.throw_timer = 20

    def update(self, dt):
        # animación de lanzamiento
        prev_midbottom = self.rect.midbottom
        if self.throw_timer > 0:
            self.throw_timer -= 1
            next_image = self.image_throw
        else:
            next_image = self.image_idle

        if self.image != next_image:
            self.image = next_image
            self.rect = self.image.get_rect(midbottom=prev_midbottom)

        # movimiento horizontal automático
        self._update_walk(dt)

    def _update_walk(self, dt):
        dx = self.speed * dt * self.direction
        self.rect.x += dx

        # Rebota en los límites
        if self.rect.right >= self.x_max:
            self.rect.right = self.x_max
            self.direction = -1
        elif self.rect.left <= self.x_min:
            self.rect.left = self.x_min
            self.direction = 1

def run_level1(dificultad, idioma, screen):
    global WIDTH, HEIGHT, clock, FPS
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
    else:
        trash_speed = 2.2
        spawn_rate = 120
        danger_spawn_rate = 360
        danger_pool = ['tronco']

    PUNTOS = 25
    TIEMPO_TOTAL = 70
    tiempo_restante = TIEMPO_TOTAL
    METAS = {'reciclable': 4, 'organica': 2, 'inorganico': 2}
    CONTADOR = {'reciclable': 0, 'organica': 0, 'inorganico': 0}
    juego_finalizado = False
    danger_penalty_display = 0  # frames para mostrar alerta

    # Fondo
    try:
        fondo = pygame.image.load("img/rio.png").convert()
        fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
    except pygame.error:
        fondo = pygame.Surface((WIDTH, HEIGHT))
        fondo.fill(BLUE)

    # Tutorial
    resultado_tutorial = tutorial_nivel1.mostrar_tutorial(screen, fondo)
    if resultado_tutorial == "salir_juego":
        return "salir_juego"

    # Sprites
    all_sprites = pygame.sprite.Group()
    trashes = pygame.sprite.Group()
    player = PlayerBar(WIDTH // 2 - 360)
    all_sprites.add(player.botes)
    cat_thrower = CatThrower()
    spawn_timer = 0
    danger_timer = 0

    # Fuentes
    font       = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 26)
    font_tiny  = pygame.font.SysFont(None, 22)
    font_danger = pygame.font.SysFont(None, 24)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Lógica de tiempo y fin de juego
        if not juego_finalizado:
            tiempo_restante -= dt
            if PUNTOS <= 0 or tiempo_restante <= 0:
                PUNTOS = max(PUNTOS, 0)
                tiempo_restante = max(tiempo_restante, 0)
                juego_finalizado = True
            if all(CONTADOR[tipo] >= METAS[tipo] for tipo in METAS):
                juego_finalizado = True

        if danger_penalty_display > 0:
            danger_penalty_display -= 1

        # Eventos
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
            # Movimiento del Jugador
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -8
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 8
            player.move(dx)

            # Aparición de Basura
            spawn_timer += 1
            spawned_this_cycle = False
            if spawn_timer >= spawn_rate:
                tipo = random.choice(TRASH_TYPES)
                t = Trash(tipo, trash_speed)
                all_sprites.add(t)
                trashes.add(t)
                spawn_timer = 0
                spawned_this_cycle = True

            # Aparición de Peligros
            danger_timer += 1
            if danger_timer >= danger_spawn_rate and not spawned_this_cycle:
                danger_type = random.choice(danger_pool)
                d = Peligro(danger_type, trash_speed)
                all_sprites.add(d)
                trashes.add(d)
                danger_timer = 0
                cat_thrower.trigger_throw()

            trashes.update()

            # Colisiones
            for trash in trashes:
                for bin in player.botes:
                    if trash.rect.colliderect(bin.rect):

                        if trash.es_peligro:
                            if trash.tipo == 'tronco':
                                PUNTOS -= 1
                                danger_penalty_display = 60
                                print("¡Peligro! Colisión con Tronco. -1 Punto.")
                            elif trash.tipo == 'bomba':
                                PUNTOS = 0
                                juego_finalizado = True
                                print("¡GAME OVER! Colisión con BOMBA.")
                        elif trash.tipo == bin.tipo and CONTADOR[trash.tipo] < METAS[trash.tipo]:
                            CONTADOR[trash.tipo] += 1
                            print(f"¡Correcto! Recolectaste {trash.tipo}. Meta: {CONTADOR[trash.tipo]}/{METAS[tipo]}")
                        else:
                            PUNTOS -= 1
                            print("¡Error! Clasificación incorrecta. -1 Punto.")

                        trash.kill()
                        break

            # Eliminar basura que se va de la pantalla
            for trash in trashes.copy():
                if trash.rect.top > HEIGHT:
                    trash.kill()

        # DIBUJO
        screen.blit(fondo, (0, 0))
        screen.blit(cat_thrower.image, cat_thrower.rect)
        trashes.draw(screen)
        # Dibujar contorno ajustado a la forma (más preciso) usando la máscara del sprite
        # Colores por tipo: orgánica=verde, reciclable=azul, inorgánico=rojo
        outline_colors = {'organica': DARK_GREEN, 'reciclable': DARK_BLUE, 'inorganico': DARK_RED}
        for trash in trashes:
            try:
                if getattr(trash, 'es_peligro', False):
                    # No outline for peligros (opcional)
                    continue
                col = outline_colors.get(getattr(trash, 'tipo', None), BLACK)
                img = getattr(trash, 'image', None)
                if img is None:
                    continue
                # Create a mask from the sprite surface and get an outline of non-transparent pixels
                mask = pygame.mask.from_surface(img)
                outline = mask.outline()
                if outline and len(outline) >= 3:
                    pts = [(trash.rect.left + x, trash.rect.top + y) for (x, y) in outline]
                    # Draw the polygon outline; use width 3 for visibility
                    pygame.draw.polygon(screen, col, pts, 3)
                else:
                    # Fallback: small rounded rect if outline is not available
                    rect = trash.rect.inflate(6, 6)
                    radius = max(0, min(8, rect.width // 8))
                    pygame.draw.rect(screen, col, rect, 3, border_radius=radius)
            except Exception:
                # Ignore drawing errors to avoid crashing runtime
                pass
        player.draw(screen)

        # ===============================
        # PANEL OBJETIVOS RECOLECCIÓN
        # (arriba a la izquierda)
        # ===============================
        PANEL_WIDTH = 340
        PANEL_HEIGHT = 260
        panel_x = 10            # esquina izquierda
        panel_y = 10            # arriba
        panel_rect = pygame.Rect(panel_x, panel_y, PANEL_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, panel_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, panel_rect, 3, border_radius=10)

        # Franja de título
        header_rect = pygame.Rect(panel_rect.x, panel_rect.y, PANEL_WIDTH, 32)
        pygame.draw.rect(screen, (210, 245, 210), header_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, header_rect, 1, border_radius=10)

        # Título
        titulo_surf = font_small.render(get_text("OBJETIVOS DE RECOLECCIÓN", idioma), True, BLACK)
        titulo_x = panel_rect.x + (PANEL_WIDTH - titulo_surf.get_width()) // 2
        titulo_y = panel_rect.y + 5
        screen.blit(titulo_surf, (titulo_x, titulo_y))

        # Subtítulo (MI PUNTUACIÓN DE RECICLAJE)
        subtitulo_surf = font_tiny.render(get_text("MI PUNTUACIÓN DE RECICLAJE", idioma), True, (50, 50, 50))
        subtitulo_x = panel_rect.x + (PANEL_WIDTH - subtitulo_surf.get_width()) // 2
        subtitulo_y = panel_rect.y + 38
        screen.blit(subtitulo_surf, (subtitulo_x, subtitulo_y))

        # Metas por tipo
        y_off = 70
        for tipo in ['reciclable', 'organica', 'inorganico']:
            color = {'organica':DARK_GREEN,'reciclable':DARK_BLUE,'inorganico':DARK_RED}[tipo]

            label_map = {
                'reciclable': get_text("RECICLABLE", idioma),
                'organica':   get_text("ORGÁNICA", idioma),
                'inorganico': get_text("INORGÁNICA", idioma)
            }
            label_surf = font_small.render(f"[{label_map[tipo]}]", True, color)
            screen.blit(label_surf, (panel_rect.x + 14, panel_rect.y + y_off))

            goal_surf = font_small.render(f"{CONTADOR[tipo]}/{METAS[tipo]}", True, BLACK)
            screen.blit(goal_surf, (panel_rect.right - goal_surf.get_width() - 14, panel_rect.y + y_off))

            barra_x = panel_rect.x + 14
            barra_y = panel_rect.y + y_off + 22
            barra_w = PANEL_WIDTH - 28
            barra_h = 18
            barra_rect = pygame.Rect(barra_x, barra_y, barra_w, barra_h)

            progreso = CONTADOR[tipo] / METAS[tipo] if METAS[tipo] > 0 else 0
            pygame.draw.rect(screen, GRAY, barra_rect, border_radius=4)
            fill_rect = pygame.Rect(barra_x, barra_y, int(barra_w * progreso), barra_h)
            pygame.draw.rect(screen, color, fill_rect, border_radius=4)
            pygame.draw.rect(screen, BLACK, barra_rect, 2, border_radius=4)

            y_off += 60

        # ============================
        # SIMBOLOGÍA (debajo del panel)
        # ============================
        SYM_X = 10
        SYM_Y = panel_rect.bottom + 10   # justo debajo del panel
        SYM_WIDTH = 230
        SYM_GAP = 8
        ROW_HEIGHT = ICON_BOX_SIZE + 16
        NUM_ROWS = 3

        SYM_HEIGHT = 36 + NUM_ROWS * ROW_HEIGHT + (NUM_ROWS - 1) * SYM_GAP
        sym_rect = pygame.Rect(SYM_X, SYM_Y, SYM_WIDTH, SYM_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, sym_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, sym_rect, 2, border_radius=10)

        # Franja título guía
        title_bar_rect = pygame.Rect(sym_rect.x, sym_rect.y, SYM_WIDTH, 26)
        pygame.draw.rect(screen, (200, 230, 255), title_bar_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, title_bar_rect, 1, border_radius=10)

        titulo_sim = font_small.render(get_text("GUÍA DE BASURA", idioma), True, BLACK)
        screen.blit(
            titulo_sim,
            (sym_rect.x + (SYM_WIDTH - titulo_sim.get_width()) // 2, sym_rect.y + 4)
        )

        types = [
            ('organica',   icon_organica,   bin_icon_organica),
            ('reciclable', icon_reciclable, bin_icon_reciclable),
            ('inorganico', icon_inorganico, bin_icon_inorganico)
        ]
        row_y = SYM_Y + 30
        for tipo, icon_img, bin_icon in types:
            row_rect = pygame.Rect(SYM_X + 6, row_y, SYM_WIDTH - 12, ROW_HEIGHT)
            pygame.draw.rect(screen, WHITE, row_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, row_rect, 1, border_radius=8)

            box_rect = pygame.Rect(
                row_rect.x + 6,
                row_rect.y + (ROW_HEIGHT - ICON_BOX_SIZE) // 2,
                ICON_BOX_SIZE,
                ICON_BOX_SIZE
            )
            pygame.draw.rect(screen, WHITE, box_rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, box_rect, 2, border_radius=6)

            img_rect = icon_img.get_rect(center=box_rect.center)
            screen.blit(icon_img, img_rect)

            bin_rect = bin_icon.get_rect()
            bin_rect.bottomright = (box_rect.right - 3, box_rect.bottom - 3)
            screen.blit(bin_icon, bin_rect)

            label_key = {'organica':'ORGÁNICA','reciclable':'RECICLABLE','inorganico':'INORGÁNICA'}[tipo]
            label_text = get_text(label_key, idioma)
            label_s = font_small.render(label_text, True, BLACK)
            text_x = box_rect.right + 8
            text_y = row_rect.y + (ROW_HEIGHT - label_s.get_height()) // 2
            screen.blit(label_s, (text_x, text_y))

            row_y += ROW_HEIGHT + SYM_GAP

        # Indicador de Peligros
        if danger_penalty_display > 0:
            text_alert = get_text("¡PELIGRO! Tronco: -1 PUNTO", idioma)
            alert_surf = font_danger.render(text_alert, True, BLACK)

            alert_w = alert_surf.get_width() + 20
            alert_h = alert_surf.get_height() + 10
            alert_x = (WIDTH // 2) - (alert_w // 2)
            alert_y = 100

            alert_rect = pygame.Rect(alert_x, alert_y, alert_w, alert_h)

            pygame.draw.rect(screen, ACCENT_YELLOW, alert_rect, border_radius=6)
            pygame.draw.rect(screen, DARK_RED, alert_rect, 3, border_radius=6)
            screen.blit(alert_surf, (alert_x + 10, alert_y + 5))

        # HUD Puntos y Tiempo (arriba derecha)
        puntos_surf = font.render(f"{get_text('PUNTOS', idioma)}: {PUNTOS}", True, BLACK)
        puntos_rect = puntos_surf.get_rect(topright=(WIDTH - 20, 20))
        pygame.draw.rect(
            screen, LIGHT_GRAY,
            (puntos_rect.x - 10, puntos_rect.y - 5, puntos_rect.width + 20, puntos_rect.height + 10),
            border_radius=6
        )
        pygame.draw.rect(
            screen, BLACK,
            (puntos_rect.x - 10, puntos_rect.y - 5, puntos_rect.width + 20, puntos_rect.height + 10),
            2, border_radius=6
        )
        screen.blit(puntos_surf, puntos_rect)

        tiempo_surf = font.render(f"{get_text('Tiempo', idioma)}: {int(tiempo_restante)}s", True, BLACK)
        screen.blit(tiempo_surf, (WIDTH - 200, 60))

        barra_x, barra_y, barra_w, barra_h = WIDTH - 300, 95, 280, 25
        pygame.draw.rect(screen, GRAY, (barra_x, barra_y, barra_w, barra_h), border_radius=6)
        tiempo_progreso = tiempo_restante / TIEMPO_TOTAL
        if tiempo_progreso > 0.6:
            color_tiempo = (0, 200, 0)
        elif tiempo_progreso > 0.3:
            color_tiempo = (255, 200, 0)
        else:
            color_tiempo = (200, 0, 0)
        pygame.draw.rect(
            screen,
            color_tiempo,
            (barra_x + 2, barra_y + 2, int((barra_w - 4) * tiempo_progreso), barra_h - 4),
            border_radius=6
        )
        pygame.draw.rect(screen, BLACK, (barra_x, barra_y, barra_w, barra_h), 2, border_radius=6)

        # Finalización
        if juego_finalizado:
            if PUNTOS <= 0 and tiempo_restante > 0:
                accion = mostrar_menu_derrota(screen)
            elif tiempo_restante <= 0 and not all(CONTADOR[tipo] >= METAS[tipo] for tipo in METAS):
                accion = mostrar_menu_derrota(screen)
            else:
                accion = mostrar_menu_victoria(screen, "level1")

            if accion == "siguiente":
                return "siguiente"
            elif accion == "reintentar":
                return "reiniciar"
            elif accion == "salir":
                return "salir_menu"

        pygame.display.flip()
    return "siguiente"

if __name__ == "__main__":
    accion = run_level1("Intermedio", "Español", screen)
    print(f"Resultado: {accion}")
    pygame.quit()
    sys.exit()