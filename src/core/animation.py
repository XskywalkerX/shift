class Animation:
    def __init__(self, frames, speed=0.1, loop=True):
        self.frames = frames
        self.speed = speed
        self.loop = loop

        self.current_frame = 0
        self.timer = 0

        self.finished = False

    def update(self, dt):
        self.timer += dt

        if self.timer >= self.speed:
            self.timer = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.timer = 0
        self.finished = False