import pygame
import random


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

        self.speed = random.choice([-2, 2])
        self.moving = random.choice([True, False])

    def update(self):
        if self.moving:
            self.rect.x += self.speed

            if self.rect.left <= 0:
                self.speed *= -1

            if self.rect.right >= 1280:
                self.speed *= -1

    def render(self, screen):
        pygame.draw.rect(
            screen,
            (100, 140, 255),
            self.rect
        )