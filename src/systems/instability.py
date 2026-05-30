class Instability:
    def __init__(self):
        self.level = 0

    def update(self, dt):
        self.level += dt * 2