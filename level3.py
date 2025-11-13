import pygame
import sys
import random
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
except pygame.error as e:
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

# FUNCIONES DE IMÁGENES Y DATOS
def create_item_sprite(color, size, shape='rect'):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    if shape == 'rect':
        pygame.draw.rect(surface, color, (0, 0, size, size), 0, 5)
    elif shape == 'circle':
        pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)
    return surface

def create_large_final_sprite(color, name):
    size = int(ITEM_SIZE * 2.0)
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, (0, 0, size, size), 0, 10)
    text_surface = font_small.render(name.split(' ')[0], True, BLACK)
    surface.blit(text_surface, (size // 2 - text_surface.get_width() // 2, size // 2 - text_surface.get_height() // 2))
    return surface

TRANSFORM_DATA = {
    'BOTELLA PET': { 'color_orig': BLUE_ORIG, 'shape_orig': 'rect', 'color_trit': RED_TRIT, 'shape_trit': 'circle', 'nombre_final': "LADRILLOS DE JUGUETE", 'color_final': GREEN_FINAL },
    'LATA ALUMINIO': { 'color_orig': (200, 200, 200), 'shape_orig': 'circle', 'color_trit': (100, 100, 100), 'shape_trit': 'rect', 'nombre_final': "SARTÉN RECICLADA", 'color_final': (255, 140, 0) },
    'PERIODICO': { 'color_orig': (150, 120, 100), 'shape_orig': 'rect', 'color_trit': (50, 50, 50), 'shape_trit': 'rect', 'nombre_final': "CAJAS DE HUEVO", 'color_final': (180, 180, 100) }
}
TRANSFORM_TYPES = list(TRANSFORM_DATA.keys())

IMAGES = {}
for name, data in TRANSFORM_DATA.items():
    IMAGES[name] = create_item_sprite(data['color_orig'], ITEM_SIZE, data['shape_orig'])
    IMAGES[name + '_TRIT'] = create_item_sprite(data['color_trit'], ITEM_SIZE, data['shape_trit'])
    IMAGES[name + '_FINAL_GRANDE'] = create_large_final_sprite(data['color_final'], data['nombre_final'])
    IMAGES[name + '_FINAL_PEQUE'] = create_item_sprite(data['color_final'], ITEM_SIZE, 'rect')

# CLASES Item y ConveyorBelt 
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
            self.image = IMAGES[self.tipo]
        elif self.state == 'TRIT':
            self.image = IMAGES[self.tipo + '_TRIT']
        elif self.state == 'FINAL':
            self.image = IMAGES[self.tipo + '_FINAL_PEQUE']
        self.rect.size = self.image.get_size()

    def update(self, direction='right'):
        if self.state != 'OUTPUT':
            if self.state in ['ORIG', 'FINAL']:
                self.rect.x += self.speed
            if self.state == 'ORIG':
                self.rect.y = CONVEYOR_TOP_Y + (CONVEYOR_HEIGHT - ITEM_SIZE) // 2
            elif self.state == 'FINAL':
                self.rect.y = CONVEYOR_BOTTOM_Y + (CONVEYOR_HEIGHT - ITEM_SIZE) // 2
            elif self.state == 'TRIT':
                self.rect.x += self.speed
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

# Función de Inspección y Mensaje
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

    img_final_grande = IMAGES[item.tipo + '_FINAL_GRANDE']
    img_rect = img_final_grande.get_rect(center=(box_rect.centerx, box_rect.y + 150))
    screen.blit(img_final_grande, img_rect)

    text_name = font_large.render(item.data['nombre_final'], True, item.data['color_final'])
    screen.blit(text_name, (box_rect.centerx - text_name.get_width() // 2, img_rect.bottom + 20))

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

# Función Principal del Nivel 3
def run_level3(dificultad=None, idioma=None, screen=screen):
    METAS_TRITURAR = 5
    contador_triturados = 0
    juego_finalizado = False
    current_item = None
    is_grinding = False
    grind_start_time = 0
    is_transforming = False
    transform_start_time = 0
    item_inspected = False
    particles = []
    output_items = []
    conveyor_top = ConveyorBelt(CONVEYOR_TOP_Y, WIDTH)
    conveyor_bottom = ConveyorBelt(CONVEYOR_BOTTOM_Y, CONVEYOR_BOTTOM_WIDTH)
    all_items = pygame.sprite.Group()
    spawn_rate = 180
    spawn_timer = 0

    running = True
    while running:
        clock.tick(FPS)

        if contador_triturados >= METAS_TRITURAR and not juego_finalizado:
            juego_finalizado = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego"

            elif event.type == pygame.KEYDOWN:
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
                            p_color = current_item.data['color_orig']
                            p_center_x = GRINDER_X + (GRINDER_WIDTH // 3)
                            p_center_y = CONVEYOR_TOP_Y + CONVEYOR_HEIGHT // 2
                            for _ in range(30):
                                particles.append(Particle(p_center_x + random.randint(-10, 10), p_center_y, p_color))

                    elif current_item.state == 'TRIT' and not is_transforming:
                        if current_item.rect.x >= TRANSFORM_STOP_X - 5:
                            is_transforming = True
                            transform_start_time = pygame.time.get_ticks()

        if not juego_finalizado:
            if not current_item and not is_grinding and not is_transforming and spawn_timer >= spawn_rate:
                tipo = random.choice(TRANSFORM_TYPES)
                new_item = Item(tipo, 'ORIG', -ITEM_SIZE, 0)
                all_items.add(new_item)
                current_item = new_item
                spawn_timer = 0
                item_inspected = False

            spawn_timer += 1

            for item in all_items:
                if item.state == 'ORIG':
                    if not is_grinding:
                        if item.rect.right < GRINDER_STOP_X:
                            item.update()
                        else:
                            item.rect.right = GRINDER_STOP_X
                elif item.state == 'TRIT':
                    if not is_transforming:
                        if item.rect.x < TRANSFORM_STOP_X:
                            item.update()
                        else:
                            item.rect.x = TRANSFORM_BOX_X_CENTERED + (TRANSFORM_BOX_W // 2) - (ITEM_SIZE // 2)
                    elif is_transforming:
                        elapsed_time = pygame.time.get_ticks() - transform_start_time
                        if elapsed_time >= TRANSFORM_TIME:
                            is_transforming = False
                            item.transform_to_final()

                elif item.state == 'FINAL':
                    if not item_inspected:
                        item.update()
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
                    current_item.triturar()
                    contador_triturados += 1

            particles = [p for p in particles if p.lifetime > 0]
            for p in particles:
                p.update()

        # DIBUJO
        if USE_BACKGROUND_IMAGE:
            screen.blit(BACKGROUND_IMAGE, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        meta_text = font_large.render(f"OBJETOS TRITURADOS: {contador_triturados}/{METAS_TRITURAR}", True, YELLOW)
        meta_rect = meta_text.get_rect(center=(WIDTH // 2, 50))
        pygame.draw.rect(screen, BLACK, (meta_rect.x - 20, meta_rect.y - 10, meta_rect.width + 40, meta_rect.height + 20), 0, 5)
        screen.blit(meta_text, meta_rect)
        
        conveyor_top.draw(screen)
        pygame.draw.rect(screen, RED, (GRINDER_X, CONVEYOR_TOP_Y - 5, GRINDER_WIDTH, GRINDER_HEIGHT), 0, 5)
        pygame.draw.circle(screen, BLACK, (GRINDER_X + GRINDER_WIDTH // 2, CONVEYOR_TOP_Y + CONVEYOR_HEIGHT // 2), 30)
        text_triturar = font_small.render("TRITURADORA", True, WHITE)
        screen.blit(text_triturar, (GRINDER_X + 10, CONVEYOR_TOP_Y + CONVEYOR_HEIGHT + 5))
        
        conveyor_bottom.draw(screen)
        TRANSFORM_BOX_X = TRANSFORM_BOX_X_CENTERED - 10
        TRANSFORM_BOX_Y = CONVEYOR_BOTTOM_Y - 10
        TRANSFORM_BOX_SIZE = CONVEYOR_HEIGHT + 20
        TRANSFORM_BOX_W_DRAW = TRANSFORM_BOX_SIZE + 20
        TRANSFORM_BOX_H = TRANSFORM_BOX_SIZE

        pygame.draw.rect(screen, LIGHT_GRAY, (TRANSFORM_BOX_X, TRANSFORM_BOX_Y, TRANSFORM_BOX_W_DRAW, TRANSFORM_BOX_H), 0, 5)

        if current_item and current_item.state == 'TRIT' and current_item.rect.x >= TRANSFORM_STOP_X - 5:
            if not is_transforming:
                text_hold = font.render("Presiona E", True, BLACK)
                screen.blit(text_hold, (TRANSFORM_BOX_X + 20, TRANSFORM_BOX_Y + TRANSFORM_BOX_H // 2 - text_hold.get_height() // 2))
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
                    text_action = font_large.render("Presiona E para Triturar", True, YELLOW)
                    screen.blit(text_action, (item.rect.centerx - text_action.get_width() // 2, item.rect.top - 100))
            elif item.state == 'TRIT' and not is_transforming:
                screen.blit(item.label_trit, (item.rect.centerx - item.label_trit.get_width() // 2, item.rect.top - item.label_trit.get_height() - 5))

        for p in particles:
            p.draw(screen)

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