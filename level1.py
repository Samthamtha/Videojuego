import pygame
import sys
import random
from pause import mostrar_menu_pausa

pygame.init()
WIDTH, HEIGHT = 1540, 785
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

bin_organica = pygame.image.load("img/boteVerde.png").convert_alpha()
bin_organica = pygame.transform.scale(bin_organica, (190, 70))
bin_reciclable = pygame.image.load("img/boteazul.png").convert_alpha()
bin_reciclable = pygame.transform.scale(bin_reciclable, (190, 70))
bin_inorganico = pygame.image.load("img/boterojo.png").convert_alpha()
bin_inorganico = pygame.transform.scale(bin_inorganico, (190, 70))





trash_cascara = pygame.image.load("img/Cascara.png").convert_alpha()
trash_cascara = pygame.transform.scale(trash_cascara, (40, 40))
trash_lata = pygame.image.load("img/Lata.png").convert_alpha()
trash_lata = pygame.transform.scale(trash_lata, (40, 40))
trash_botella = pygame.image.load("img/botella.png").convert_alpha()
trash_botella = pygame.transform.scale(trash_botella, (40, 40))



# --- Sprites ---

class Trash(pygame.sprite.Sprite):
    def __init__(self, tipo, x, speed):
        super().__init__()
        self.tipo = tipo
        self.image = pygame.Surface((40,40),pygame.SRCALPHA)
        if tipo == 'organica':
            self.image.blit(trash_cascara, (0, 0))
        elif tipo == 'reciclable':
            self.image.blit(trash_lata, (0, 0))
        else:
            self.image.blit(trash_botella, (0, 0))
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
        self.image = pygame.Surface((190,70), pygame.SRCALPHA)
        if tipo == 'organica':
            self.image.blit(bin_organica, (0, 0))
        elif tipo == 'reciclable':
            self.image.blit(bin_reciclable, (0, 0))
        else:       
            self.image.blit(bin_inorganico, (0, 0))
        self.rect = self.image.get_rect(topleft=(x, HEIGHT-80))

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
            bin.rect.x = self.rect.x + i*150
            if bin.rect.left < 0:
                bin.rect.left = 0
            if bin.rect.right > WIDTH:
                bin.rect.right = WIDTH

    def draw(self, surface):
        self.botes.draw(surface)

# --- Función principal ---
def run_level1(dificultad, idioma, screen):
    # Ajuste de velocidad según dificultad
    if dificultad.lower() == "fácil" or dificultad.lower() == "facil":
        trash_speed = 2
    elif dificultad.lower() == "difícil" or dificultad.lower() == "dificil":
        trash_speed = 6
    else:
        trash_speed = 4  # Por defecto o "Normal"

    fondo = pygame.image.load("img/rio.png").convert()
    fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))

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


            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                accion = mostrar_menu_pausa(screen, WIDTH, HEIGHT)

                if accion == "reanudar":
                    pass  # Simplemente continúa el juego
                elif accion == "reiniciar":
                    # Reinicia el nivel desde cero
                    run_level1(dificultad, idioma, screen)
                    return
                elif accion == "salir":
                    return  # Regresa al menú principal




        # Movimiento
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -7
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 7
        player.move(dx)

        # Generar basura
        spawn_timer += 1
        if spawn_timer > 60:
            tipo = random.choice(['organica','reciclable','otro'])
            trash = Trash(tipo, random.randint(500, WIDTH-500), trash_speed)
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
        screen.blit(fondo, (0, 0))
        all_sprites.draw(screen)
        player.draw(screen)

        text = font.render(f"Puntos: {score}", True, WHITE)
        screen.blit(text, (20,20))

        pygame.display.flip()

# --- Ejecutar nivel solo ---
if __name__ == "__main__":
    run_level1()
    pygame.quit()
