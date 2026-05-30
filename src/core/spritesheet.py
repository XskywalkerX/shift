import pygame


class SpriteSheet:
    def __init__(self, image_path):
        self.sheet = pygame.image.load(
            image_path
        ).convert_alpha()

    def get_frames(self, frame_width, frame_height):
        frames = []

        sheet_width = self.sheet.get_width()

        for x in range(0, sheet_width, frame_width):
            frame = pygame.Surface(
                (frame_width, frame_height),
                pygame.SRCALPHA
            )

            frame.blit(
                self.sheet,
                (0, 0),
                (x, 0, frame_width, frame_height)
            )

            frames.append(frame)

        return frames