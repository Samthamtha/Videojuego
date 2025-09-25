import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nivel 1 - Separación de Basura")
clock = pygame.time.Clock()
FPS = 60

# Colores
BLUE = (0,100,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,200,0)
RED = (200,0,0)
YELLOW = (200,200,0)

font = pygame.font.SysFont(None, 36)

# --- Sprites ---

class Trash(pygame.sprite.Sprite):
    def __init__(self, tipo, x, speed):
        super().__init__()
        self.tipo = tipo
        self.image = pygame.Surface((40,40))
        if tipo == 'organica':
            self.image.fill(GREEN)
        elif tipo == 'reciclable':
            self.image.fill(BLUE)
        else:
            self.image.fill(RED)
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
        self.image = pygame.Surface((80,40))
        if tipo == 'organica':
            self.image.fill(GREEN)
        elif tipo == 'reciclable':
            self.image.fill(BLUE)
        else:
            self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, HEIGHT-60))

class PlayerBar:
    def __init__(self, x):
        # Tres botes
        self.botes = pygame.sprite.Group()
        self.botes.add(Bin('organica', x))
        self.botes.add(Bin('reciclable', x+100))
        self.botes.add(Bin('otro', x+200))
        self.rect = pygame.Rect(x, HEIGHT-60, 300, 40)  # barra visual opcional

    def move(self, dx):
        self.rect.x += dx
        # Aquí no limitamos la barra completa para que se pueda mover libremente
        # Pero limitamos los botes individuales
        for i, bin in enumerate(self.botes.sprites()):
            bin.rect.x = self.rect.x + i*100
            if bin.rect.left < 0:
                bin.rect.left = 0
            if bin.rect.right > WIDTH:
                bin.rect.right = WIDTH

    def draw(self, surface):
        self.botes.draw(surface)

# --- Función principal ---
def run_level1():
    dificultad = "Normal"
    trash_speed = 5

    all_sprites = pygame.sprite.Group()
    trashes = pygame.sprite.Group()

    player = PlayerBar(250)
    all_sprites.add(player.botes)

    score = 0
    spawn_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movimiento
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 5
        player.move(dx)

        # Generar basura
        spawn_timer += 1
        if spawn_timer > 60:
            tipo = random.choice(['organica','reciclable','otro'])
            trash = Trash(tipo, random.randint(0, WIDTH-40), trash_speed)
            all_sprites.add(trash)
            trashes.add(trash)
            spawn_timer = 0

        # Actualizar basura
        trashes.update()

        # Colisiones según tipo
        for trash in trashes:
            for bin in player.botes:
                if trash.rect.colliderect(bin.rect):
                    if trash.tipo == bin.tipo:
                        score += 1
                        trash.kill()
                        # sonido de acierto
                    else:
                        score -= 1
                        trash.kill()
                        # sonido de error

        # Dibujar
        screen.fill(BLUE)
        all_sprites.draw(screen)
        player.draw(screen)

        text = font.render(f"Puntos: {score}", True, WHITE)
        screen.blit(text, (20,20))

        pygame.display.flip()

# --- Ejecutar nivel solo ---
if __name__ == "__main__":
    run_level1()
    pygame.quit()
