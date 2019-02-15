import palettes
import Player

from EventQueue import EventQueue
from LightStrip import LightStrip
from UiModule import UiModule


class PlayerChainsUi(UiModule):
    def __init__(self, trellis, app, player):
        super().__init__()

        self.app = app
        self.player = player

        if player.side == Player.SIDE_LEFT:
            self.x_range = range(4)
        else:
            self.x_range = range(7, 3, -1)

        self.strip = LightStrip(
            pixels=trellis.pixels,
            x_range=self.x_range,
            y_range=range(3, 4),
            colors=palettes.CHAINS,
            speed=0.1,
            value=0,
        )

    def render(self, t):
        self.process_events(t)
        self.strip.render(t)


    def handle_keys(self, t, pressed, down, up):
        for (x, y) in down:
            if y == 3 and x in self.x_range:
                self.strip.set_highlight((x, y), t)
                self.events.add_task("show_chains", 0.25, t)

    def highlight(self, t):
        self.strip.set_value(4, t)
        self.events.add_task("update_strip", 1, t)

    def enter(self, t):
        self.strip.highlight = None
        self.update_strip(t)

    def leave(self, t):
        self.strip.set_value(0, t)
        return 0.5

    def update_strip(self, t=None):
        if self.player.chains == 0:
            self.strip.set_value(0, t)
        elif self.player.chains <= 6:
            self.strip.set_value(1, t)
        elif self.player.chains <= 12:
            self.strip.set_value(2, t)
        elif self.player.chains <= 18:
            self.strip.set_value(3, t)
        else:
            self.strip.set_value(4, t)

    def dispatch_event(self, t, event):
        if event == "update_strip":
            self.update_strip(t)
        elif event == "show_chains":
            self.app.show_chains(t, self.player)
