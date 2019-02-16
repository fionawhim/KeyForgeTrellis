import time
import math

from MainUi import MainUi
import Player
from PlayerKeyUi import PlayerKeyUi
from PlayerChainsUi import PlayerChainsUi
from ChainsUi import ChainsUi
from StartupUi import StartupUi

from EventQueue import EventQueue

TARGET_FPS = 1 / 30.0
KEY_CHECK_INTERVAL = 0.025

SHAKE_THRESHOLD = 4.0
FLIP_THRESHOLD = 8

STATE_STARTUP = 0
STATE_MAIN = 1
STATE_PICK_START_PLAYER = 2
STATE_EDIT_CHAINS = 3


class App:
    def __init__(self, trellis, accelerometer):
        self.trellis = trellis
        self.accelerometer = accelerometer

        self.players = [
            Player.Player(Player.SIDE_LEFT),
            Player.Player(Player.SIDE_RIGHT),
        ]

        self.current_player = self.players[0]

        self.events = EventQueue()
        self.pressed = set()
        self.axis_reading = [ None, None, None ]

        self.state = None
        self.transitioning = False

        self.startup_ui = StartupUi(trellis=trellis, app=self)

        self.left_player_ui = PlayerKeyUi(trellis=trellis, player=self.players[0])
        self.right_player_ui = PlayerKeyUi(trellis=trellis, player=self.players[1])
        self.left_chains_ui = PlayerChainsUi(
            trellis=trellis, app=self, player=self.players[0]
        )
        self.right_chains_ui = PlayerChainsUi(
            trellis=trellis, app=self, player=self.players[1]
        )
        self.chains_ui = ChainsUi(trellis, self)

        self.active_modules_by_state = [
            # Startup
            [self.startup_ui],
            # Main
            [
                self.left_player_ui,
                self.right_player_ui,
                self.left_chains_ui,
                self.right_chains_ui,
            ],
            # Pick first player
            [],
            # Chains
            [self.chains_ui],
        ]

        # self.events.add_task(("finish_transition", STATE_EDIT_CHAINS), 0)
        self.events.add_task(("finish_transition", STATE_MAIN), 0)

    def run(self):
        self.trellis.pixels.auto_write = False

        last_pressed_t = 0

        fps = 0
        fps_t = time.monotonic()

        while True:
            t = time.monotonic()

            modules = (
                self.active_modules_by_state[self.state] if self.state != None else []
            )

            while 1:
                event = self.events.next_event(t)
                if event:
                    self.dispatch_event(t, event)
                else:
                    break

            if t >= last_pressed_t + KEY_CHECK_INTERVAL and not self.transitioning:
                pressed = set(self.trellis.pressed_keys)

                down = pressed - self.pressed
                up = self.pressed - pressed

                for m in modules:
                    m.handle_keys(t, pressed=pressed, down=down, up=up)

                self.pressed = pressed

                """Detect when the Trellis is shaken.
                See http://www.profoundlogic.com/docs/display/PUI/Accelerometer+Test+for+Shaking
                TL;DR one or more axis experiences a significant (set by bound) change very quickly
                Returns whether a shake was detected.
                """
                shaken = False
                x, y, z = self.accelerometer.acceleration
                if self.axis_reading[0] is not None:
                    shaken = (math.fabs(self.axis_reading[0] - x) > SHAKE_THRESHOLD and
                                math.fabs(self.axis_reading[1] - y) > SHAKE_THRESHOLD and
                                math.fabs(self.axis_reading[2] - z) > SHAKE_THRESHOLD)
                self.axis_reading = (x, y, z)
                if shaken:
                    self.start_transition(t, STATE_MAIN)
                elif z > FLIP_THRESHOLD:
                    self.start_transition(t, STATE_STARTUP)
                
                last_pressed_t = t

            for m in modules:
                m.render(t)
            self.trellis.pixels.show()

            t_diff = time.monotonic() - t
            if t_diff < TARGET_FPS:
                time.sleep(TARGET_FPS - t_diff)

            fps = fps + 1

            if t > fps_t + 1:
                print("FPS: ", fps / (t - fps_t), t)
                fps = 0
                fps_t = t

    def show_chains(self, t, player):
        self.current_player = player
        self.start_transition(t, STATE_EDIT_CHAINS)

    def start_transition(self, t, new_state):
        if self.transitioning or new_state == self.state:
            return

        self.transitioning = True

        current_modules = set(self.active_modules_by_state[self.state])
        new_modules = set(self.active_modules_by_state[new_state])

        leaving_modules = current_modules - new_modules
        leaving_delay = 0

        for m in leaving_modules:
            d = m.leave(t)
            leaving_delay = max(leaving_delay, d)

        self.events.add_task(("finish_transition", new_state), leaving_delay, t)

    def finish_transition(self, t, new_state):
        current_modules = (
            set(self.active_modules_by_state[self.state])
            if self.state != None
            else set()
        )
        new_modules = set(self.active_modules_by_state[new_state])

        entering_modules = new_modules - current_modules

        for m in entering_modules:
            m.enter(t)

        self.transitioning = False
        self.state = new_state

    def dispatch_event(self, t, event):
        if event[0] == "finish_transition":
            self.finish_transition(t, event[1])

