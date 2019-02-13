import palettes

from EventQueue import EventQueue
from LightStrip import LightStrip
from StartupUi import StartupUi
import Player


class PlayerKeyUi(StartupUi):
    def __init__(self, trellis, player):
        self.player = player

        x_range = range(4) if player.side == Player.SIDE_LEFT else range(7, 3, -1)
        self.key_x = 0 if player.side == Player.SIDE_LEFT else 7

        self.strips = [
            LightStrip(
                pixels=trellis.pixels,
                x_range=x_range,
                y_range=range(1),
                colors=palettes.RED_KEY,
                value=1,
            ),
            LightStrip(
                pixels=trellis.pixels,
                x_range=x_range,
                y_range=range(1, 2),
                colors=palettes.YELLOW_KEY,
                value=1,
            ),
            LightStrip(
                pixels=trellis.pixels,
                x_range=x_range,
                y_range=range(2, 3),
                colors=palettes.BLUE_KEY,
                value=1,
            ),
        ]

        self.update_strips(None)

    def render(self, t):
        for strip in self.strips:
            strip.render(t)

    def dirty(self):
        for strip in self.strips:
            strip.dirty = True

    def handle_keys(self, t, pressed, down, up):
        for key in down:
            (x, y) = key
            if x == self.key_x and y < len(self.strips):
                self.player.toggle_key(y)
                self.update_strips(t)

    def update_strips(self, t):
        for i in range(len(self.strips)):
            key = self.player.keys[i]
            strip = self.strips[i]

            if key and strip.value == 1:
                strip.set_value(4, t)
            elif not key and strip.value == 4:
                strip.set_value(1, t)

