# sprites.py
import pygame
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [
            pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "PjFemale.png")), (100, 100)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "PjFemaleWalk1.png")), (100, 100)),
            pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "PjFemaleWalk2.png")), (100, 100)),
        ]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_animating = False
        self.animation_speed = 0.15
        self.counter = 0

    def update(self):
        if self.is_animating:
            self.counter += self.animation_speed
            if self.counter >= 1:
                self.counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
