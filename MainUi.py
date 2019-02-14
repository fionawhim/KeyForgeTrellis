import time
import math
import random
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
from LightStrip import LightStrip
from ChainsUi import ChainsUi
from EventQueue import EventQueue



class FirstPlayerUi:
    def __init__(self, trellis, app, main_ui, player):
        self.player = player

        if player.side == SIDE_LEFT:
            self.x_range = range(1, 4)
        else:
            self.x_range = range(6, 3, -1)

        self.strip = LightStrip(
            pixels=trellis.pixels,
            x_range=self.x_range,
            y_range=range(0, 3),
            speed=None,
            colors=[fancy.CHSV(0, 0, 0.5), fancy.CHSV(0.5, 0.25, 0.25)],
            palette_shift_speed=-4,
            value=9,
        )

    def render(self, t):
        if self.player.is_first:
            self.strip.set_value(9, t)
        else:
            self.strip.set_value(0, t)
        self.strip.render(t)


class MainUi:
    def __init__(self, trellis, app):
        self.app = app
        self.trellis = trellis

        self.reset()

    def reset(self):
        self.mode = "summary"
        self.chains_ui = None

        self.keys_uis = []
        self.chains_uis = []
        self.first_player_uis = []

        self.events = EventQueue()
        self.events.add_task("highlight_chains", 0.25)
        self.events.add_task("reset_chains", 1)

        self.reset_strip = LightStrip(
            pixels=self.trellis.pixels,
            x_range=range(3, 5),
            y_range=range(0, 1),
            colors=[
                fancy.CHSV(2.2 / 6, 1.0, 0.5),
                fancy.CHSV(2.2 / 6, 0.25, 0.25),
                fancy.CHSV(2.2 / 6, 0.25, 0.25),
            ],
            palette_shift_speed=-0.5,
            palette_scale=0.25,
            background_color=None,
            value=0,
        )

        for p in self.app.players:
            p.reset()
            self.keys_uis.append(PlayerKeyUi(self.trellis, p))
            self.chains_uis.append(PlayerChainsUi(self.trellis, self.app, self, p))
            self.first_player_uis.append(FirstPlayerUi(self.trellis, self.app, self, p))

        self.events.add_task("start_choose_first_player", 2)

    def render(self, t):
        while 1:
            event = self.events.next_event(t)
            if event:
                self.dispatch_event(t, event)
            else:
                break

        for ui in self.keys_uis:
            ui.render(t)

        if self.mode == "summary":
            for ui in self.chains_uis:
                ui.render(t)
            for ui in self.first_player_uis:
                ui.render(t)
            self.reset_strip.render(t)
        elif self.mode == "chains":
            self.chains_ui.render(t)

    def handle_keys(self, t, pressed, down, up):
        if self.mode == "summary":
            if (3, 0) in down and (4, 0) in down:
                self.reset_strip.set_value(t, 2)
            if (
                (3, 0) not in pressed
                and (4, 0) not in pressed
                and self.reset_strip.value > 0
            ):
                self.reset()

            if len(down) > 0:
                for p in self.app.players:
                    if p.is_first:
                        p.is_first = False
                        return

        for ui in self.keys_uis:
            ui.handle_keys(t, pressed, down, up)
        for ui in self.chains_uis:
            ui.handle_keys(t, pressed, down, up)

    def show_chains(self, p):
        if self.mode != "chains":
            self.chains_ui = ChainsUi(self.trellis, self.app, p)
            self.mode = "chains"
        try:
            self.events.remove_task("close_chains")
            self.events.remove_task("back_to_summary")
        except KeyError:
            pass
        self.events.add_task("close_chains", 1.5)

    def back_to_summary(self):
        self.mode = "summary"
        self.chains_ui = None

        for ui in self.keys_uis:
            ui.dirty()
        for ui in self.chains_uis:
            ui.dirty()

    def dispatch_event(self, t, event):
        if event == "highlight_chains":
            for ui in self.chains_uis:
                ui.highlight_chains(t)
        elif event == "reset_chains":
            for ui in self.chains_uis:
                ui.update_strip(t)
        elif event == "close_chains":
            wait = self.chains_ui.close(t)
            self.events.add_task("back_to_summary", wait, t)
        elif event == "back_to_summary":
            self.back_to_summary()
        elif event == "start_choose_first_player":
            random.choice(self.app.players).is_first = True
            self.first_player_choice_delay = 0.5
            self.events.add_task("cycle_first_player", self.first_player_choice_delay)
        elif event == "cycle_first_player":
            for p in self.app.players:
                p.is_first = not p.is_first
            if self.first_player_choice_delay > 0.0005 or random.random() >= 0.25:
                self.first_player_choice_delay = self.first_player_choice_delay * 0.8
                self.events.add_task(
                    "cycle_first_player", self.first_player_choice_delay
                )

