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
    # --- Load assets for the controls animation ---
    KEY_IMG_SIZE = (260, 260)
    try:
        key_left = pygame.transform.scale(pygame.image.load("img/teclado_izquierda.png").convert_alpha(), KEY_IMG_SIZE)
    except Exception:
        key_left = pygame.Surface(KEY_IMG_SIZE, pygame.SRCALPHA); pygame.draw.rect(key_left, (200,200,200), key_left.get_rect())
    try:
        key_center = pygame.transform.scale(pygame.image.load("img/teclado1.png").convert_alpha(), KEY_IMG_SIZE)
    except Exception:
        key_center = pygame.Surface(KEY_IMG_SIZE, pygame.SRCALPHA); pygame.draw.rect(key_center, (200,200,200), key_center.get_rect())
    try:
        key_right = pygame.transform.scale(pygame.image.load("img/teclado_derecha.png").convert_alpha(), KEY_IMG_SIZE)
    except Exception:
        key_right = pygame.Surface(KEY_IMG_SIZE, pygame.SRCALPHA); pygame.draw.rect(key_right, (200,200,200), key_right.get_rect())

    # Trash/bin image under the keys
    try:
        bin_img = pygame.image.load("img/boteVerde.png").convert_alpha()
        bin_img = pygame.transform.scale(bin_img, (200, 200))
    except Exception:
        bin_img = pygame.Surface((96,96), pygame.SRCALPHA); pygame.draw.rect(bin_img, (0,150,0), bin_img.get_rect())

    # Overlay and UI elements
    overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.fill((0,0,0)); overlay.set_alpha(160)
    # Kid-friendly fonts: prefer Comic Sans, fallback to default
    try:
        title_font = pygame.font.SysFont('Comic Sans MS', 96, bold=True)
    except Exception:
        title_font = pygame.font.SysFont(None, 96, True)
    try:
        instr_font = pygame.font.SysFont('Comic Sans MS', 44)
    except Exception:
        instr_font = pygame.font.SysFont(None, 44)
    try:
        skip_font = pygame.font.SysFont('Comic Sans MS', 36, bold=True)
    except Exception:
        skip_font = pygame.font.SysFont(None, 36, True)
    small_font = pygame.font.SysFont(None, 30)

    # Pre-render title + instruction with a soft shadow for a playful look
    TITLE_TEXT = "CONTROLES"
    title_shadow = title_font.render(TITLE_TEXT, True, (40, 40, 40))
    title_surf = title_font.render(TITLE_TEXT, True, (255, 230, 80))
    INSTR_TEXT = "Usa estos botones para arrastrar la basura"
    instr_shadow = instr_font.render(INSTR_TEXT, True, (30, 30, 30))
    instr_surf = instr_font.render(INSTR_TEXT, True, (255, 220, 60))
    skip_button_rect = pygame.Rect(WIDTH - 200, 22, 160, 56)

    # Sequence: center -> left hold -> right hold (seconds)
    seq = [('center', 0.6), ('left', 1.2), ('right', 1.2)]
    cycles = 3
    current_cycle = 0
    step_index = 0
    step_time = 0.0

    # Positions and spacing
    SPACING = 100
    # center the block of 3 keys (left, center, right) with spacing
    total_keys_w = 3 * KEY_IMG_SIZE[0] + 2 * SPACING
    start_x = WIDTH // 2 - total_keys_w // 2
    keys_x = start_x
    keys_y = HEIGHT // 2 - 120
    bin_y = keys_y + KEY_IMG_SIZE[1] + 50
    bin_x = WIDTH // 2 - bin_img.get_width() // 2
    bin_target_x = bin_x

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir_juego"
            if event.type == pygame.KEYDOWN:
                # ENTER ends the tutorial immediately
                if event.key == pygame.K_RETURN:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if skip_button_rect.collidepoint(event.pos):
                    return True

        # Update step timer
        step_time += dt
        cur_name, cur_dur = seq[step_index]
        if step_time >= cur_dur:
            step_time = 0.0
            step_index += 1
            # play blip when advancing step
            try:
                if blip_sound:
                    blip_sound.play()
            except Exception:
                pass
            if step_index >= len(seq):
                step_index = 0
                current_cycle += 1
                if current_cycle >= cycles:
                    # finished cycles — tutorial complete
                    return True

        # Determine which key to show pressed and bin target
        cur_name, cur_dur = seq[step_index]
        show_left = (cur_name == 'left')
        show_right = (cur_name == 'right')

        if show_left:
            bin_target_x = WIDTH // 2 - 220
        elif show_right:
            bin_target_x = WIDTH // 2 + 80
        else:
            bin_target_x = WIDTH // 2 - bin_img.get_width() // 2

        # Smoothly move bin toward target
        bin_x += (bin_target_x - bin_x) * min(1.0, dt * 8.0)

        # Draw background + overlay
        try:
            screen.blit(fondo_nivel, (0,0))
        except Exception:
            screen.fill((40,40,100))
        screen.blit(overlay, (0,0))

        # Title at top center (shadow + main)
        title_x = WIDTH//2 - title_surf.get_width()//2
        title_y = 36
        screen.blit(title_shadow, (title_x + 4, title_y + 4))
        screen.blit(title_surf, (title_x, title_y))
        # Instruction text below title (shadow + main)
        instr_x = WIDTH//2 - instr_surf.get_width()//2
        instr_y = title_y + title_surf.get_height() + 12
        screen.blit(instr_shadow, (instr_x + 3, instr_y + 3))
        screen.blit(instr_surf, (instr_x, instr_y))

        # Draw keys: left, center, right positions using SPACING
        left_pos = (keys_x, keys_y)
        center_pos = (keys_x + KEY_IMG_SIZE[0] + SPACING, keys_y)
        right_pos = (keys_x + 2*(KEY_IMG_SIZE[0] + SPACING), keys_y)

        # Center key
        screen.blit(key_center, center_pos)

        # Left key (pressed or neutral)
        if show_left:
            screen.blit(key_left, left_pos)
        else:
            screen.blit(key_center, left_pos)

        # Right key (pressed or neutral)
        if show_right:
            screen.blit(key_right, right_pos)
        else:
            screen.blit(key_center, right_pos)

        # Draw bin under keys and move it
        screen.blit(bin_img, (int(bin_x), bin_y))

        # Skip button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (255, 215, 0) if skip_button_rect.collidepoint(mouse_pos) else (240, 240, 240)
        pygame.draw.rect(screen, button_color, skip_button_rect, border_radius=12)
        pygame.draw.rect(screen, (0,0,0), skip_button_rect, 4, border_radius=12)
        skip_text = skip_font.render("SALTAR", True, (0,0,0))
        text_pos = skip_text.get_rect(center=skip_button_rect.center)
        screen.blit(skip_text, text_pos)

        # Small hint under keys
        hint = small_font.render("Usa ← y → para mover el bote", True, (255,255,255))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, bin_y + bin_img.get_height() + 12))

        pygame.display.flip()

    return True
