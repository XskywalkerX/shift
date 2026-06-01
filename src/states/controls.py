import pygame
import os

from src.core.state_machine import State
from src.core.fonts import get_font


class ControlsState(State):

    def __init__(self, game):
        super().__init__(game)

        self.title_font = get_font(72)
        self.text_font = get_font(28)

        # =========================
        # GIF DO MENU
        # =========================

        self.frames = []

        self.scroll_y = 0

        folder = "assets/background/"

        files = sorted(
            [
                f for f in os.listdir(folder)
                if f.startswith("frame")
                and f.endswith(".png")
            ]
        )

        for file in files:
            self.frames.append(
                pygame.image.load(
                    os.path.join(folder, file)
                ).convert()
            )

        self.frame_index = 0
        self.frame_timer = 0

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_y += event.y * 40

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    self.scroll_y += 40

                elif event.key == pygame.K_DOWN:
                    self.scroll_y -= 40

                elif event.key == pygame.K_ESCAPE:

                    from src.states.menu import MenuState

                    self.game.state_machine.change_state(
                        MenuState(self.game)
                    )

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    from src.states.menu import MenuState

                    self.game.state_machine.change_state(
                        MenuState(self.game)
                    )

    def update(self, dt):

        self.frame_timer += dt

        if self.frame_timer >= 0.08:

            self.frame_timer = 0

            self.frame_index = (
                self.frame_index + 1
            ) % len(self.frames)

        self.scroll_y = min(self.scroll_y, 0)

        min_scroll = -800  # ajuste conforme necessário

        self.scroll_y = max(
            self.scroll_y,
            min_scroll
        )

    def render(self, screen):

        # =========================
        # BACKGROUND
        # =========================

        bg = pygame.transform.scale(
            self.frames[self.frame_index],
            screen.get_size()
        )

        screen.blit(bg, (0, 0))

        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 180))

        screen.blit(overlay, (0, 0))

        # =========================
        # TÍTULO
        # =========================

        title = self.title_font.render(
            "CONTROLES",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2
                - title.get_width() // 2,
                60
            )
        )

        # =========================
        # TEXTOS
        # =========================

        lines = [

            "MOVIMENTAÇÃO",
            "",
            "W A S D  -  Movimentar personagem",
            "ESPAÇO  -  Pular",
            "SHIFT  -  Dash",
            "",
            "COMBATE",
            "",
            "Clique Esquerdo  -  Ataque Primário",
            "Clique Direito  -  Ataque Secundário",
            "",
            "MUNDO",
            "",
            "TAB  -  SWAP",
            "",
            "SWAP significa alternar entre",
            "o Mundo Plataforma e o Mundo Shooter.",
            "",
            "No Mundo Plataforma:",
            "- Plataformas aparecem",
            "- Combate corpo a corpo",
            "",
            "No Mundo Shooter:",
            "- Obstáculos aparecem",
            "- Arma de longo alcance",
            "",
            "OUTROS",
            "",
            "ESC  -  Pausar jogo",
            "",
            "Pressione ESC para voltar"
        ]

        y = 170 + self.scroll_y

        for text in lines:

            if text in [
                "MOVIMENTAÇÃO",
                "COMBATE",
                "MUNDO",
                "OUTROS"
            ]:
                color = (255, 210, 80)
            else:
                color = (255, 255, 255)

            rendered = self.text_font.render(
                text,
                True,
                color
            )

            if -50 < y < screen.get_height() + 50:

                screen.blit(
                    rendered,
                    (
                        screen.get_width() // 2
                        - rendered.get_width() // 2,
                        y
                    )
                )

            y += 34