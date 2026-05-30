import random


class ScreenShake:
    def __init__(self):
        self.intensity = 0

    def trigger(self, amount):
        self.intensity = amount

    def update(self):
        if self.intensity > 0:
            self.intensity *= 0.9

        return (
            random.uniform(
                -self.intensity,
                self.intensity
            ),
            random.uniform(
                -self.intensity,
                self.intensity
            )
        )