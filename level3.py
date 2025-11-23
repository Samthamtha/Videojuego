import pygame
import sys
import random
import math
from pause import mostrar_menu_pausa
from victory_menu import mostrar_menu_victoria, mostrar_menu_derrota

pygame.init()
WIDTH, HEIGHT = 1540, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nivel 3 - Fábrica de Reciclaje (Simulación)")
clock = pygame.time.Clock()
FPS = 60

# CARGA DE IMAGEN DE FONDO 
try:
    BACKGROUND_IMAGE = pygame.image.load("img/fondo_nivel3.png").convert()
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
    USE_BACKGROUND_IMAGE = True
except Exception as e:
    print(f"Advertencia: No se pudo cargar la imagen de fondo: {e}")
    USE_BACKGROUND_IMAGE = False


# COLORES Y FUENTES
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (220, 220, 220)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
BLUE_ORIG = (0, 100, 200)
RED_TRIT = (180, 50, 50)
GREEN_FINAL = (0, 150, 0)
CONVEYOR_COLOR = (120, 120, 120)
OUTPUT_TABLE_COLOR = (0, 150, 200)

font = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 24)

# CONFIGURACIÓN DE POSICIONES Y SPRITES
ITEM_SIZE = 80
CONVEYOR_SPEED = 2.5
TRANSFORM_TIME = 2000
GRIND_TIME = 500
CONVEYOR_HEIGHT = 200
CONVEYOR_TOP_Y = 100
CONVEYOR_GAP = 50
CONVEYOR_BOTTOM_Y = CONVEYOR_TOP_Y + CONVEYOR_HEIGHT + CONVEYOR_GAP
GRINDER_STOP_X = WIDTH - 270
GRINDER_X = WIDTH - 250
GRINDER_WIDTH = 150
GRINDER_HEIGHT = CONVEYOR_HEIGHT + 20
CONVEYOR_BOTTOM_WIDTH = WIDTH // 2
TRANSFORM_STOP_X = WIDTH // 2 - 50
OUTPUT_TABLE_X = 50
OUTPUT_TABLE_Y = CONVEYOR_BOTTOM_Y + CONVEYOR_HEIGHT + 50
OUTPUT_TABLE_WIDTH = WIDTH // 2 + 100
OUTPUT_TABLE_HEIGHT = 150
OUTPUT_ITEM_STACK_OFFSET = 20
TRANSFORM_BOX_X_CENTERED = WIDTH // 2 - 50
TRANSFORM_BOX_W = CONVEYOR_HEIGHT + 20


# CLASE Particle
class Particle:
    def __init__(self, x, y, color):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -2)
        self.lifetime = random.randint(10, 30)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.vy += 0.3

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


# RUTAS DE IMAGENES SEGÚN TUS ARCHIVOS
FILE_MAP = {
    'BOTELLA PET': {
        'orig': "img/botella.png",
        'trit': "img/botella_triturada.png",
        'final': "img/bloques.png"
    },
    'LATA ALUMINIO': {
        'orig': "img/Lata.png",
        'trit': "img/lata_triturada.png",
        'final': "img/Sarten.png"
    },
    'PERIODICO': {
        'orig': "img/periodico.png",
        'trit': "img/periodico_triturado.png",
        'final': "img/Cascara_huevo.png"
    }
}

TRANSFORM_DATA = {
    'BOTELLA PET': {'color_orig': BLUE_ORIG, 'shape_orig': 'rect', 'color_trit': RED_TRIT, 'shape_trit': 'circle', 'nombre_final': "LADRILLOS DE JUGUETE", 'color_final': GREEN_FINAL},
    'LATA ALUMINIO': {'color_orig': (200, 200, 200), 'shape_orig': 'circle', 'color_trit': (100, 100, 100), 'shape_trit': 'rect', 'nombre_final': "SARTÉN RECICLADA", 'color_final': (255, 140, 0)},
    'PERIODICO': {'color_orig': (150, 120, 100), 'shape_orig': 'rect', 'color_trit': (50, 50, 50), 'shape_trit': 'rect', 'nombre_final': "CAJAS DE HUEVO", 'color_final': (180, 180, 100)}
}
TRANSFORM_TYPES = list(TRANSFORM_DATA.keys())


