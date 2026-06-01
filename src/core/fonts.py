import pygame

pygame.font.init()

FONT_SMALL = pygame.font.Font(
    "assets/fonts/Minecraft.ttf",
    24
)

FONT_MEDIUM = pygame.font.Font(
    "assets/fonts/Minecraft.ttf",
    36
)

FONT_BIG = pygame.font.Font(
    "assets/fonts/Minecraft.ttf",
    72
)

def get_font(size):
    return pygame.font.Font(
        "assets/fonts/Minecraft.ttf",
        size
    )