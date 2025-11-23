import pygame
import os
import math
import wave
import struct
import random


def crear_blip_wav(path='blip.wav', frecuencia=880, duracion=0.04, volumen=0.2, sample_rate=44100):
    if os.path.exists(path):
        return path
    n_samples = int(sample_rate * duracion)
    amplitude = int(32767 * volumen)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(amplitude * math.sin(2.0 * math.pi * frecuencia * t))
            wf.writeframes(struct.pack('<h', val))
    return path


# ensure mixer
if not pygame.mixer.get_init():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
    except Exception:
        pygame.mixer.init()


BLIP_PATH = crear_blip_wav()
try:
    blip_sound = pygame.mixer.Sound(BLIP_PATH)
except Exception:
    blip_sound = None


def _load_img_safe(path, size=None):
    try:
        surf = pygame.image.load(path).convert_alpha()
        if size:
            surf = pygame.transform.scale(surf, size)
        return surf
    except Exception:
        # fallback: simple key with arrow drawn
        w, h = size if size else (120, 120)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (240,240,240), s.get_rect(), border_radius=8)
        pygame.draw.rect(s, (200,200,200), s.get_rect(), 6, border_radius=8)
        return s


def mostrar_tutorial_nivel2(screen, fondo_nivel=None):
    """Muestra tutorial para el nivel 2 (flechas). Devuelve True si termina, 'salir_juego' si cierra."""
    WIDTH, HEIGHT = screen.get_size()
    clock = pygame.time.Clock()
    FPS = 60

    # key images size (larger for clearer display)
    KEY_SIZE = (260, 260)
    # Use the exact filenames provided by the user
    key_up = _load_img_safe('img/teclado_arriba.png', KEY_SIZE)
    key_down = _load_img_safe('img/teclado_abajo.png', KEY_SIZE)
    key_left = _load_img_safe('img/teclado_izquierda.png', KEY_SIZE)
    key_right = _load_img_safe('img/teclado_derecha.png', KEY_SIZE)
    # center image for teclado1
    key_center = _load_img_safe('img/teclado1.png', KEY_SIZE)
    # prepare the single-image animation sequence (names -> surfaces)
    name_to_img = {
        'center': key_center,
        'right': key_right,
        'down': key_down,
        'left': key_left,
        'up': key_up,
    }
    seq = ['center', 'right', 'down', 'left', 'up']
    seq_dur = 0.9
    step_index = 0
    step_time = 0.0

    # overlay and fonts
    overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.fill((0,0,0)); overlay.set_alpha(160)
    try:
        title_font = pygame.font.SysFont('Comic Sans MS', 92, bold=True)
    except Exception:
        title_font = pygame.font.SysFont(None, 92, True)
    try:
        instr_font = pygame.font.SysFont('Comic Sans MS', 42)
    except Exception:
        instr_font = pygame.font.SysFont(None, 42)
    small_font = pygame.font.SysFont(None, 28)

    TITLE_TEXT = 'CONTROLES'
    title_shadow = title_font.render(TITLE_TEXT, True, (30,30,30))
    title_surf = title_font.render(TITLE_TEXT, True, (255,230,80))
    INSTR_TEXT = 'Usa las flechas para seleccionar la herramienta correcta'
    instr_shadow = instr_font.render(INSTR_TEXT, True, (30,30,30))
    instr_surf = instr_font.render(INSTR_TEXT, True, (255,220,60))

    skip_button_rect = pygame.Rect(WIDTH - 200, 22, 160, 56)

    # layout: place the keyboard animation on the LEFT side
    SPACING = 30
    # position the keyboard animation much closer to the left edge
    left_margin = 2
    keys_x = left_margin
    keys_y_mid = HEIGHT // 2 - KEY_SIZE[1]//2
    # center column for the keyboard block (three cols)
    center_col_x = keys_x + KEY_SIZE[0] + SPACING
    up_pos = (center_col_x - KEY_SIZE[0]//2, keys_y_mid - KEY_SIZE[1] - 40)
    left_pos = (keys_x, keys_y_mid)
    down_pos = (center_col_x - KEY_SIZE[0]//2, keys_y_mid)
    right_pos = (center_col_x + KEY_SIZE[0] + SPACING - KEY_SIZE[0]//2, keys_y_mid)
    center_pos = (center_col_x, keys_y_mid)

    # animation removed: show center keyboard image statically

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'salir_juego'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if skip_button_rect.collidepoint(event.pos):
                    return True

        # no animation: keep center key visible (static)

        # draw
        try:
            if fondo_nivel:
                screen.blit(fondo_nivel, (0,0))
            else:
                screen.fill((30,30,80))
        except Exception:
            screen.fill((30,30,80))
        screen.blit(overlay, (0,0))

        # title + instr with shadow
        tx = WIDTH//2 - title_surf.get_width()//2
        ty = 34
        screen.blit(title_shadow, (tx+4, ty+4))
        screen.blit(title_surf, (tx, ty))
        ix = WIDTH//2 - instr_surf.get_width()//2
        iy = ty + title_surf.get_height() + 10
        screen.blit(instr_shadow, (ix+3, iy+3))
        screen.blit(instr_surf, (ix, iy))

        # static display: show center key image, no highlights
        cur_name = 'center'

        def blit_key(base_surf, pos, highlighted=False):
            x, y = pos
            if highlighted:
                # draw a colored rounded square behind to indicate press
                bg = pygame.Surface((KEY_SIZE[0], KEY_SIZE[1]), pygame.SRCALPHA)
                bg.fill((180, 60, 60))
                screen.blit(bg, (x, y))
            screen.blit(base_surf, (x, y))

        # advance single-image animation timer
        step_time += dt
        if step_time >= seq_dur:
            step_time = 0.0
            step_index = (step_index + 1) % len(seq)
            try:
                if blip_sound:
                    blip_sound.play()
            except Exception:
                pass

        cur_name = seq[step_index]
        current_img = name_to_img.get(cur_name, key_center)
        # draw only the current image at the left animation area (center_pos)
        # but scale the animation image larger than the regular key size
        ANIM_SCALE = 1.5
        anim_w = int(KEY_SIZE[0] * ANIM_SCALE)
        anim_h = int(KEY_SIZE[1] * ANIM_SCALE)
        # compute a top-left so the larger image is centered where the original was
        prev_center_x = center_pos[0] + KEY_SIZE[0] // 2
        prev_center_y = center_pos[1] + KEY_SIZE[1] // 2
        anim_pos = (prev_center_x - anim_w // 2, prev_center_y - anim_h // 2)
        try:
            img_draw = pygame.transform.scale(current_img, (anim_w, anim_h))
        except Exception:
            img_draw = current_img
        screen.blit(img_draw, anim_pos)

        # RIGHT panel: square divided in 4 (map arrows to quadrants)
        PANEL_SIZE = KEY_SIZE[0] * 2 // 1  # approximate size
        # make the panel a bit smaller so its 4 cells appear smaller
        PANEL_SIZE = int(KEY_SIZE[0] * 1.0)
        panel_margin = 120
        panel_x = WIDTH - panel_margin - PANEL_SIZE
        panel_y = HEIGHT//2 - PANEL_SIZE//2
        cell_w = PANEL_SIZE // 2
        cell_h = PANEL_SIZE // 2
        # mapping: up->(0,0), right->(1,0), left->(0,1), down->(1,1)
        cell_map = {
            'up': (0, 0),
            'right': (1, 0),
            'left': (0, 1),
            'down': (1, 1),
        }

        # draw panel background
        pygame.draw.rect(screen, (220,220,220), (panel_x, panel_y, PANEL_SIZE, PANEL_SIZE), border_radius=8)
        # draw cell separators and cells
        for key_name, (cx, cy) in cell_map.items():
            cx_px = panel_x + cx * cell_w
            cy_px = panel_y + cy * cell_h
            # highlighted only if it matches the current key (do NOT highlight all on 'center')
            highlighted = (cur_name == key_name)
            cell_color = (180,60,60) if highlighted else (240,240,240)
            pygame.draw.rect(screen, cell_color, (cx_px+6, cy_px+6, cell_w-12, cell_h-12), border_radius=6)
            pygame.draw.rect(screen, (0,0,0), (cx_px+6, cy_px+6, cell_w-12, cell_h-12), 3, border_radius=6)

        # skip button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (255,215,0) if skip_button_rect.collidepoint(mouse_pos) else (240,240,240)
        pygame.draw.rect(screen, button_color, skip_button_rect, border_radius=12)
        pygame.draw.rect(screen, (0,0,0), skip_button_rect, 4, border_radius=12)
        skip_text = pygame.font.SysFont(None, 36).render('SALTAR', True, (0,0,0))
        screen.blit(skip_text, skip_text.get_rect(center=skip_button_rect.center))

        # small hint
        hint = small_font.render('Presiona ENTER para continuar', True, (255,255,255))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))

        pygame.display.flip()

    return True


if __name__ == '__main__':
    # quick manual test runner
    pygame.init()
    # match main game resolution
    screen = pygame.display.set_mode((1540, 785))
    mostrar_tutorial_nivel2(screen)
    pygame.quit()
