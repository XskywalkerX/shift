import pygame

from settings import *

from src.core.state_machine import State
from src.states.gameplay import GameplayState
from src.states.credits import CreditsState
from src.states.configurations import SettingsState
from src.states.controls import ControlsState

from src.core.fonts import get_font


class MenuState(State):

    def __init__(self, game):
        super().__init__(game)

        # ==========================
        # MENU OPTIONS
        # ==========================

        self.options = [
            "JOGAR",
            "CONTROLES",
            "CREDITOS",
            "CONFIGURAR"
        ]

        self.selected = 0

        # ==========================
        # FONTS
        # ==========================

        self.title_font = get_font(120)
        self.option_font = get_font(42)
        self.small_font = get_font(24)

        # ==========================
        # BACKGROUND ANIMATION
        # ==========================

        self.menu_frames = []

        FRAME_COUNT = 20  # altere para quantidade real

        for i in range(FRAME_COUNT):

            image = pygame.image.load(
                f"assets/background/frame_{i}_delay-0.1s.png"
            ).convert()

            image = pygame.transform.scale(
                image,
                (WIDTH, HEIGHT)
            )

            self.menu_frames.append(image)

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.08

        # ==========================
        # AUDIO
        # ==========================

        pygame.mixer.music.load(
            "assets/audio/menu_theme.ogg"
        )

        pygame.mixer.music.set_volume(0.5)

        pygame.mixer.music.play(-1)

        self.move_sound = pygame.mixer.Sound(
            "assets/audio/menu_move.ogg"
        )

        self.select_sound = pygame.mixer.Sound(
            "assets/audio/menu_select.ogg"
        )

        # ==========================
        # FADE TRANSITION
        # ==========================

        self.transitioning = False
        self.fade_alpha = 0

        self.next_state = None

    def start_transition(self, state):

        self.select_sound.play()

        self.transitioning = True
        self.fade_alpha = 0

        self.next_state = state

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:

                    self.selected -= 1

                    if self.selected < 0:
                        self.selected = len(self.options) - 1

                    self.move_sound.play()

                elif event.key == pygame.K_DOWN:

                    self.selected += 1

                    if self.selected >= len(self.options):
                        self.selected = 0

                    self.move_sound.play()

                elif event.key == pygame.K_RETURN:

                    option = self.options[self.selected]

                    if option == "JOGAR":

                        self.start_transition(
                            GameplayState(self.game)
                        )

                    elif option == "CREDITOS":

                        self.start_transition(
                            CreditsState(self.game)
                        )

                    elif option == "CONTROLES":

                        self.start_transition(
                            ControlsState(self.game)
                        )

                    elif option == "CONFIGURAR":

                        self.start_transition(
                            SettingsState(self.game)
                        )

    def update(self, dt):

        # ==========================
        # BACKGROUND ANIMATION
        # ==========================

        self.frame_timer += dt

        if self.frame_timer >= self.frame_speed:

            self.frame_timer = 0

            self.current_frame += 1

            if self.current_frame >= len(self.menu_frames):

                self.current_frame = 0

        # ==========================
        # FADE
        # ==========================

        if self.transitioning:

            self.fade_alpha += 400 * dt

            if self.fade_alpha >= 255:

                self.fade_alpha = 255

                self.game.state_machine.change_state(
                    self.next_state
                )

    def render(self, screen):

        # ==========================
        # ANIMATED BACKGROUND
        # ==========================

        screen.blit(
            self.menu_frames[self.current_frame],
            (0, 0)
        )

        # ==========================
        # DARK OVERLAY
        # ==========================

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 140)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        # ==========================
        # TITLE
        # ==========================

        title = self.title_font.render(
            "SHIFT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                100
            )
        )

        # ==========================
        # OPTIONS
        # ==========================

        start_y = 320

        for i, option in enumerate(self.options):

            selected = (i == self.selected)

            color = (
                (255, 220, 80)
                if selected
                else
                (180, 180, 180)
            )

            font = (
                get_font(50)
                if selected
                else
                self.option_font
            )

            text = font.render(
                option,
                True,
                color
            )

            screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    start_y + i * 75
                )
            )

        # ==========================
        # HELP TEXT
        # ==========================

        help_text = self.small_font.render(
            "UP / DOWN - Navigate     ENTER - Select",
            True,
            (180, 180, 180)
        )

        screen.blit(
            help_text,
            (
                WIDTH // 2 - help_text.get_width() // 2,
                HEIGHT - 60
            )
        )

        # ==========================
        # FADE EFFECT
        # ==========================

        if self.transitioning:

            fade = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            fade.fill((0, 0, 0))

            fade.set_alpha(
                int(self.fade_alpha)
            )

            screen.blit(
                fade,
                (0, 0)
            )