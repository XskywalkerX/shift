import pygame

pygame.init()

info = pygame.display.Info()

WIDTH = info.current_w
HEIGHT = info.current_h

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