def load_image_safe(path, size=None, fallback_color=(180, 180, 180)):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        w, h = size if size else (ITEM_SIZE, ITEM_SIZE)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(fallback_color)
        try:
            smallf = pygame.font.SysFont(None, 16)
            label = smallf.render(path.split('/')[-1], True, (0, 0, 0))
            s.blit(label, (4, 4))
        except Exception:
            pass
        return s


IMAGES = {}
for tipo in TRANSFORM_TYPES:
    fm = FILE_MAP.get(tipo, {})
    IMAGES[tipo] = load_image_safe(fm.get('orig', ''), (ITEM_SIZE, ITEM_SIZE))
    IMAGES[tipo + '_TRIT'] = load_image_safe(fm.get('trit', ''), (ITEM_SIZE, ITEM_SIZE))
    IMAGES[tipo + '_FINAL_GRANDE'] = load_image_safe(fm.get('final', ''), (ITEM_SIZE * 2, ITEM_SIZE * 2))
    IMAGES[tipo + '_FINAL_PEQUE'] = load_image_safe(fm.get('final', ''), (ITEM_SIZE, ITEM_SIZE))

# CARGAR SONIDOS (si existen)
try:
    pygame.mixer.init()
except Exception:
    pass

def _load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

WARNING_SOUND = _load_sound("sonido/advertencia.mp3")
LASER_SOUND = _load_sound("sonido/laser.mp3")

# Cargar imagen del gato para los rayos
GATO_IMAGE = load_image_safe("img/gato_malo.png", (150, 150))


class Item(pygame.sprite.Sprite):
    def __init__(self, tipo, state, x, y):
        super().__init__()
        self.tipo = tipo
        self.state = state
        self.data = TRANSFORM_DATA.get(tipo, {})
        self.label_orig = font_small.render(self.tipo, True, YELLOW)
        self.label_trit = font_small.render(f"TRIT: {self.tipo}", True, WHITE)
        self.rect = pygame.Rect(x, y, ITEM_SIZE, ITEM_SIZE)
        self.speed = CONVEYOR_SPEED
        self.update_image()

    def update_image(self):
        if self.state == 'ORIG':
            self.image = IMAGES.get(self.tipo, IMAGES.get(self.tipo + '_TRIT', pygame.Surface((ITEM_SIZE, ITEM_SIZE))))
        elif self.state == 'TRIT':
            self.image = IMAGES.get(self.tipo + '_TRIT', IMAGES.get(self.tipo, pygame.Surface((ITEM_SIZE, ITEM_SIZE))))
        elif self.state == 'FINAL':
            self.image = IMAGES.get(self.tipo + '_FINAL_PEQUE', IMAGES.get(self.tipo, pygame.Surface((ITEM_SIZE, ITEM_SIZE))))
        else:
            self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
        self.rect.size = self.image.get_size()

    def update(self, conveyor_dx=0):
        if self.state != 'OUTPUT':
            if self.state in ['ORIG', 'FINAL', 'TRIT']:
                self.rect.x += conveyor_dx
            if self.state == 'ORIG':
                self.rect.y = CONVEYOR_TOP_Y + (CONVEYOR_HEIGHT - ITEM_SIZE) // 2
            elif self.state == 'FINAL':
                self.rect.y = CONVEYOR_BOTTOM_Y + (CONVEYOR_HEIGHT - ITEM_SIZE) // 2
            elif self.state == 'TRIT':
                TRANSFORM_BOX_Y = CONVEYOR_BOTTOM_Y - 10
                TRANSFORM_BOX_H = CONVEYOR_HEIGHT + 20
                self.rect.y = TRANSFORM_BOX_Y + (TRANSFORM_BOX_H - ITEM_SIZE) // 2

    def triturar(self):
        self.state = 'TRIT'
        self.update_image()
        self.rect.x = -ITEM_SIZE * 2

    def transform_to_final(self):
        self.state = 'FINAL'
        self.update_image()


