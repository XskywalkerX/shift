import pygame

from src.core.state_machine import State
from src.core.fonts import get_font

from src.core.config import Config
from src.core.audio import AudioManager


class SettingsState(State):

    def __init__(self, game):

        super().__init__(game)

        self.font = get_font(48)

        self.small = get_font(28)

        self.options = [
            "Volume da Musica",
            "Volume dos Efeitos Sonoros",
            "Brilho"
        ]

        self.selected = 0

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    from src.states.menu import MenuState

                    self.game.state_machine.change_state(
                        MenuState(self.game)
                    )

                elif event.key == pygame.K_UP:

                    self.selected = (
                        self.selected - 1
                    ) % 3

                elif event.key == pygame.K_DOWN:

                    self.selected = (
                        self.selected + 1
                    ) % 3

                elif event.key == pygame.K_LEFT:

                    self.change_value(-0.05)

                elif event.key == pygame.K_RIGHT:

                    self.change_value(+0.05)

    def change_value(self, amount):

        if self.selected == 0:

            Config.music_volume = max(
                0,
                min(
                    1,
                    Config.music_volume + amount
                )
            )

            AudioManager.music_volume = (
                Config.music_volume
            )

        elif self.selected == 1:

            Config.sfx_volume = max(
                0,
                min(
                    1,
                    Config.sfx_volume + amount
                )
            )

            AudioManager.sfx_volume = (
                Config.sfx_volume
            )

        else:

            Config.brightness = max(
                0.2,
                min(
                    1.5,
                    Config.brightness + amount
                )
            )

        AudioManager.update_volumes()

    def update(self, dt):
        pass

    def draw_slider(
        self,
        screen,
        x,
        y,
        value
    ):

        pygame.draw.rect(
            screen,
            (80,80,80),
            (x, y, 300, 10)
        )

        pygame.draw.rect(
            screen,
            (255,200,80),
            (
                x,
                y,
                int(300 * value),
                10
            )
        )

    def render(self, screen):

        title = self.font.render(
            "SETTINGS",
            True,
            (255,255,255)
        )

        screen.blit(
            title,
            (100, 80)
        )

        values = [
            Config.music_volume,
            Config.sfx_volume,
            Config.brightness / 1.5
        ]

        for i, name in enumerate(self.options):

            color = (
                (255,220,80)
                if i == self.selected
                else
                (200,200,200)
            )

            text = self.small.render(
                name,
                True,
                color
            )

            screen.blit(
                text,
                (
                    120,
                    220 + i * 120
                )
            )

            self.draw_slider(
                screen,
                400,
                240 + i * 120,
                values[i]
            )