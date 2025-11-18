# tutorial_nivel1.py
import pygame
import random
import math
import wave
import struct
import os

# Crear blip WAV simple si no existe (sin numpy)
def crear_blip_wav(path='blip.wav', frecuencia=880, duracion=0.04, volumen=0.2, sample_rate=44100):
    if os.path.exists(path):
        return path
    n_samples = int(sample_rate * duracion)
    amplitude = int(32767 * volumen)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(amplitude * math.sin(2.0 * math.pi * frecuencia * t))
            wf.writeframes(struct.pack('<h', val))
    return path

# inicializar mixer si no está
if not pygame.mixer.get_init():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
    except Exception:
        # intentar sin especificar parámetros
        pygame.mixer.init()

# crear y cargar blip
BLIP_PATH = crear_blip_wav()
try:
    blip_sound = pygame.mixer.Sound(BLIP_PATH)
except Exception:
    blip_sound = None

# --- Clases para objetos que caen ---
class FallingObject(pygame.sprite.Sprite):
    def __init__(self, img_path, x_range, y_start=-50, speed=200):
        super().__init__()
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except Exception:
            self.image = pygame.Surface((60,60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (180,50,50), self.image.get_rect())
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(max(0, x_range[0]), min(x_range[1], 2000))
        self.rect.y = y_start
        self.speed = speed

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > 2000:
            self.kill()

# --- Wrap de texto (divide por palabras) ---
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current = ''
    for w in words:
        test = (current + ' ' + w).strip() if current else w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# --- Función del tutorial ---
def mostrar_tutorial(screen, fondo_nivel, metas=None):
    """Muestra el tutorial. Devuelve True si termina normalmente,
       devuelve 'salir_juego' si el usuario cierra la ventana."""
    WIDTH, HEIGHT = screen.get_size()
    clock = pygame.time.Clock()
    FPS = 60

    # Cargar imágenes del perrito (fallback si falla)
    pibble_imgs = []
    for i in range(1, 4):
        try:
            img = pygame.image.load(f"img/pibble_talk{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (150, 150))
        except Exception:
            img = pygame.Surface((150,150), pygame.SRCALPHA)
            pygame.draw.ellipse(img, (200,200,200), img.get_rect())
        pibble_imgs.append(img)

    # teclas de dirección (fallback)
    teclado_imgs = []
    KEY_IMG_SIZE = (100, 100)
    for path in ("img/teclado_izquierda.png","img/teclado1.png","img/teclado_derecha.png"):
        try:
            t = pygame.image.load(path).convert_alpha()
            t = pygame.transform.scale(t, KEY_IMG_SIZE)
        except Exception:
            t = pygame.Surface(KEY_IMG_SIZE, pygame.SRCALPHA)
            pygame.draw.rect(t,(200,200,200), t.get_rect())
        teclado_imgs.append(t)

    falling_group = pygame.sprite.Group()

    dialogos = [
        {"text": "PIBBLE (Perrito): ¡Guau, guau! ¡Al fin llegaste! Soy Pibble, el Guardián de la Galaxia Patitas, y he viajado por el espacio-tiempo hasta tu planeta.", "falling": None, "show_keys": False},
        {"text": "Vine por una misión crítica: ¡detener a ese gato malvado, el Doctor Maullido! Está llenando tu mundo de basura y contaminación para que el planeta se extinga lentamente.", "falling": None, "show_keys": False},
        {"text": "¡El río es nuestra primera prueba! ¡Tenemos que cruzarlo para avanzar a la siguiente etapa y detener su avance!", "falling": None, "show_keys": False},
        {"text": "PIBBLE (Perrito): ¡Primero lo primero! Para movernos solo usa las flechas de dirección, izquierda y derecha en tu teclado.", "falling": None, "show_keys": True},
        {"text": "Nuestro objetivo aquí es muy importante: ¡tenemos que recolectar 10 objetos clave antes de que se acabe el tiempo!", "falling": None, "show_keys": False},
        {"text": "¡Cuidado! El Doctor Maullido está lanzando su basura alienígena. Hay que saber qué tomar y qué no.", "falling": "basura", "show_keys": False},
        {"text": "¡ERROR ES CASTIGO! Si agarras algo que no es un objeto clave, ¡pierdes 1 punto! Solo recolecta lo que piden.", "falling": "basura", "show_keys": False},
        {"text": "TRONCOS: Chocar con un tronco es muy molesto y te hace perder 2 puntos. ¡Esquívalos!", "falling": "tronco", "show_keys": False},
        {"text": "¡Las Bombas!: ¡Estas son la peor amenaza! Mantente lejos!", "falling": "bomba", "show_keys": False},
        {"text": "TIEMPO: ¡Tenemos poco tiempo! Si el reloj llega a cero, el Doctor Maullido escapa.", "falling": None, "show_keys": False},
        {"text": "¡Concéntrate! Eres la última esperanza de este planeta. ¡Vamos a cruzar el río!", "falling": None, "show_keys": False},
    ]

    font = pygame.font.SysFont(None, 28)
    enter_text = font.render("Presiona ENTER para continuar...", True, (0, 0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0,0,0))
    overlay.set_alpha(150)

    dialog_index = 0
    # letra_index cuenta caracteres mostrados (incluye espacios)
    letra_index = 0

    # Precompute line-wrapped arrays for current dialog when needed
    current_lines = []
    total_chars = 0

    def prepare_dialog(dlg):
        nonlocal current_lines, total_chars, letra_index
        current_lines = wrap_text(dlg["text"], font, text_panel_rect.width - 20)
        # total chars counting lines concatenated with single spaces (to approximate positions)
        total_chars = sum(len(l) for l in current_lines)
        letra_index = 0

    # Pre-create text rect
    text_panel_rect = pygame.Rect(50, HEIGHT - 180, WIDTH - 220, 130)
    skip_button_rect = pygame.Rect(WIDTH - 180, 25, 140, 50)

    # Initialize first dialog lines
    if dialogos:
        prepare_dialog(dialogos[0])

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Si texto no está completo: mostrar todo
                    if letra_index < total_chars:
                        letra_index = total_chars
                    else:
                        # avanzar al siguiente diálogo
                        dialog_index += 1
                        falling_group.empty()
                        if dialog_index >= len(dialogos):
                            running = False
                        else:
                            prepare_dialog(dialogos[dialog_index])
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if skip_button_rect.collidepoint(event.pos):
                    return True

        # Draw background + overlay
        try:
            screen.blit(fondo_nivel, (0,0))
        except Exception:
            screen.fill((40,40,100))
        screen.blit(overlay, (0,0))

        # Animación perrito
        img_idx = (pygame.time.get_ticks() // 300) % len(pibble_imgs)
        pibble_rect = pibble_imgs[img_idx].get_rect(bottomright=(WIDTH-30, HEIGHT-30))
        screen.blit(pibble_imgs[img_idx], pibble_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Dialogue box
        pygame.draw.rect(screen, (255,255,255), text_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (0,0,0), text_panel_rect, 3, border_radius=8)

        # Skip button
        button_color = (255, 215, 0) if skip_button_rect.collidepoint(mouse_pos) else (240, 240, 240)
        pygame.draw.rect(screen, button_color, skip_button_rect, border_radius=10)
        pygame.draw.rect(screen, (0,0,0), skip_button_rect, 3, border_radius=10)
        skip_font = pygame.font.SysFont(None, 32)
        skip_text = skip_font.render("SALTAR", True, (0,0,0))
        text_pos = skip_text.get_rect(center=skip_button_rect.center)
        screen.blit(skip_text, text_pos)

        # If dialog valid, spawn falling objects and show keys
        if dialog_index < len(dialogos):
            dlg = dialogos[dialog_index]
            # spawn falling objects probabilistic
            if dlg["falling"] == "tronco" and random.random() < 0.02:
                falling_group.add(FallingObject("img/tronco.png", (50, WIDTH-100), speed=300))
            elif dlg["falling"] == "bomba" and random.random() < 0.02:
                falling_group.add(FallingObject("img/bomba.png", (50, WIDTH-100), speed=300))
            elif dlg["falling"] == "basura" and random.random() < 0.02:
                basura_tipo = random.choice(["img/Cascara.png","img/Lata.png","img/botella.png"])
                falling_group.add(FallingObject(basura_tipo, (50, WIDTH-100), speed=200))

            if dlg["show_keys"]:
                base_x = 150
                spacing = 120
                y_pos = HEIGHT - 310
                for i, key_img in enumerate(teclado_imgs):
                    screen.blit(key_img, (base_x + i*spacing, y_pos))

        # letra por letra: incrementar a ritmo constante (no por frame)
        if dialog_index < len(dialogos) and letra_index < total_chars:
            # velocidad de caracteres por segundo
            cps = 45  # ajustar velocidad
            letra_index += max(1, int(cps * dt))
            # reproducir blip por cada bloque de caracteres avanzados (simple)
            if blip_sound:
                blip_sound.play()

        # Construir texto parcial según letra_index y lines
        shown_lines = []
        chars_left = letra_index
        for line in current_lines:
            if chars_left >= len(line):
                shown_lines.append(line)
                chars_left -= len(line)
            else:
                shown_lines.append(line[:chars_left])
                break

        # Dibujar líneas
        y_off = 10
        for ln in shown_lines:
            surf = font.render(ln, True, (0,0,0))
            screen.blit(surf, (text_panel_rect.x + 10, text_panel_rect.y + y_off))
            y_off += surf.get_height() + 3

        # ENTER text
        screen.blit(enter_text, (text_panel_rect.right - enter_text.get_width() - 10,
                                 text_panel_rect.bottom - enter_text.get_height() - 10))

        # Update & draw falling objects
        falling_group.update(dt)
        falling_group.draw(screen)

        pygame.display.flip()

    # Fin del tutorial: devolver True para que el nivel continúe
    return True
