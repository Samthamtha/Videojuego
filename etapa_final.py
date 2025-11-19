import pygame
import sys
import random
from pause import mostrar_menu_pausa
from victory_menu import mostrar_menu_victoria, mostrar_menu_derrota

# Estructura básica de la etapa final (esqueleto - imágenes/sonidos se añadirán después)

WIDTH = 1540
HEIGHT = 785
FPS = 60


def load_image_safe(path, size=None, fallback_color=(200, 200, 200)):
	"""Carga una imagen y si falla devuelve una Surface de fallback con etiqueta."""
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
			label = font.render(path.split('/')[-1], True, (0, 0, 0))
			s.blit(label, (4, 4))
		except Exception:
			pass
		return s


class EtapaFinal:
	"""Clase que encapsula la etapa final (estructura, estados y dibujos).

	Por ahora es un esqueleto: placeholders para jugador, jefe, ataques y simbología.
	Imágenes reales y mecánicas se agregarán más adelante.
	"""

	def __init__(self, screen):
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.fps = FPS

		# Estados: 'intro' -> 'battle' -> 'victory'/'game_over'
		self.state = 'intro'
		self.ticks = 0

		# Cargar assets placeholders (se pueden reemplazar por imágenes reales más tarde)
		self.player_img = load_image_safe('img/player_placeholder.png', (48, 48), (100, 180, 250))
		self.boss_img = load_image_safe('img/boss_placeholder.png', (140, 140), (220, 80, 80))
		self.soul_img = load_image_safe('img/soul_placeholder.png', (24, 24), (255, 200, 0))

		# Simbología izquierda (lista de rutas que luego se reemplazarán por imágenes reales)
		self.legend_images = [
			load_image_safe('img/legend_1.png', (64, 64)),
			load_image_safe('img/legend_2.png', (64, 64)),
			load_image_safe('img/legend_3.png', (64, 64)),
		]

		# Propiedades de jugador y jefe (valores iniciales y placeholders)
		# Battle box (área donde se mueve el 'soul' al estilo Undertale)
		self.box_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 260, 300, 160)
		# Posición del jugador inicial dentro del cuadro
		self.player_pos = pygame.Vector2(self.box_rect.centerx, self.box_rect.centery)
		self.player_hp = 20
		self.player_max_hp = 20
		self.player_speed = 4.5
		self.player_invuln = 0  # frames de invulnerabilidad tras recibir daño

		self.boss_pos = pygame.Vector2(WIDTH // 2, 180)
		self.boss_hp = 60
		self.boss_max_hp = 60

		# Lista de ataques activos (estructuras simples por ahora)
		self.attacks = []  # cada ataque: dict con tipo, pos, vel, lifetime

		# Fuentes
		self.font = pygame.font.SysFont(None, 28)
		self.font_large = pygame.font.SysFont(None, 44)

	def start_battle(self):
		self.state = 'battle'
		self.ticks = 0

	def reset(self):
		self.state = 'intro'
		self.ticks = 0
		self.player_hp = self.player_max_hp
		self.boss_hp = self.boss_max_hp
		self.attacks.clear()

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					# Pausa
					accion = mostrar_menu_pausa(self.screen, HEIGHT, WIDTH)
					if accion == 'salir':
						return 'salir_menu'
					if accion == 'reiniciar':
						return 'reiniciar'

				if self.state == 'intro' and event.key == pygame.K_SPACE:
					self.start_battle()

				# Placeholder: tecla para simular daño al jefe
				if self.state == 'battle' and event.key == pygame.K_a:
					self.boss_hp = max(0, self.boss_hp - 5)
					if self.boss_hp == 0:
						self.state = 'victory'

				# Placeholder: tecla para simular daño al jugador
				if self.state == 'battle' and event.key == pygame.K_s:
					self.player_hp = max(0, self.player_hp - 5)
					if self.player_hp == 0:
						self.state = 'game_over'

		return None

	def update(self):
		self.ticks += 1

		if self.state == 'intro':
			# animación/espera breve antes de comenzar
			if self.ticks > 90:
				# esperar que el jugador pulse espacio para empezar
				pass

		elif self.state == 'battle':
			# Lógica simple de generación de ataques placeholder
			if self.ticks % 60 == 0:
				# generar un ataque aleatorio
				atk = {
					'type': random.choice(['bone', 'gaster', 'laser']),
					'pos': pygame.Vector2(random.randint(200, WIDTH - 200), -40),
					'vel': pygame.Vector2(0, random.uniform(2.0, 4.0)),
					'life': 300
				}
				self.attacks.append(atk)

			# actualizar ataques
			for atk in list(self.attacks):
				atk['pos'] += atk['vel']
				atk['life'] -= 1
				if atk['pos'].y > HEIGHT + 100 or atk['life'] <= 0:
					try:
						self.attacks.remove(atk)
					except ValueError:
						pass

				# Movimiento del jugador dentro del battle box (WASD o flechas)
				keys = pygame.key.get_pressed()
				dx = 0.0
				dy = 0.0
				if keys[pygame.K_LEFT] or keys[pygame.K_a]:
					dx -= self.player_speed
				if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
					dx += self.player_speed
				if keys[pygame.K_UP] or keys[pygame.K_w]:
					dy -= self.player_speed
				if keys[pygame.K_DOWN] or keys[pygame.K_s]:
					dy += self.player_speed

				# Aplicar movimiento y mantener dentro de box
				new_pos = self.player_pos + pygame.Vector2(dx, dy)
				pad = 8
				min_x = self.box_rect.left + pad
				max_x = self.box_rect.right - pad
				min_y = self.box_rect.top + pad
				max_y = self.box_rect.bottom - pad
				new_pos.x = max(min_x, min(max_x, new_pos.x))
				new_pos.y = max(min_y, min(max_y, new_pos.y))
				self.player_pos = new_pos

				# Decrementar invulnerabilidad si aplica
				if self.player_invuln > 0:
					self.player_invuln -= 1

				# Colisiones simples: si un ataque toca al jugador, resta vida y activa invuln
				for atk in list(self.attacks):
					# distancia simple
					if (atk['pos'] - self.player_pos).length() < 22:
						if self.player_invuln == 0:
							self.player_hp = max(0, self.player_hp - 1)
							self.player_invuln = 60  # 1 segundo aprox a 60 FPS
						try:
							self.attacks.remove(atk)
						except ValueError:
							pass
						if self.player_hp == 0:
							self.state = 'game_over'

		elif self.state in ('victory', 'game_over'):
			# dejar que el usuario vea la pantalla y presione una tecla para continuar
			pass

	def draw_legend_left(self):
		# rectángulo vertical en la izquierda con fondo blanco y casillas para imágenes
		panel_w = 140
		panel_h = HEIGHT - 100
		panel_x = 10
		panel_y = 50

		# Sombra
		shadow = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		shadow.fill((0, 0, 0, 60))
		self.screen.blit(shadow, (panel_x + 6, panel_y + 6))

		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((255, 255, 255, 230))
		pygame.draw.rect(panel, (0, 0, 0), panel.get_rect(), 2, border_radius=6)
		self.screen.blit(panel, (panel_x, panel_y))

		# Dibujar casillas blancas centradas en el panel
		gap = 18
		box_size = 64
		start_y = panel_y + 20
		for i, img in enumerate(self.legend_images):
			box_x = panel_x + (panel_w - box_size) // 2
			box_y = start_y + i * (box_size + gap)
			pygame.draw.rect(self.screen, (255, 255, 255), (box_x - 4, box_y - 4, box_size + 8, box_size + 8), 0, border_radius=6)
			# fondo blanco pequeño
			inner = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
			inner.fill((255, 255, 255))
			self.screen.blit(inner, (box_x, box_y))
			# imagen (placeholder)
			img_rect = img.get_rect(center=(box_x + box_size // 2, box_y + box_size // 2))
			self.screen.blit(img, img_rect)

	def draw(self):
		# Fondo simple
		self.screen.fill((20, 20, 30))

		# Dibujar boss
		boss_rect = self.boss_img.get_rect(center=(int(self.boss_pos.x), int(self.boss_pos.y)))
		self.screen.blit(self.boss_img, boss_rect)

		# Dibujar battle box (cuadro donde se mueve el jugador al estilo Undertale)
		pygame.draw.rect(self.screen, (0, 0, 0), self.box_rect.inflate(6, 6))
		pygame.draw.rect(self.screen, (255, 255, 255), self.box_rect)

		# Dibujar ataques (se ven dentro y fuera de la caja)
		for atk in self.attacks:
			if atk['type'] == 'bone':
				pygame.draw.rect(self.screen, (240, 240, 240), (int(atk['pos'].x) - 8, int(atk['pos'].y) - 20, 16, 40))
			elif atk['type'] == 'gaster':
				pygame.draw.circle(self.screen, (180, 180, 255), (int(atk['pos'].x), int(atk['pos'].y)), 18)
			elif atk['type'] == 'laser':
				pygame.draw.line(self.screen, (255, 50, 50), (int(atk['pos'].x), int(atk['pos'].y)), (int(atk['pos'].x), HEIGHT), 4)

		# Dibujar jugador (soul) dentro del box - parpadea si está invulnerable
		alpha = 255 if self.player_invuln == 0 or (self.player_invuln // 6) % 2 == 0 else 100
		# círculo simple representando el 'soul'
		surf = pygame.Surface((36, 36), pygame.SRCALPHA)
		pygame.draw.circle(surf, (255, 200, 0, alpha), (18, 18), 14)
		self.screen.blit(surf, (int(self.player_pos.x) - 18, int(self.player_pos.y) - 18))


		# HUD: barras de vida
		# Boss HP
		hp_w = 420
		hp_h = 24
		hp_x = WIDTH // 2 - hp_w // 2
		hp_y = 20
		pygame.draw.rect(self.screen, (0, 0, 0), (hp_x - 4, hp_y - 4, hp_w + 8, hp_h + 8), 0, border_radius=6)
		pygame.draw.rect(self.screen, (120, 0, 0), (hp_x, hp_y, hp_w, hp_h), 0, border_radius=6)
		boss_frac = max(0, self.boss_hp / max(1, self.boss_max_hp))
		pygame.draw.rect(self.screen, (255, 80, 80), (hp_x, hp_y, int(hp_w * boss_frac), hp_h), 0, border_radius=6)
		text_boss = self.font.render(f"Jefe  {self.boss_hp}/{self.boss_max_hp}", True, (255, 255, 255))
		self.screen.blit(text_boss, (hp_x + 8, hp_y - 2))

		# Player HP (esquina inferior izquierda)
		ph_w = 220
		ph_h = 18
		ph_x = 180
		ph_y = HEIGHT - 40
		pygame.draw.rect(self.screen, (0, 0, 0), (ph_x - 4, ph_y - 4, ph_w + 8, ph_h + 8), 0, border_radius=6)
		pygame.draw.rect(self.screen, (40, 40, 40), (ph_x, ph_y, ph_w, ph_h), 0, border_radius=6)
		player_frac = max(0, self.player_hp / max(1, self.player_max_hp))
		pygame.draw.rect(self.screen, (80, 200, 120), (ph_x, ph_y, int(ph_w * player_frac), ph_h), 0, border_radius=6)
		text_player = self.font.render(f"Jugador  {self.player_hp}/{self.player_max_hp}", True, (255, 255, 255))
		self.screen.blit(text_player, (ph_x + 6, ph_y - 22))

		# Dibujar panel/simbología izquierda
		self.draw_legend_left()

		# Mensajes según estado
		if self.state == 'intro':
			title = self.font_large.render("ETAPA FINAL", True, (255, 255, 255))
			sub = self.font.render("Presiona ESPACIO para empezar el combate", True, (200, 200, 200))
			self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
			self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

		elif self.state == 'victory':
			# Pantalla de victoria simple; luego se puede abrir mostrar_menu_victoria
			text = self.font_large.render("¡VICTORIA!", True, (240, 220, 60))
			self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

		elif self.state == 'game_over':
			text = self.font_large.render("DERROTA", True, (240, 80, 80))
			self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))

		pygame.display.flip()


def run_etapa_final(dificultad=None, idioma=None, screen=None):
	"""Función de entrada para la etapa final. Devuelve códigos similares a los niveles:
	'reiniciar', 'salir_menu', 'salir_juego', 'siguiente' (si aplica)"""
	pygame.init()

	if screen is None:
		screen = pygame.display.set_mode((WIDTH, HEIGHT))

	etapa = EtapaFinal(screen)

	running = True
	while running:
		etapa.clock.tick(FPS)

		accion = etapa.handle_events()
		if accion == 'salir_menu':
			return 'salir_menu'
		if accion == 'reiniciar':
			return 'reiniciar'

		etapa.update()

		# Si la etapa llegó a victory/game_over podemos mostrar menús
		if etapa.state == 'victory':
			# mostrar menú de victoria (usa nivel id 'level_final' para indicar último)
			opcion = mostrar_menu_victoria(screen, 'level_final')
			if opcion == 'reintentar' or opcion == 'reintentar':
				etapa.reset()
				continue
			elif opcion == 'siguiente':
				return 'siguiente'
			else:
				return 'salir_menu'

		if etapa.state == 'game_over':
			opcion = mostrar_menu_derrota(screen)
			if opcion == 'reintentar':
				etapa.reset()
				continue
			else:
				return 'salir_menu'

		etapa.draw()

	return 'salir_menu'


if __name__ == '__main__':
	# Permite prueba rápida ejecutando este archivo directamente
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	run_etapa_final(screen=screen)

