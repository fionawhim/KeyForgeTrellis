import palettes
import Player

from EventQueue import EventQueue
from LightStrip import LightStrip
from UiModule import UiModule


class PlayerKeyUi(UiModule):
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

        self.strips = []

        self.update_strips(None)

    def render(self, t):
        for strip in self.strips:
            strip.render(t)

    def handle_keys(self, t, pressed, down, up):
        for key in down:
            (x, y) = key
            if x == self.key_x and y < len(self.strips):
                self.player.toggle_key(y)
                self.update_strips(t)

    def enter(self, t):
        for s in self.strips:
            s.dirty = True
        self.update_strips(t)

    def leave(self, t):
        for strip in self.strips:
            strip.set_value(0, t)
        return 0.25

    def update_strips(self, t):
        for i in range(len(self.strips)):
            key = self.player.keys[i]
            strip = self.strips[i]

            if key:
                strip.set_value(4, t)
                strip.palette_shift_speed = -30
            else:
                strip.set_value(1, t)
                strip.palette_shift_speed = None

