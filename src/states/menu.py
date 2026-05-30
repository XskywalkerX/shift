import pygame

from src.core.state_machine import State
from src.states.gameplay import GameplayState
from src.states.credits import CreditsState


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)

        self.font = pygame.font.SysFont("consolas", 72)
        self.small_font = pygame.font.SysFont("consolas", 32)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.state_machine.change_state(GameplayState(self.game))

                if event.key == pygame.K_c:
                    self.game.state_machine.change_state(CreditsState(self.game))

    def update(self, dt):
        pass

    def render(self, screen):
        title = self.font.render("SHIFT", True, (255, 255, 255))

        start = self.small_font.render("PRESS ENTER TO START", True, (255, 255, 255))
        credits = self.small_font.render("PRESS C FOR CREDITS", True, (150, 150, 150))

        screen.blit(title, (300, 200))
        screen.blit(start, (420, 400))
        screen.blit(credits, (430, 460))