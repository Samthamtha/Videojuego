import os
import sys
import random
import math
import pygame
from pause import mostrar_menu_pausa
from victory_menu import mostrar_menu_victoria, mostrar_menu_derrota

# Final boss stage (Sliks-like) — cleaned, with boss HP bar and UI

WIDTH = 1540
HEIGHT = 785
FPS = 60

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'img')
SOUND_DIR = os.path.join(os.path.dirname(__file__), 'sonido')


def load_image_safe(path, size=None, fallback_color=(100, 100, 100)):
	try:
		img = pygame.image.load(path).convert_alpha()
		if size:
			img = pygame.transform.scale(img, size)
		return img
	except Exception:
		w, h = size if size else (64, 64)
		s = pygame.Surface((w, h), pygame.SRCALPHA)
		s.fill(fallback_color)
		try:
			font = pygame.font.SysFont(None, 14)
			label = font.render(os.path.basename(path), True, (0, 0, 0))
			s.blit(label, (4, 4))
		except Exception:
			pass
		return s


def _load_sound(path):
	try:
		return pygame.mixer.Sound(path)
	except Exception:
		return None


class EtapaFinal:
	def __init__(self, screen, dificultad=None):
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.fps = FPS
		self.dificultad = dificultad

		# Assets
		self.bg = load_image_safe(os.path.join(ASSET_DIR, 'fondo_final.jpg'), (WIDTH, HEIGHT), (18,18,28))
		# Load gato frames much larger per latest user request
		self.gato_frames = [load_image_safe(os.path.join(ASSET_DIR, f'gato_final{i}.png'), size=(520, 520)) for i in range(1,7)]
		# Make the player (pibble) noticeably bigger as requested
		self.player_frames = [load_image_safe(os.path.join(ASSET_DIR, f'pibble_ang{i}.png'), size=(80, 80)) for i in range(1,7)]
		# store player sprite dimensions for collisions/ground calculations
		self.player_w = self.player_frames[0].get_width()
		self.player_h = self.player_frames[0].get_height()
		heart_path = os.path.join(ASSET_DIR, 'heart.png')
		self.heart_img = load_image_safe(heart_path, (28,28)) if os.path.exists(heart_path) else None
		warn_path = os.path.join(ASSET_DIR, 'advertencia.png')
		self.warn_img = load_image_safe(warn_path, (64,64)) if os.path.exists(warn_path) else None

		try:
			pygame.mixer.init()
		except Exception:
			pass
		self.warn_sound = _load_sound(os.path.join(SOUND_DIR, 'advertencia.mp3'))
		self.laser_sound = _load_sound(os.path.join(SOUND_DIR, 'laser.mp3'))
		# Make warning sound a bit quieter so it's less jarring
		if self.warn_sound:
			try:
				self.warn_sound.set_volume(0.28)
			except Exception:
				pass

		# Stage
		self.platform_h = 100
		self.platform_rect = pygame.Rect(0, HEIGHT - self.platform_h, WIDTH, self.platform_h)

		# Player (place so the sprite stands on the black platform)
		self.player_pos = pygame.Vector2(180, HEIGHT - self.platform_h - (self.player_h // 2))
		self.player_vel = pygame.Vector2(0,0)
		self.player_speed = 5.0
		self.gravity = 0.6
		self.jump_speed = -13
		self.on_ground = False
		self.player_frame = 0
		self.player_anim_timer = 0
		self.player_max_hp = 10
		self.player_hp = self.player_max_hp
		self.player_invuln = 0

		# Attack
		self.attack_cooldown = 600
		self.last_attack_time = -9999
		self.attack_range = 110
		self.attacking = False
		self.attack_anim_start = 0
		self.ATTACK_ANIM_DURATION = 320
		self.ATTACK_HIT_TIME = 160
		self.attack_hit_applied = False

		# Boss: compute sprite size and place the cat standing on the black platform
		boss_w, boss_h = self.gato_frames[0].get_size()
		self.gato_pos = pygame.Vector2(WIDTH//2, HEIGHT - self.platform_h - boss_h//2 - 8)
		self.gato_dir = 1
		self.gato_speed = 2.0
		# keep the gato fully on-screen by constraining its center within margins
		left_bound = 120 + boss_w // 2
		right_bound = WIDTH - 120 - boss_w // 2
		self.gato_bounds = (left_bound, right_bound)
		self.gato_max_hp = 30
		self.gato_hp = self.gato_max_hp
		self.gato_frame = 0
		self.gato_anim_timer = 0
		self.gato_hit_timer = 0
		self.GATO_HIT_DURATION = 800

		# Death/victory sequence
		self.gato_dead = False
		self.death_start = 0
		self.DEATH_SHAKE_DURATION = 900
		self.DEATH_DISAPPEAR_DELAY = 200
		self.CONFETTI_DURATION = 2200
		self.confetti = []
		self.post_death_action = None

		# Attacks / lasers
		self.WARNING_MIN = 1200
		self.WARNING_MAX = 2200
		self.WARNING_DURATION = 700
		self.LASER_DURATION = 700
		self.LASER_WIDTH = 96
		# Ajustar daño según dificultad (2 vidas en principiante, 2 en otras)
		if dificultad and 'principiante' in str(dificultad).lower():
			self.LASER_DAMAGE = 2
		else:
			self.LASER_DAMAGE = 2
		self.SCRATCH_DAMAGE = 0
		
		# Tutorial
		self.tutorial_completado = False
		self.tutorial_start_time = 0

		self.next_warning_time = pygame.time.get_ticks() + random.randint(self.WARNING_MIN, self.WARNING_MAX)
		self.warning_active = False
		self.warning_start = 0
		self.warning_x = 0
		self.lasers = []

		# UI fonts
		self.font = pygame.font.SysFont(None, 28)
		self.font_large = pygame.font.SysFont(None, 44)
		self.font_tutorial = pygame.font.SysFont(None, 36)

		# Input flags
		self.moving_left = False
		self.moving_right = False
		
		# Efecto de golpe mejorado
		self.hit_effect_active = False
		self.hit_effect_start = 0
		self.hit_effect_duration = 300
		self.hit_particles = []

		self.running = True

        

	def spawn_confetti(self, count=40):
		# create simple confetti particles around the boss position
		for i in range(count):
			angle = random.uniform(0, 360)
			s = random.randint(6, 14)
			speed = random.uniform(1.5, 5.0)
			vel = pygame.Vector2(random.uniform(-1.5, 1.5) * speed, random.uniform(-3.5, -1.0) * speed)
			col = random.choice([(240,80,80), (240,200,60), (80,200,120), (120,160,240), (220,120,240)])
			p = {
				'pos': pygame.Vector2(self.gato_pos.x + random.randint(-40,40), self.gato_pos.y + random.randint(-40,40)),
				'vel': vel,
				'size': s,
				'color': col,
				'life': random.randint(900, 1800),
				'angle': angle,
				'spin': random.uniform(-6, 6)
			}
			self.confetti.append(p)
        

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit(); sys.exit()
			if event.type == pygame.KEYDOWN:
				# Cerrar tutorial con cualquier tecla
				if not self.tutorial_completado:
					self.tutorial_completado = True
					continue
					
				if event.key == pygame.K_ESCAPE:
					# Open pause menu and react to its selection
					try:
						accion = mostrar_menu_pausa(self.screen, HEIGHT, WIDTH)
					except Exception:
						# Fallback: if pause menu fails, exit to menu
						accion = 'salir'

					if accion == 'reanudar':
						# continue the level
						continue
					if accion == 'reiniciar':
						return 'reiniciar'
					if accion == 'salir':
						return 'salir_menu'
				if event.key in (pygame.K_a, pygame.K_LEFT): self.moving_left = True
				if event.key in (pygame.K_d, pygame.K_RIGHT): self.moving_right = True
				if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
					if self.on_ground:
						self.player_vel.y = self.jump_speed; self.on_ground = False
				if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
					now = pygame.time.get_ticks()
					if now - self.last_attack_time >= self.attack_cooldown:
						self.last_attack_time = now
						self.attacking = True; self.attack_anim_start = now; self.attack_hit_applied = False
			if event.type == pygame.KEYUP:
				if event.key in (pygame.K_a, pygame.K_LEFT): self.moving_left = False
				if event.key in (pygame.K_d, pygame.K_RIGHT): self.moving_right = False
		return None

	def update(self):
		# Pausar el juego si el tutorial está activo
		if not self.tutorial_completado:
			return
			
		dt = self.clock.tick(self.fps)
		now = pygame.time.get_ticks()

		# Player movement
		vx = 0
		if self.moving_left: vx -= self.player_speed
		if self.moving_right: vx += self.player_speed
		self.player_vel.x = vx
		self.player_vel.y += self.gravity
		self.player_pos += self.player_vel
		# ground calculation uses the player's sprite height (centered)
		ground_y = HEIGHT - self.platform_h - (self.player_h // 2)
		if self.player_pos.y >= ground_y:
			self.player_pos.y = ground_y; self.player_vel.y = 0; self.on_ground = True
		self.player_pos.x = max(24, min(WIDTH-24, self.player_pos.x))

		# Animations
		self.player_anim_timer += dt
		if self.player_anim_timer > 80:
			self.player_anim_timer = 0
			self.player_frame = (self.player_frame + 1) % len(self.player_frames)
		self.gato_anim_timer += dt
		if self.gato_anim_timer > 100:
			self.gato_anim_timer = 0
			self.gato_frame = (self.gato_frame + 1) % len(self.gato_frames)

		# Boss patrol
		self.gato_pos.x += self.gato_speed * self.gato_dir
		if self.gato_pos.x < self.gato_bounds[0]: self.gato_pos.x = self.gato_bounds[0]; self.gato_dir = 1
		if self.gato_pos.x > self.gato_bounds[1]: self.gato_pos.x = self.gato_bounds[1]; self.gato_dir = -1

		# Warning -> lasers
		if not self.warning_active and not self.lasers and now >= self.next_warning_time:
			target_x = int(self.gato_pos.x + random.randint(-140,140))
			target_x = max(40, min(WIDTH-40, target_x))
			self.warning_x = target_x; self.warning_active = True; self.warning_start = now
			try:
				if self.warn_sound: self.warn_sound.play()
			except Exception:
				pass

		if self.warning_active and now - self.warning_start >= self.WARNING_DURATION:
			self.warning_active = False
			num = random.choice([1,1,2])
			self.lasers = []
			for i in range(num):
				lx = int(self.warning_x + random.randint(-30,30) + i*(self.LASER_WIDTH+20))
				lx = max(0, min(WIDTH, lx))
				self.lasers.append({'x':lx, 'start':now, 'duration':self.LASER_DURATION})
			try:
				if self.laser_sound: self.laser_sound.play()
			except Exception:
				pass

		# Laser lifespan
		if self.lasers:
			alive = [L for L in self.lasers if now - L['start'] < L['duration']]
			if not alive: self.next_warning_time = now + random.randint(self.WARNING_MIN, self.WARNING_MAX)
			self.lasers = alive

		# Laser collision (use dynamic player size)
		if self.lasers and self.player_invuln <= 0:
			for L in self.lasers:
				laser_rect = pygame.Rect(L['x'] - self.LASER_WIDTH//2, 0, self.LASER_WIDTH, HEIGHT - self.platform_h)
				player_rect = pygame.Rect(int(self.player_pos.x) - self.player_w//2,
										  int(self.player_pos.y) - self.player_h//2,
										  self.player_w, self.player_h)
				if laser_rect.colliderect(player_rect):
					self.player_hp = max(0, self.player_hp - self.LASER_DAMAGE)
					self.player_invuln = 700
					break

		# Boss scratch (use actual sprite rects)
		gf_now = self.gato_frames[self.gato_frame]
		gato_rect = gf_now.get_rect(center=(int(self.gato_pos.x), int(self.gato_pos.y)))
		player_rect = pygame.Rect(int(self.player_pos.x) - self.player_w//2,
								  int(self.player_pos.y) - self.player_h//2,
								  self.player_w, self.player_h)
		if gato_rect.colliderect(player_rect) and self.player_invuln <= 0:
			if self.SCRATCH_DAMAGE > 0:
				self.player_hp = max(0, self.player_hp - self.SCRATCH_DAMAGE)
			self.player_invuln = 600

		if self.player_invuln > 0:
			self.player_invuln = max(0, self.player_invuln - dt)

		# Attack animation handling
		if self.attacking:
			elapsed = now - self.attack_anim_start
			if not self.attack_hit_applied and elapsed >= self.ATTACK_HIT_TIME:
				if abs(self.player_pos.x - self.gato_pos.x) <= self.attack_range:
					self.gato_hp = max(0, self.gato_hp - 3)
					self.gato_hit_timer = now
					# Activar efecto de golpe mejorado
					self.hit_effect_active = True
					self.hit_effect_start = now
					# Crear partículas de impacto
					for _ in range(15):
						angle = random.uniform(0, 360)
						speed = random.uniform(2, 6)
						self.hit_particles.append({
							'pos': pygame.Vector2(self.gato_pos.x, self.gato_pos.y),
							'vel': pygame.Vector2(math.cos(math.radians(angle)) * speed, 
												math.sin(math.radians(angle)) * speed),
							'size': random.randint(4, 10),
							'color': (255, 200, 0),
							'life': random.randint(200, 400)
						})
				self.attack_hit_applied = True
			if elapsed >= self.ATTACK_ANIM_DURATION:
				self.attacking = False
		
		# Actualizar efecto de golpe
		if self.hit_effect_active:
			if now - self.hit_effect_start >= self.hit_effect_duration:
				self.hit_effect_active = False
				self.hit_particles = []
			else:
				# Actualizar partículas
				alive_particles = []
				for p in self.hit_particles:
					p['pos'] += p['vel']
					p['vel'] *= 0.95  # Fricción
					p['life'] -= dt
					if p['life'] > 0:
						alive_particles.append(p)
				self.hit_particles = alive_particles

		# Death sequence trigger
		if self.gato_hp <= 0 and not self.gato_dead:
			self.gato_dead = True
			self.death_start = now
			# stop boss movement
			self.gato_speed = 0
			# small sound or effect could be played here

		# If in death/confetti phase, update particles instead of normal boss logic
		if self.gato_dead:
			# Confetti spawn after disappearance delay
			death_elapsed = now - self.death_start
			if death_elapsed >= self.DEATH_DISAPPEAR_DELAY and not self.confetti:
				# spawn confetti pieces
				self.spawn_confetti(60)

			# update confetti
			if self.confetti:
				alive = []
				for p in self.confetti:
					p['vel'].y += 0.25  # gravity
					p['pos'] += p['vel']
					p['life'] -= dt
					p['angle'] += p.get('spin', 0)
					if p['life'] > 0:
						alive.append(p)
				self.confetti = alive

			# after confetti duration, show victory message and menu once
			if death_elapsed >= self.DEATH_SHAKE_DURATION + self.CONFETTI_DURATION and self.post_death_action is None:
				# Mostrar mensaje personalizado de victoria
				self.show_victory_message()
				try:
					self.post_death_action = mostrar_menu_victoria(self.screen, 'level_final')
				except Exception:
					self.post_death_action = 'salir'

	def draw_warning(self):
		if self.warning_active:
			x = int(self.warning_x)
			if self.warn_img:
				w = self.warn_img.get_width(); self.screen.blit(self.warn_img, (x-w//2, 40))
			else:
				tri = pygame.Surface((72,72), pygame.SRCALPHA)
				pygame.draw.polygon(tri, (240,200,30), [(36,4),(68,64),(4,64)])
				pygame.draw.rect(tri, (160,0,0), (32,16,8,28))
				self.screen.blit(tri, (x-36,24))
			txt = self.font.render('¡ADVERTENCIA!', True, (255,220,40))
			self.screen.blit(txt, (x - txt.get_width()//2, 100))

	def draw_lasers(self):
		for L in self.lasers:
			alpha = 170
			surf = pygame.Surface((self.LASER_WIDTH, HEIGHT - self.platform_h), pygame.SRCALPHA)
			surf.fill((220,30,30,alpha))
			self.screen.blit(surf, (L['x'] - self.LASER_WIDTH//2, 0))

	def draw(self):
		# Background and platform
		self.screen.blit(self.bg, (0,0))
		pygame.draw.rect(self.screen, (0,0,0), self.platform_rect)

		# Player
		pf = self.player_frames[self.player_frame]
		pr = pf.get_rect(center=(int(self.player_pos.x), int(self.player_pos.y)))
		if self.player_invuln > 0 and (self.player_invuln // 80) % 2 == 0:
			temp = pf.copy(); temp.fill((255,255,255,120), special_flags=pygame.BLEND_RGBA_ADD); self.screen.blit(temp, pr)
		else:
			self.screen.blit(pf, pr)

		# Attack effect mejorado
		if self.attacking:
			facing = 1 if self.player_pos.x < self.gato_pos.x else -1
			slash_w, slash_h = 80, 35
			slash = pygame.Surface((slash_w, slash_h), pygame.SRCALPHA)
			# Efecto de golpe más visible con gradiente
			for i in range(slash_h):
				alpha = int(255 * (1 - i / slash_h))
				pygame.draw.line(slash, (255, 255, 100, alpha), (0, i), (slash_w, i))
			pygame.draw.ellipse(slash, (255, 200, 60, 220), (0, 0, slash_w, slash_h))
			sx = int(self.player_pos.x + facing*35 - slash_w//2); sy = int(self.player_pos.y - 15)
			if facing == -1: slash = pygame.transform.flip(slash, True, False)
			self.screen.blit(slash, (sx, sy))
		
		# Dibujar partículas de impacto
		for p in self.hit_particles:
			alpha = int(255 * (p['life'] / 400))
			particle_surf = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
			pygame.draw.circle(particle_surf, (*p['color'], alpha), (p['size']//2, p['size']//2), p['size']//2)
			self.screen.blit(particle_surf, (int(p['pos'].x - p['size']//2), int(p['pos'].y - p['size']//2)))

		# Boss (possibly red when hit) / Death shake and disappearance
		gf = self.gato_frames[self.gato_frame]
		now = pygame.time.get_ticks()
		if self.gato_dead:
			death_elapsed = now - self.death_start
			# during shake phase, draw gato with horizontal shake offset
			if death_elapsed <= self.DEATH_SHAKE_DURATION:
				shake_amount = 6 + int(6 * (death_elapsed / self.DEATH_SHAKE_DURATION))
				offset_x = int(shake_amount * (1 if (death_elapsed // 40) % 2 == 0 else -1))
				gr = gf.get_rect(center=(int(self.gato_pos.x) + offset_x, int(self.gato_pos.y)))
				self.screen.blit(gf, gr)
			else:
				# after shake and disappear delay, gato is not drawn (disappeared)
				pass
		else:
			gr = gf.get_rect(center=(int(self.gato_pos.x), int(self.gato_pos.y)))
			if now - self.gato_hit_timer <= self.GATO_HIT_DURATION:
				temp = gf.copy()
				try: temp.fill((220,30,30,120), special_flags=pygame.BLEND_RGBA_ADD)
				except Exception: pass
				self.screen.blit(temp, gr)
			else:
				self.screen.blit(gf, gr)

		# Warnings and lasers
		self.draw_warning(); self.draw_lasers()

		# Draw confetti particles (if any)
		if self.confetti:
			for p in self.confetti:
				col = p['color']
				x, y = int(p['pos'].x), int(p['pos'].y)
				size = p['size']
				# draw as rotated rect/ellipse approximation
				surf = pygame.Surface((size, size), pygame.SRCALPHA)
				surf.fill(col)
				rotated = pygame.transform.rotate(surf, p.get('angle', 0))
				self.screen.blit(rotated, (x - rotated.get_width()//2, y - rotated.get_height()//2))

		# UI: Boss HP bar (top center) - large and flashy
		bar_w = 640; bar_h = 36
		bx = WIDTH//2 - bar_w//2; by = 20
		# panel behind bar
		panel = pygame.Surface((bar_w+12, bar_h+12), pygame.SRCALPHA)
		panel.fill((0,0,0,160))
		pygame.draw.rect(panel, (255,255,255,30), panel.get_rect(), 2, border_radius=8)
		self.screen.blit(panel, (bx-6, by-6))
		# empty background
		pygame.draw.rect(self.screen, (80, 20, 20), (bx, by, bar_w, bar_h), 0, border_radius=8)
		# fill
		frac = max(0.0, min(1.0, self.gato_hp / max(1, self.gato_max_hp)))
		fill_w = int(bar_w * frac)
		if fill_w > 0:
			grad = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
			grad.fill((240,80,80))
			# bright highlight
			hi = pygame.Surface((fill_w, bar_h//2), pygame.SRCALPHA); hi.fill((255,140,140,80))
			grad.blit(hi, (0,0))
			self.screen.blit(grad, (bx, by))
		# border and name
		pygame.draw.rect(self.screen, (30,0,0), (bx, by, bar_w, bar_h), 3, border_radius=8)
		name = self.font_large.render('GATO FINAL', True, (255,220,180))
		self.screen.blit(name, (bx + 12, by + bar_h//2 - name.get_height()//2))
		# numeric hp on right of bar
		num = self.font.render(f'{self.gato_hp}/{self.gato_max_hp}', True, (255,255,255))
		self.screen.blit(num, (bx + bar_w - num.get_width() - 12, by + bar_h//2 - num.get_height()//2))

		# Player hearts UI (bottom-left)
		hearts_total = self.player_max_hp
		heart_w = 28; gap = 6; sx = 20; sy = HEIGHT - 44
		for i in range(hearts_total):
			x = sx + i * (heart_w + gap)
			if self.heart_img:
				img = self.heart_img.copy()
				if i >= self.player_hp: img.fill((80,80,80,160), special_flags=pygame.BLEND_RGBA_MULT)
				self.screen.blit(img, (x, sy))
			else:
				color = (220,40,40) if i < self.player_hp else (80,80,80)
				pygame.draw.polygon(self.screen, color, [(x+6, sy+14),(x+14, sy+26),(x+22, sy+14),(x+14,sy+6)])

		# Mostrar tutorial si no está completado
		if not self.tutorial_completado:
			self.draw_tutorial()
		
		pygame.display.flip()

	def show_victory_message(self):
		"""Muestra un mensaje personalizado de victoria"""
		# Fondo semitransparente
		overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 200))
		self.screen.blit(overlay, (0, 0))
		
		# Panel del mensaje
		panel_w = 900
		panel_h = 300
		panel_x = WIDTH // 2 - panel_w // 2
		panel_y = HEIGHT // 2 - panel_h // 2
		
		# Fondo del panel
		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((30, 40, 30, 240))
		pygame.draw.rect(panel, (100, 255, 100, 255), panel.get_rect(), 4, border_radius=15)
		self.screen.blit(panel, (panel_x, panel_y))
		
		# Mensaje de victoria
		mensaje = "¡Felicidades! Has logrado vencer tu némesis."
		mensaje2 = "Recuerda cuidar el planeta. ¡Suerte!"
		
		# Título
		title = self.font_large.render("¡VICTORIA!", True, (100, 255, 100))
		self.screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 30))
		
		# Mensaje principal
		text1 = self.font_tutorial.render(mensaje, True, (255, 255, 255))
		self.screen.blit(text1, (panel_x + panel_w // 2 - text1.get_width() // 2, panel_y + 100))
		
		text2 = self.font_tutorial.render(mensaje2, True, (255, 255, 255))
		self.screen.blit(text2, (panel_x + panel_w // 2 - text2.get_width() // 2, panel_y + 150))
		
		# Instrucción para continuar
		continuar = self.font.render("Presiona cualquier tecla para continuar...", True, (200, 255, 200))
		self.screen.blit(continuar, (panel_x + panel_w // 2 - continuar.get_width() // 2, panel_y + 220))
		
		pygame.display.flip()
		
		# Esperar a que el usuario presione una tecla
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					waiting = False
	
	def draw_tutorial(self):
		"""Dibuja el tutorial inicial"""
		# Fondo semitransparente
		overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 200))
		self.screen.blit(overlay, (0, 0))
		
		# Panel del tutorial
		panel_w = 800
		panel_h = 500
		panel_x = WIDTH // 2 - panel_w // 2
		panel_y = HEIGHT // 2 - panel_h // 2
		
		# Fondo del panel
		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((30, 30, 40, 240))
		pygame.draw.rect(panel, (255, 255, 255, 255), panel.get_rect(), 4, border_radius=15)
		self.screen.blit(panel, (panel_x, panel_y))
		
		# Título
		title = self.font_large.render("TUTORIAL - COMBATE FINAL", True, (255, 220, 100))
		self.screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 30))
		
		# Instrucciones
		y_offset = 100
		line_height = 50
		
		instrucciones = [
			"MOVIMIENTO:",
			"  A / ← : Mover a la izquierda",
			"  D / → : Mover a la derecha",
			"  W / ↑ / Espacio : Saltar",
			"",
			"ATAQUE:",
			"  Enter : Atacar al gato (debes estar cerca)",
			"",
			"ADVERTENCIAS:",
			"  ⚠️ Evita los láseres rojos del gato",
			"  ⚠️ Los láseres quitan 2 vidas",
			"  ⚠️ Mantente en movimiento para esquivar",
			"",
			"Presiona cualquier tecla para comenzar..."
		]
		
		for i, texto in enumerate(instrucciones):
			if texto.startswith("  "):
				color = (200, 200, 200)
				font_inst = self.font
			elif texto.endswith(":"):
				color = (255, 200, 100)
				font_inst = self.font_tutorial
			elif texto.startswith("⚠️"):
				color = (255, 100, 100)
				font_inst = self.font
			elif "Presiona" in texto:
				color = (100, 255, 100)
				font_inst = self.font_tutorial
			else:
				color = (255, 255, 255)
				font_inst = self.font
			
			text_surf = font_inst.render(texto, True, color)
			self.screen.blit(text_surf, (panel_x + 40, panel_y + y_offset + i * line_height))

	def run(self):
		while self.running:
			accion = self.handle_events()
			if accion == 'salir_menu': return 'salir_menu'
			self.update()
			if self.player_hp <= 0: return 'derrota'
			# Wait for death/confetti sequence to complete before returning victory
			if self.gato_dead:
				# if the post-death menu has been shown, forward its action
				if self.post_death_action is not None:
					return self.post_death_action
			self.draw()


def run_etapa_final(dificultad=None, idioma=None, screen=None):
	pygame.init()
	try:
		pygame.mixer.init()
	except Exception:
		pass

	# If called standalone (no screen provided), create a window and start music
	if screen is None:
		screen = pygame.display.set_mode((WIDTH, HEIGHT))
		# Try to play the stage music if present
		try:
			music_path = os.path.join(SOUND_DIR, 'final.mp3')
			if os.path.exists(music_path):
				pygame.mixer.music.load(music_path)
				pygame.mixer.music.set_volume(0.3)
				pygame.mixer.music.play(-1)
		except Exception:
			pass

	try:
		etapa = EtapaFinal(screen, dificultad)
	except Exception:
		import traceback
		traceback.print_exc()
		raise
	return etapa.run()


if __name__ == '__main__':
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	run_etapa_final(screen=screen)

