import time
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
import App
import Player
from LightStrip import LightStrip
from UiModule import UiModule

BLUE_WITH_WHITE_HIGHLIGHT_PALETTE = [
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.7, 1.0),
    fancy.CHSV(4 / 6.0, 0.0, 1.0),
]

CHAIN_STRIP_SPEED = 0.02


class ChainsUi(UiModule):
    def __init__(self, trellis, app):
        super().__init__()

        self.app = app

        # if player.side == "left":
        #     player_x = range(7, 8)
        #     controls_x = range(7, 8)
        #     chains_x = range(1, 7)
        # else:
        #     player_x = range(0, 1)
        #     controls_x = range(0, 1)
        #     chains_x = range(6, 0, -1)

        self.player_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(0, 1),
            y_range=range(0, 4),
            colors=BLUE_WITH_WHITE_HIGHLIGHT_PALETTE,
            value=4,
            brightness=0.6,
            palette_shift_speed=-2,
            palette_scale=0.2,
        )

        self.chain_bg_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(1, 7),
            y_range=range(0, 4),
            colors=[fancy.CHSV(4 / 6.0, 0.3, 0.2)],
            brightness=0.8,
            speed=0.01,
            # palette_shift_speed=-10,
            value=0,
        )

        self.chain_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(1, 7),
            y_range=range(0, 4),
            colors=palettes.CHAINS,
            brightness=0.8,
            speed=CHAIN_STRIP_SPEED,
            value=0,
            background_color=None,
            highlight_color=fancy.CHSV(0, 0.8, 0.0),
            highlight_speed=0.25,
        )

        self.button_strip = LightStrip(
            pixels=trellis.pixels,
            x_range=range(1, 7),
            y_range=range(3, 4),
            colors=palettes.CHAINS,
            brightness=0.8,
            speed=CHAIN_STRIP_SPEED,
            value=0,
            background_color=None,
            highlight_color=fancy.CHSV(0, 0.5, 1.0),
            highlight_speed=None,
        )

        self.strips = [
            self.player_strip,
            self.chain_bg_strip,
            self.chain_strip,
            self.button_strip,
        ]

    def render(self, t):
        self.process_events(t)
        for strip in self.strips:
            strip.render(t)

    def enter(self, t):
        p = self.app.current_player

        x_range = range(0, 1) if p.side == Player.SIDE_LEFT else range(7, 8)

        self.player_strip.set_position(x_range, range(0, 4))
        self.player_strip.set_value(4)
        self.player_strip.highlight = None
        self.chain_bg_strip.set_value(24)
        self.chain_strip.set_value(p.chains, t)
        self.chain_strip.background_color = None
        self.chain_strip.highlight_color = fancy.CHSV(0, 0.8, 0.0)
        self.chain_strip.highlight_speed = 0.25
        self.button_strip.highlight = None

        self.initial_chains = p.chains

        self.events.add_task("exit", 5, t)

        if p.chains > 0:
            for (x, y) in self.app.pressed:
                if y == 3:
                    self.button_strip.set_highlight((x, y), t)
                    self.events.add_task("decrement_chain", 1.5, t)

    def leave(self, t):
        self.chain_strip.set_value(0)
        self.chain_strip.background_color = None
        self.chain_bg_strip.set_value(0, t)
        self.chain_strip.clear_highlight()
        self.player_strip.set_value(0, t)
        return 0.25

    def handle_keys(self, t, pressed, down, up):
        p = self.app.current_player

        if len(pressed) > 0:
            try:
                self.events.remove_task("exit")
            except KeyError:
                pass
        elif len(up) > 0:
            self.events.add_task("exit", 5, t)

        if len(pressed) == 1:
            for (x, y) in down:
                if x == 0 or x == 7:
                    self.player_strip.set_highlight((x, y), t)
                else:
                    new_chains = y * 6 + x
                    if new_chains == 1 and p.chains == 1:
                        p.chains = 0
                    else:
                        p.chains = new_chains

                    self.chain_strip.background_color = self.chain_bg_strip.colors[0]
                    if p.chains < self.initial_chains:
                        self.chain_strip.set_highlight(
                            list(range(p.chains + 1, self.initial_chains + 1)), t
                        )
                        self.chain_strip.highlight_color = fancy.CHSV(0, 0, 0.0)
                        self.chain_strip.highlight_speed = 0.75
                    elif p.chains > self.initial_chains:
                        self.chain_strip.set_highlight(
                            list(range(self.initial_chains + 1, p.chains + 1)), t
                        )
                        self.chain_strip.highlight_color = fancy.CHSV(0.9, 1.0, 1.0)
                        self.chain_strip.highlight_speed = 10
                    else:
                        self.chain_strip.clear_highlight()

        for (x, y) in up:
            if (
                self.button_strip.highlight != None
                and (x, y) == self.button_strip.highlight[0]
            ):
                self.button_strip.clear_highlight()
                self.chain_bg_strip.dirty = True
                self.chain_strip.dirty = True
                try:
                    self.events.remove_task("decrement_chain")
                except KeyError:
                    print("DECREASE CHAINS?")
                    p.decrease_chains()
                    self.chain_strip.set_value(p.chains)
                    self.chain_strip.clear_highlight()
                    self.chain_bg_strip.dirty = True
                    self.events.add_task("exit", 0.75)

            if x == 0 or x == 7:
                self.player_strip.highlight = None
                self.app.start_transition(t, App.STATE_MAIN)

    def dispatch_event(self, t, event):
        if event == "decrement_chain":
            p = self.app.current_player
            self.chain_strip.set_highlight(p.chains)
        elif event == "exit":
            self.app.start_transition(t, App.STATE_MAIN)

