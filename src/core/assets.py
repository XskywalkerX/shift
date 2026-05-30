import pygame
from pathlib import Path


class AssetLoader:
    def __init__(self):
        self.cache = {}

    def load_sprite(self, path, fallback_size=(40, 40), fallback_color=(255, 0, 255)):
        path = Path(path)

        if path.exists():
            image = pygame.image.load(path).convert_alpha()
            return image

        surface = pygame.Surface(fallback_size)
        surface.fill(fallback_color)
        return surface


assets = AssetLoader()