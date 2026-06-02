import pygame
import asyncio

from settings import *
from src.core.state_machine import StateMachine
from src.states.menu import MenuState


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.state_machine = StateMachine()
        self.state_machine.change_state(MenuState(self))

    async def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.state_machine.handle_events(events)
            self.state_machine.update(dt)

            self.screen.fill(BG_COLOR)
            self.state_machine.render(self.screen)

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()