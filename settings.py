import pygame

print("pygame =", pygame)
print("pygame file =", getattr(pygame, "__file__", None))
print("pygame version =", getattr(pygame, "__version__", None))
print("has init =", hasattr(pygame, "init"))

if hasattr(pygame, "init"):
    pygame.init()

WIDTH = 1280
HEIGHT = 720

WORLD_WIDTH = 1200
WORLD_HEIGHT = 1200

FPS = 60

TITLE = "SHIFT"

BG_COLOR = (10, 10, 15)

SHOOTER_COLOR = (255, 80, 80)
PLATFORM_COLOR = (100, 140, 255)

PLAYER_SIZE = 40
PLAYER_SPEED = 6
PLAYER_JUMP = -15
GRAVITY = 0.8

WORLD_SWAP_COOLDOWN = 400