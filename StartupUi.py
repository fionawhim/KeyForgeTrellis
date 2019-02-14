import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
import App
from UiModule import UiModule
from LightStrip import LightStrip

EDGE_POSITIONS = (
    list((x, 0) for x in range(7))
    + list((7, y) for y in range(0, 3))
    + list((x, 3) for x in range(7, 0, -1))
    + list((0, y) for y in range(3, 0, -1))
)
EDGE_STRIP_TIME = 1


class StartupUi(UiModule):
    def __init__(self, trellis, app):
        super().__init__()

        self.app = app

        self.center_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(1, 7),
            y_range=range(1, 3),
            speed=0.1,
            colors=[
                fancy.CHSV(0, 0, 0.5),
                fancy.CHSV(0.5, 0.25, 0.25),
                fancy.CHSV(0.0, 0.25, 0.25),
                fancy.CHSV(0.2, 0.25, 0.25),
            ],
            palette_shift_speed=-4,
            value=12,
        )

        self.edge_strip = LightStrip(
            pixels=trellis.pixels,
            positions=EDGE_POSITIONS,
            speed=EDGE_STRIP_TIME * 0.6 / 20,
            colors=palettes.RED_KEY + palettes.BLUE_KEY + palettes.YELLOW_KEY,
            value=0,
        )

    def render(self, t):
        self.process_events(t)

        self.edge_strip.render(t)
        self.center_strip.render(t)

    def handle_keys(self, t, pressed, down, up):
        if len(pressed) > 0:
            self.app.start_transition(t, App.STATE_MAIN)

    def enter(self, t):
        self.center_strip.speed = 0.1

    def leave(self, t):
        self.center_strip.speed = 0.05
        self.center_strip.set_value(0, t)
        return 0.05 * 12