class ConveyorBelt:
    def __init__(self, y, width):
        self.y = y
        self.width = width
        self.height = CONVEYOR_HEIGHT
        self.rect = pygame.Rect(0, self.y, self.width, self.height)
        self.color = CONVEYOR_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        line_color = (150, 150, 150)
        for i in range(0, self.width, 30):
            x = (i + (pygame.time.get_ticks() // 20 % 30)) % self.width
            pygame.draw.line(surface, line_color, (x, self.y + 5), (x, self.y + self.height - 5), 2)


def show_inspection_screen(screen, item):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    box_width = 500
    box_height = 400
    box_rect = pygame.Rect(WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2, box_width, box_height)
    pygame.draw.rect(screen, LIGHT_GRAY, box_rect, 0, 10)
    pygame.draw.rect(screen, BLACK, box_rect, 3, 10)

    text_title = font_large.render("¡OBJETO REVALORIZADO!", True, BLACK)
    screen.blit(text_title, (box_rect.centerx - text_title.get_width() // 2, box_rect.y + 30))

    img_final_grande = IMAGES.get(item.tipo + '_FINAL_GRANDE')
    if img_final_grande:
        img_rect = img_final_grande.get_rect(center=(box_rect.centerx, box_rect.y + 150))
        screen.blit(img_final_grande, img_rect)

    text_name = font_large.render(item.data.get('nombre_final', "OBJETO"), True, item.data.get('color_final', BLACK))
    screen.blit(text_name, (box_rect.centerx - text_name.get_width() // 2, box_rect.bottom - 90))

    text_continue = font.render("Presiona E para continuar...", True, BLACK)
    screen.blit(text_continue, (box_rect.centerx - text_continue.get_width() // 2, box_rect.bottom - 40))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                waiting = False
                return "continuar"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "salir_menu"
    return "continuar"


def draw_button_prompt(screen, text, x, y, key_char=None, pulse=True):
    """Dibuja un botón destacado y atractivo para mostrar qué tecla presionar"""
    # Efecto de pulso
    pulse_offset = 0
    if pulse:
        pulse_offset = int(5 * abs(math.sin(pygame.time.get_ticks() / 200)))
    
    # Fondo del botón con sombra
    button_width = 200
    button_height = 70
    shadow_offset = 4
    
    # Sombra
    shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, button_width, button_height)
    pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, 0, 10)
    
    # Botón principal con gradiente
    button_rect = pygame.Rect(x - pulse_offset//2, y - pulse_offset//2, button_width + pulse_offset, button_height + pulse_offset)
    
    # Gradiente del botón (de amarillo a naranja)
    for i in range(button_rect.height):
        color_ratio = i / button_rect.height
        r = int(255 - color_ratio * 30)
        g = int(200 - color_ratio * 50)
        b = int(0)
        pygame.draw.line(screen, (r, g, b), 
                        (button_rect.x, button_rect.y + i), 
                        (button_rect.x + button_rect.width, button_rect.y + i))
    
    # Borde del botón
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, 10)
    
    # Texto de la tecla si se proporciona
    if key_char:
        key_font = font_large
        key_text = key_font.render(key_char.upper(), True, WHITE)
        key_rect = pygame.Rect(button_rect.x + 10, button_rect.y + 5, 50, 50)
        pygame.draw.rect(screen, (50, 50, 50), key_rect, 0, 5)
        pygame.draw.rect(screen, WHITE, key_rect, 2, 5)
        screen.blit(key_text, (key_rect.centerx - key_text.get_width() // 2, 
                              key_rect.centery - key_text.get_height() // 2))
    
    # Texto de instrucción
    if key_char:
        prompt_text = font_small.render(text, True, WHITE)
        screen.blit(prompt_text, (button_rect.x + 70, button_rect.centery - prompt_text.get_height() // 2))
    else:
        prompt_text = font.render(text, True, WHITE)
        screen.blit(prompt_text, (button_rect.centerx - prompt_text.get_width() // 2, 
                                  button_rect.centery - prompt_text.get_height() // 2))


def run_level3(dificultad=None, idioma=None, screen=screen):
    METAS_TRITURAR = 5
    contador_triturados = 0
    juego_finalizado = False
    current_item = None
    is_grinding = False
    grind_start_time = 0
    is_transforming = False
    transform_start_time = 0
    transform_key = None  # Tecla aleatoria para transformar
    item_inspected = False
    particles = []
    output_items = []
    conveyor_top = ConveyorBelt(CONVEYOR_TOP_Y, WIDTH)
    conveyor_bottom = ConveyorBelt(CONVEYOR_BOTTOM_Y, CONVEYOR_BOTTOM_WIDTH)
    all_items = pygame.sprite.Group()
    spawn_rate = 180
    spawn_timer = 0

    # Controles de cinta: banderas para manejar teclas mantenidas
    moving_left = False
    moving_right = False
    conveyor_dx = 0
    # Variables para advertencia y láser (aleatorio, independiente del jugador)
    warning_active = False
    warning_start_time = 0
    warning_played = False

    laser_active = False
    laser_start_time = 0
    laser_played = False
    # lista de láseres activos; cada uno es dict {'x': int, 'track': 'top'|'bottom'}
    lasers = []
    LASER_WIDTH = 18

    # Ajustes según dificultad
    # valores por defecto (Principiante) - aumentado la frecuencia
    num_lasers = 1
    WARNING_MIN_INTERVAL = 2000
    WARNING_MAX_INTERVAL = 5000
    WARNING_DURATION = 1000
    LASER_DURATION = 350

    if dificultad:
        dif = str(dificultad).lower()
        if 'inter' in dif:  # Intermedio - más frecuente
            num_lasers = 2
            WARNING_MIN_INTERVAL = 1200
            WARNING_MAX_INTERVAL = 2800
            WARNING_DURATION = 700
            LASER_DURATION = 260
            LASER_WIDTH = 16
        elif 'prof' in dif or 'profe' in dif or 'profesional' in dif:  # Profesional - más frecuente aún
            num_lasers = 3
            WARNING_MIN_INTERVAL = 700
            WARNING_MAX_INTERVAL = 1600
            WARNING_DURATION = 500
            LASER_DURATION = 220
            LASER_WIDTH = 12

    # siguiente tiempo aleatorio para la próxima advertencia
    next_warning_time = pygame.time.get_ticks() + random.randint(WARNING_MIN_INTERVAL, WARNING_MAX_INTERVAL)

    # Mensajes burlones cuando el gato golpea con el láser
    mensajes_burlones = [
        "¡JAJAJA! ¡TE ALCANCÉ!",
        "¡MUAHAHA! ¡ERES MUY LENTO!",
        "¡JA JA JA! ¡NO PUEDES ESCAPAR!",
        "¡TE DISTRAIGO! ¡JAJAJA!",
        "¡MIRA AQUÍ! ¡TE GOLPEÉ!",
        "¡NO PODRÁS GANAR! ¡JAJAJA!",
        "¡ERES MUY MALO! ¡MUAHAHA!",
        "¡INTENTA DE NUEVO! ¡JA JA JA!",
        "¡TE ENGAÑÉ! ¡JAJAJA!",
        "¡NO ERES RÁPIDO! ¡MUAHAHA!"
    ]
    
    # Variables para mostrar mensajes burlones
    mensaje_burlon_activo = False
    mensaje_burlon_texto = ""
    mensaje_burlon_start_time = 0
    MENSAJE_BURLON_DURACION = 2000  # 2 segundos

    running = True
    while running:
        clock.tick(FPS)

        if contador_triturados >= METAS_TRITURAR and not juego_finalizado:
            juego_finalizado = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego"

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    moving_left = True
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    moving_right = True

                if event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    accion = mostrar_menu_pausa(screen, HEIGHT, WIDTH)
                    if accion == "salir_juego":
                        return "salir_juego"
                    elif accion == "reiniciar":
                        return "reiniciar"
                    elif accion in ["salir", "salir_menu"]:
                        return "salir_menu"

                if not juego_finalizado and event.key == pygame.K_e and current_item:
                    if current_item.state == 'ORIG' and not is_grinding:
                        if current_item.rect.right >= GRINDER_STOP_X:
                            is_grinding = True
                            grind_start_time = pygame.time.get_ticks()
                            current_item.rect.x = -5000
                            p_color = current_item.data.get('color_orig', (255, 255, 255))
                            p_center_x = GRINDER_X + (GRINDER_WIDTH // 3)
                            p_center_y = CONVEYOR_TOP_Y + CONVEYOR_HEIGHT // 2
                            for _ in range(30):
                                particles.append(Particle(p_center_x + random.randint(-10, 10), p_center_y, p_color))

                # Detectar tecla aleatoria para transformar
                if not juego_finalizado and current_item and current_item.state == 'TRIT' and not is_transforming:
                    if current_item.rect.x >= TRANSFORM_STOP_X - 5 and transform_key:
                        # Mapeo de letras a códigos de teclas de pygame
                        key_map = {
                            'a': pygame.K_a, 'b': pygame.K_b, 'c': pygame.K_c, 'd': pygame.K_d,
                            'e': pygame.K_e, 'f': pygame.K_f, 'g': pygame.K_g, 'h': pygame.K_h,
                            'i': pygame.K_i, 'j': pygame.K_j, 'k': pygame.K_k, 'l': pygame.K_l,
                            'm': pygame.K_m, 'n': pygame.K_n, 'o': pygame.K_o, 'p': pygame.K_p,
                            'q': pygame.K_q, 'r': pygame.K_r, 's': pygame.K_s, 't': pygame.K_t,
                            'u': pygame.K_u, 'v': pygame.K_v, 'w': pygame.K_w, 'x': pygame.K_x,
                            'y': pygame.K_y, 'z': pygame.K_z
                        }
                        # Verificar si se presionó la tecla correcta
                        if transform_key.lower() in key_map and event.key == key_map[transform_key.lower()]:
                            is_transforming = True
                            transform_start_time = pygame.time.get_ticks()
                            transform_key = None  # Limpiar la tecla después de usarla

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    moving_left = False
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    moving_right = False

        # calcular desplazamiento horizontal de la cinta según las banderas
        if moving_left and not moving_right:
            conveyor_dx = -CONVEYOR_SPEED
        elif moving_right and not moving_left:
            conveyor_dx = CONVEYOR_SPEED
        else:
            conveyor_dx = 0

        # Secuencia de advertencia/láser aleatoria (independiente del jugador)
        now = pygame.time.get_ticks()
        if not warning_active and not laser_active and now >= next_warning_time:
            warning_active = True
            warning_start_time = now
            warning_played = False
            # elegir X aleatorias y el carril (top/bottom) para cada láser
            # Limitar las posiciones X para que solo aparezcan dentro de las transportadoras
            lasers = []
            for _ in range(num_lasers):
                track = random.choice(['top', 'bottom'])
                if track == 'top':
                    # Para la cinta superior: desde el inicio hasta donde termina (GRINDER_STOP_X)
                    max_x = GRINDER_STOP_X - LASER_WIDTH // 2
                    min_x = LASER_WIDTH // 2
                else:
                    # Para la cinta inferior: desde el inicio hasta donde termina (CONVEYOR_BOTTOM_WIDTH)
                    max_x = CONVEYOR_BOTTOM_WIDTH - LASER_WIDTH // 2
                    min_x = LASER_WIDTH // 2
                
                # Asegurar que min_x < max_x
                if min_x < max_x:
                    lx = random.randint(min_x, max_x)
                else:
                    lx = (min_x + max_x) // 2
                lasers.append({'x': lx, 'track': track})

        # reproducir sonido de advertencia y pasar al láser tras WARNING_DURATION
        if warning_active:
            if not warning_played and WARNING_SOUND:
                try:
                    WARNING_SOUND.play()
                except Exception:
                    pass
                warning_played = True
            if pygame.time.get_ticks() - warning_start_time >= WARNING_DURATION:
                warning_active = False
                laser_active = True
                laser_start_time = pygame.time.get_ticks()
                laser_played = False

        # manejar láser: reproducir sonido y marcar duración
        if laser_active:
            if not laser_played and LASER_SOUND:
                try:
                    LASER_SOUND.play()
                except Exception:
                    pass
                laser_played = True
            if pygame.time.get_ticks() - laser_start_time >= LASER_DURATION:
                laser_active = False
                # limpiar posiciones y programar siguiente advertencia aleatoria
                lasers_x = []
                next_warning_time = pygame.time.get_ticks() + random.randint(WARNING_MIN_INTERVAL, WARNING_MAX_INTERVAL)
        
        # Manejar duración del mensaje burlón
        if mensaje_burlon_activo:
            if pygame.time.get_ticks() - mensaje_burlon_start_time >= MENSAJE_BURLON_DURACION:
                mensaje_burlon_activo = False

        # (no dependemos del movimiento del jugador para los eventos de láser)

        if not juego_finalizado:
            if not current_item and not is_grinding and not is_transforming and spawn_timer >= spawn_rate:
                tipo = random.choice(TRANSFORM_TYPES)
                new_item = Item(tipo, 'ORIG', -ITEM_SIZE, 0)
                all_items.add(new_item)
                current_item = new_item
                spawn_timer = 0
                item_inspected = False

            spawn_timer += 1

            for item in list(all_items):
                if item.state == 'ORIG':
                    if not is_grinding:
                        # aplicar movimiento siempre y luego clampear a la derecha si corresponde
                        item.update(conveyor_dx)
                        if item.rect.right > GRINDER_STOP_X:
                            item.rect.right = GRINDER_STOP_X
                    if current_item is None:
                        current_item = item

                elif item.state == 'TRIT':
                    if not is_transforming:
                        item.update(conveyor_dx)
                        if item.rect.x > TRANSFORM_STOP_X:
                            item.rect.x = TRANSFORM_BOX_X_CENTERED + (TRANSFORM_BOX_W // 2) - (ITEM_SIZE // 2)
                            # Generar nueva tecla aleatoria cuando el item llega a la posición de transformación
                            if transform_key is None:
                                # Generar letra aleatoria (a-z)
                                transform_key = random.choice('abcdefghijklmnopqrstuvwxyz')
                    else:
                        elapsed_time = pygame.time.get_ticks() - transform_start_time
                        if elapsed_time >= TRANSFORM_TIME:
                            is_transforming = False
                            item.transform_to_final()
                            transform_key = None  # Limpiar la tecla después de transformar

                elif item.state == 'FINAL':
                    if not item_inspected:
                        item.update(conveyor_dx)
                        if item.rect.right >= CONVEYOR_BOTTOM_WIDTH:
                            item.rect.right = CONVEYOR_BOTTOM_WIDTH
                            item_inspected = True
                            accion = show_inspection_screen(screen, item)
                            if accion == "continuar":
                                item.state = 'OUTPUT'
                                item.rect.x = OUTPUT_TABLE_X + 20 + len(output_items) * (ITEM_SIZE + 10)
                                item.rect.y = OUTPUT_TABLE_Y + (OUTPUT_TABLE_HEIGHT - ITEM_SIZE) // 2
                                output_items.append(item)
                                all_items.remove(item)
                                current_item = None
                                item_inspected = False
                            elif accion == "salir_juego":
                                return "salir_juego"
                            elif accion == "salir_menu":
                                return "salir_menu"

                elif item.state == 'OUTPUT':
                    pass

            if is_grinding:
                elapsed_time = pygame.time.get_ticks() - grind_start_time
                if elapsed_time >= GRIND_TIME:
                    is_grinding = False
                    if current_item:
                        current_item.triturar()
                        contador_triturados += 1

            particles = [p for p in particles if p.lifetime > 0]
            for p in particles:
                p.update()

            # --- si el láser está activo, comprobar colisiones y quemar items afectados ---
            if laser_active:
                # láser(es) vertical(es) en las posiciones de `lasers` (pueden ser top o bottom)
                for l in list(lasers):
                    lx = l.get('x')
                    track = l.get('track', 'top')
                    if track == 'top':
                        ly = CONVEYOR_TOP_Y - 5
                    else:
                        ly = CONVEYOR_BOTTOM_Y - 5
                    laser_rect = pygame.Rect(lx - (LASER_WIDTH // 2), ly, LASER_WIDTH, CONVEYOR_HEIGHT + 10)
                    for it in list(all_items):
                        if it.state != 'OUTPUT' and it.rect.colliderect(laser_rect):
                            # el item se quema: vuelve al inicio como 'ORIG'
                            it.state = 'ORIG'
                            it.update_image()
                            it.rect.x = -ITEM_SIZE
                            # si era el item actual, mantenemos la referencia para seguir moviéndolo
                            if current_item is it:
                                current_item = it
                            
                            # Mostrar mensaje burlón aleatorio
                            mensaje_burlon_activo = True
                            mensaje_burlon_texto = random.choice(mensajes_burlones)
                            mensaje_burlon_start_time = pygame.time.get_ticks()

        # DIBUJO
        if USE_BACKGROUND_IMAGE:
            screen.blit(BACKGROUND_IMAGE, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        meta_text = font_large.render(f"OBJETOS TRITURADOS: {contador_triturados}/{METAS_TRITURAR}", True, YELLOW)
        meta_rect = meta_text.get_rect(center=(WIDTH // 2, 50))
        pygame.draw.rect(screen, BLACK, (meta_rect.x - 20, meta_rect.y - 10, meta_rect.width + 40, meta_rect.height + 20), 0, 5)
        screen.blit(meta_text, meta_rect)

        hint_text = font_small.render("Mover cinta: A/D o <- / ->", True, WHITE)
        screen.blit(hint_text, (meta_rect.x, meta_rect.bottom + 8))

        conveyor_top.draw(screen)
        pygame.draw.rect(screen, RED, (GRINDER_X, CONVEYOR_TOP_Y - 5, GRINDER_WIDTH, GRINDER_HEIGHT), 0, 5)
        pygame.draw.circle(screen, BLACK, (GRINDER_X + GRINDER_WIDTH // 2, CONVEYOR_TOP_Y + CONVEYOR_HEIGHT // 2), 30)
        text_triturar = font_small.render("TRITURADORA", True, WHITE)
        screen.blit(text_triturar, (GRINDER_X + 10, CONVEYOR_TOP_Y + CONVEYOR_HEIGHT + 5))

        # Mostrar símbolo de advertencia mientras warning_active (en las X de los láseres)
        if warning_active:
            for l in lasers:
                warn_x = l.get('x')
                track = l.get('track', 'top')
                if track == 'top':
                    warn_cy = CONVEYOR_TOP_Y - 70
                else:
                    warn_cy = CONVEYOR_BOTTOM_Y + CONVEYOR_HEIGHT + 10
                warn_cx = warn_x
                tri = [(warn_cx, warn_cy), (warn_cx - 30, warn_cy + 60), (warn_cx + 30, warn_cy + 60)]
                pygame.draw.polygon(screen, YELLOW, tri)
                ex = font_large.render("!", True, RED)
                screen.blit(ex, (warn_cx - ex.get_width() // 2, warn_cy + 6))
                t = font_small.render("¡LÁSER!", True, WHITE)
                screen.blit(t, (warn_cx - t.get_width() // 2, warn_cy + 70))

        conveyor_bottom.draw(screen)
        TRANSFORM_BOX_X = TRANSFORM_BOX_X_CENTERED - 10
        TRANSFORM_BOX_Y = CONVEYOR_BOTTOM_Y - 10
        TRANSFORM_BOX_SIZE = CONVEYOR_HEIGHT + 20
        TRANSFORM_BOX_W_DRAW = TRANSFORM_BOX_SIZE + 20
        TRANSFORM_BOX_H = TRANSFORM_BOX_SIZE

        pygame.draw.rect(screen, LIGHT_GRAY, (TRANSFORM_BOX_X, TRANSFORM_BOX_Y, TRANSFORM_BOX_W_DRAW, TRANSFORM_BOX_H), 0, 5)

        if current_item and current_item.state == 'TRIT' and current_item.rect.x >= TRANSFORM_STOP_X - 5:
            if not is_transforming:
                # Mostrar botón mejorado con la tecla aleatoria
                if transform_key:
                    button_x = TRANSFORM_BOX_X + (TRANSFORM_BOX_W_DRAW // 2) - 100
                    button_y = TRANSFORM_BOX_Y + TRANSFORM_BOX_H // 2 - 35
                    draw_button_prompt(screen, "Presiona", button_x, button_y, transform_key, pulse=True)
            else:
                time_ratio = (pygame.time.get_ticks() - transform_start_time) / TRANSFORM_TIME
                if time_ratio < 0.5:
                    cover_height_draw = int(time_ratio * 2 * TRANSFORM_BOX_H)
                elif time_ratio >= 0.5 and time_ratio < 0.8:
                    cover_height_draw = TRANSFORM_BOX_H
                else:
                    cover_height_draw = int((1.0 - time_ratio) * 5 * TRANSFORM_BOX_H)
                pygame.draw.rect(screen, BLACK, (TRANSFORM_BOX_X + 10, TRANSFORM_BOX_Y, TRANSFORM_BOX_W, cover_height_draw))

        pygame.draw.rect(screen, OUTPUT_TABLE_COLOR, (OUTPUT_TABLE_X, OUTPUT_TABLE_Y, OUTPUT_TABLE_WIDTH, OUTPUT_TABLE_HEIGHT), 0, 5)

        for item in all_items:
            if item.state == 'TRIT' and is_transforming:
                continue
            screen.blit(item.image, item.rect)

        for item in output_items:
            screen.blit(item.image, item.rect)

        for item in all_items:
            if item.state == 'ORIG':
                screen.blit(item.label_orig, (item.rect.centerx - item.label_orig.get_width() // 2, item.rect.top - item.label_orig.get_height() - 5))
                if item.rect.right == GRINDER_STOP_X and not is_grinding:
                    # Mostrar botón mejorado para triturar
                    button_x = item.rect.centerx - 100
                    button_y = item.rect.top - 120
                    draw_button_prompt(screen, "Triturar", button_x, button_y, "E", pulse=True)
            elif item.state == 'TRIT' and not is_transforming:
                screen.blit(item.label_trit, (item.rect.centerx - item.label_trit.get_width() // 2, item.rect.top - item.label_trit.get_height() - 5))

        for p in particles:
            p.draw(screen)

        # Dibujar rayo láser (vertical) si está activo
        if laser_active:
            laser_h = CONVEYOR_HEIGHT + 10
            laser_surf = pygame.Surface((LASER_WIDTH, laser_h), pygame.SRCALPHA)
            laser_surf.fill((255, 0, 0, 160))
            for l in lasers:
                lx = l.get('x')
                track = l.get('track', 'top')
                if track == 'top':
                    ly = CONVEYOR_TOP_Y - 5
                else:
                    ly = CONVEYOR_BOTTOM_Y - 5
                screen.blit(laser_surf, (lx - (LASER_WIDTH // 2), ly))
                
                # Dibujar el gato lanzando los rayos
                if GATO_IMAGE:
                    # Posicionar el gato arriba del láser
                    gato_x = lx - GATO_IMAGE.get_width() // 2
                    if track == 'top':
                        gato_y = CONVEYOR_TOP_Y - GATO_IMAGE.get_height() - 20
                    else:
                        gato_y = CONVEYOR_BOTTOM_Y - GATO_IMAGE.get_height() - 20
                    screen.blit(GATO_IMAGE, (gato_x, gato_y))
        
        # Dibujar mensaje burlón si está activo
        if mensaje_burlon_activo:
            # Crear un fondo semitransparente para el mensaje
            mensaje_surf = font_large.render(mensaje_burlon_texto, True, RED)
            mensaje_rect = mensaje_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            # Fondo con borde usando superficie con alpha
            bg_rect = pygame.Rect(mensaje_rect.x - 20, mensaje_rect.y - 15, 
                                 mensaje_rect.width + 40, mensaje_rect.height + 30)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, 200), (0, 0, bg_rect.width, bg_rect.height), 0, 10)
            pygame.draw.rect(bg_surf, (255, 0, 0, 255), (0, 0, bg_rect.width, bg_rect.height), 3, 10)
            screen.blit(bg_surf, bg_rect)
            
            # Efecto de parpadeo
            elapsed = pygame.time.get_ticks() - mensaje_burlon_start_time
            alpha = int(255 * (0.7 + 0.3 * abs(math.sin(elapsed / 150))))
            mensaje_surf.set_alpha(alpha)
            screen.blit(mensaje_surf, mensaje_rect)

        pygame.display.flip()

        # Manejo de finalización
        if juego_finalizado:
            accion = mostrar_menu_victoria(screen, "level3")
            if accion == "siguiente":
                return "siguiente"
            elif accion == "reintentar":
                return "reiniciar"
            elif accion == "salir":
                return "salir_menu"

    return "siguiente"


if __name__ == '__main__':
    accion = "iniciar"
    if 'screen' not in locals():
        pygame.init()
        WIDTH, HEIGHT = 1540, 800
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

    while accion not in ["salir_juego", "salir_menu"]:
        if accion == "iniciar" or accion == "reiniciar":
            accion = run_level3(screen=screen)
    pygame.quit()
    sys.exit()
    # end main
