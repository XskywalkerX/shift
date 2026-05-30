import pygame

class Obstacle:

    def __init__(self, x, y, w, h, sprite=None):

        self.rect = pygame.Rect(x, y, w, h)

        self.sprite = sprite

        if self.sprite:
            self.sprite = pygame.transform.scale(
                self.sprite,
                (w, h)
            )

    def render(self, screen):

        if self.sprite:

            screen.blit(
                self.sprite,
                self.rect
            )

        else:

            pygame.draw.rect(
                screen,
                (120, 120, 120),
                self.rect
            )