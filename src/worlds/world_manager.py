import pygame

from settings import *


class WorldManager:
    SHOOTER = 0
    PLATFORMER = 1

    def __init__(self):
        self.current_world = self.SHOOTER

        self.swap_flash = 0
        self.instability = 0

    def swap_world(self):
        if self.current_world == self.SHOOTER:
            self.current_world = self.PLATFORMER
        else:
            self.current_world = self.SHOOTER

        self.swap_flash = 255
        self.instability += 5

    def update(self, dt):
        if self.swap_flash > 0:
            self.swap_flash -= 900 * dt

        if self.swap_flash < 0:
            self.swap_flash = 0

    def render_background(self, screen):
        if self.current_world == self.SHOOTER:
            screen.fill((20, 5, 5))
        else:
            screen.fill((5, 10, 30))

        if self.swap_flash > 0:
            flash = pygame.Surface(screen.get_size())
            flash.set_alpha(
                max(0, min(255, int(self.swap_flash)))
            )
            flash.fill((255, 255, 255))
            screen.blit(flash, (0, 0))