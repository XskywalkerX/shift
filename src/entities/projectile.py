import pygame
import math


class Projectile:
    def __init__(self, x, y, angle):
        self.rect = pygame.Rect(x, y, 10, 10)

        self.speed = 15

        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

        self.dead = False

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def render(self, screen):
        pygame.draw.rect(
            screen,
            (255, 255, 100),
            self.rect
        )