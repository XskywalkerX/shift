import pygame

from src.states.menu import MenuState
from src.states.gameplay import GameplayState


class DeathState:

    def __init__(self, game):

        self.game = game

        self.font = pygame.font.SysFont(
            None,
            72
        )

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    self.game.state_machine.change_state(
                        GameplayState(self.game)
                    )

                elif event.key == pygame.K_ESCAPE:

                    self.game.state_machine.change_state(
                        MenuState(self.game)
                    )

    def update(self, dt):
        pass

    def render(self, screen):

        screen.fill((0, 0, 0))

        title = self.font.render(
            "VOCÊ MORREU :D",
            True,
            (255, 0, 0)
        )

        screen.blit(
            title,
            (
                400,
                200
            )
        )