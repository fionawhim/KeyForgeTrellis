import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
import App
from UiModule import UiModule
from LightStrip import LightStrip


class StartupUi(UiModule):
    def __init__(self, trellis, app):
        self.app = app

        self.strip = LightStrip(
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

    def render(self, t):
        self.strip.render(t)

    def handle_keys(self, t, pressed, down, up):
        if len(pressed) > 0:
            self.app.start_transition(t, App.STATE_MAIN)

    def leave(self, t):
        self.strip.set_value(0, t)
        return 1.2
