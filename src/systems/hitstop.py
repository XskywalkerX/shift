class Hitstop:
    def __init__(self):
        self.duration = 0

    def trigger(self, duration):
        self.duration = duration

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            return True

        return False