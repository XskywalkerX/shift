import pygame
import math


class EnemyProjectile:

    def __init__(self, x, y, angle, damage=15):

        self.rect = pygame.Rect(
            x,
            y,
            12,
            12
        )

        self.damage = damage

        self.speed = 8

        self.dx = math.cos(angle)
        self.dy = math.sin(angle)

        self.dead = False

    def update(self):

        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

        if (
            self.rect.right < 0
            or self.rect.left > 1920
            or self.rect.bottom < 0
            or self.rect.top > 1080
        ):
            self.dead = True

    def render(self, screen):

        pygame.draw.rect(
            screen,
            (255, 200, 50),
            self.rect
        )