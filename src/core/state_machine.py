class State:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass


class StateMachine:
    def __init__(self):
        self.current_state = None

    def change_state(self, state):
        self.current_state = state

    def handle_events(self, events):
        if self.current_state:
            self.current_state.handle_events(events)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def render(self, screen):
        if self.current_state:
            self.current_state.render(screen)