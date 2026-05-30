import pygame
from src.core.state_machine import State

class PauseState(State):

    def __init__(self, game, previous_state):
        super().__init__(game)
        self.previous_state = previous_state
        self.font = pygame.font.SysFont("consolas", 50)

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.game.state_machine.change_state(self.previous_state)

    def update(self, dt):
        pass

    def render(self, screen):

        self.previous_state.render(screen)

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        text = self.font.render("PAUSED", True, (255, 255, 255))
        screen.blit(
            text,
            (
                screen.get_width()//2 - text.get_width()//2,
                screen.get_height()//2 - 40
            )
        )