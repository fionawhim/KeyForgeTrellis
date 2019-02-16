import time
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
import App
import Player
from LightStrip import LightStrip
from UiModule import UiModule

CHAIN_STRIP_SPEED = 0.02
CHAIN_INTERACTIVE_SPEED = 0.08


class ChainsUi(UiModule):
    def __init__(self, trellis, app):
        super().__init__()

        self.app = app

        # Used to animate the box going away
        self.chain_bg_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(1, 7),
            y_range=range(0, 4),
            colors=[fancy.CHSV(0, 0, 0.0)],
            brightness=0.8,
            speed=CHAIN_STRIP_SPEED,
            background_color=None,
            value=0,
        )

        self.chain_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(1, 7),
            y_range=range(0, 4),
            colors=palettes.CHAINS,
            brightness=0.8,
            speed=CHAIN_STRIP_SPEED,
            value=-1,
            background_color=fancy.CHSV(4 / 6.0, 0.3, 0.2),
            highlight_color=fancy.CHSV(0, 0.8, 0.0),
            highlight_speed=0.25,
        )

        self.strips = [self.chain_strip, self.chain_bg_strip]

    def render(self, t):
        self.process_events(t)
        for strip in self.strips:
            strip.render(t)

    def enter(self, t):
        super().enter(t)

        p = self.app.current_player

        self.x_range = range(0, 6) if p.side == Player.SIDE_LEFT else range(7, 1, -1)
        self.y_range = range(0, 4)

        self.chain_strip.set_position(x_range=self.x_range, y_range=self.y_range)
        self.chain_bg_strip.set_position(x_range=self.x_range, y_range=self.y_range)

        self.chain_bg_strip.set_value(0)
        self.chain_strip.speed = CHAIN_STRIP_SPEED
        self.chain_strip.set_value(p.chains, t, now=True)
        self.chain_strip.dirty = True

        self.chain_strip.highlight_color = fancy.CHSV(0, 0.8, 0.0)
        self.chain_strip.highlight_speed = 0.25

        self.decrement_button = None

        for (x, y) in self.app.pressed:
            if y == 3 and p.chains > 0:
                self.decrement_button = x
                self.events.add_task("decrement_chain", 0.5, t)

    def leave(self, t):
        super().leave(t)

        self.chain_bg_strip.set_value(24, t)
        self.chain_strip.clear_highlight()
        return 0.25

    def handle_keys(self, t, pressed, down, up):
        p = self.app.current_player

        if len(pressed) > 0:
            try:
                self.events.remove_task("exit")
            except KeyError:
                pass

        if len(pressed) == 1:
            for (x, y) in down:
                if x in self.x_range:
                    new_chains = y * 6 + list(self.x_range).index(x) + 1

                    # If you're on 1, toggle it to 0 because otherwise there’s
                    # no other way to get to 0.
                    if new_chains == 1 and p.chains == 1:
                        p.chains = 0
                    else:
                        p.chains = new_chains

                    self.chain_strip.speed = CHAIN_INTERACTIVE_SPEED
                    self.chain_strip.set_value(p.chains, t)
                else:
                    self.app.start_transition(t, App.STATE_MAIN)

        for (x, y) in up:
            if x == self.decrement_button and y == 3:
                self.chain_bg_strip.dirty = True
                self.chain_strip.dirty = True
                try:
                    self.events.remove_task("decrement_chain")
                except KeyError:
                    # If we key error, it means that the decrement_chain went off
                    p.decrease_chains()
                    self.chain_strip.set_value(p.chains)
                    self.chain_strip.clear_highlight()
                    self.chain_bg_strip.dirty = True
                    self.events.add_task("exit", 0.75)
            else:
                self.events.add_task("exit", 2.5, t)

    def dispatch_event(self, t, event):
        if event == "decrement_chain":
            p = self.app.current_player
            self.chain_strip.set_highlight(p.chains)
        elif event == "exit":
            self.app.start_transition(t, App.STATE_MAIN)

