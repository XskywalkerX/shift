import pygame

from src.core.state_machine import State


class CreditsState(State):
    def __init__(self, game):
        super().__init__(game)

        self.font = pygame.font.SysFont("consolas", 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                from src.states.menu import MenuState

                self.game.state_machine.change_state(MenuState(self.game))

    def update(self, dt):
        pass

    def render(self, screen):
        lines = [
            "SHIFT//WORLD",
            "",
            "Programming: You",
            "",
            "Reality Stability: CRITICAL FAILURE",
            "",
            "Press any key to return"
        ]

        total_height = len(lines) * 60
        start_y = (screen.get_height() - total_height) // 2

        for i, line in enumerate(lines):
            text = self.font.render(
                line,
                True,
                (255, 255, 255)
            )

            rect = text.get_rect(
                center=(
                    screen.get_width() // 2,
                    start_y + i * 60
                )
            )

            screen.blit(text, rect)