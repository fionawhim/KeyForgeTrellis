import time

from MainUi import MainUi
import Player
from PlayerKeyUi import PlayerKeyUi
from ChainsUi import ChainsUi
from StartupUi import StartupUi

from EventQueue import EventQueue

SIXTY_FPS = 1 / 60.0
KEY_CHECK_INTERVAL = 0.025

STATE_STARTUP = 0
STATE_MAIN = 1
STATE_PICK_START_PLAYER = 2
STATE_EDIT_CHAINS = 3


class App:
    def __init__(self, trellis):
        self.trellis = trellis
        self.players = [
            Player.Player(Player.SIDE_LEFT),
            Player.Player(Player.SIDE_RIGHT),
        ]

        self.events = EventQueue()

        self.state = None
        self.transitioning = False

        self.startup_ui = StartupUi(trellis=trellis, app=self)

        self.left_player_ui = PlayerKeyUi(trellis=trellis, player=self.players[0])
        self.right_player_ui = PlayerKeyUi(trellis=trellis, player=self.players[1])

        self.active_modules_by_state = [
            [self.startup_ui],
            [self.left_player_ui, self.right_player_ui],
        ]

        self.events.add_task(("finish_transition", STATE_STARTUP), 0)

    def run(self):
        self.trellis.pixels.auto_write = False

        last_pressed = set()
        last_pressed_t = 0

        fps = 0
        fps_t = time.monotonic()

        while True:
            t = time.monotonic()

            modules = self.active_modules_by_state[self.state] if self.state != None else []

            while 1:
                event = self.events.next_event(t)
                if event:
                    self.dispatch_event(t, event)
                else:
                    break

            if t >= last_pressed_t + KEY_CHECK_INTERVAL:
                pressed = set(self.trellis.pressed_keys)

                down = pressed - last_pressed
                up = last_pressed - pressed

                for m in modules:
                    m.handle_keys(t, pressed=pressed, down=down, up=up)

                last_pressed = pressed
                last_pressed_t = t

            for m in modules:
                m.render(t)
            self.trellis.pixels.show()

            t_diff = time.monotonic() - t
            if t_diff < SIXTY_FPS:
                time.sleep(SIXTY_FPS - t_diff)

            fps = fps + 1

            if t > fps_t + 1:
                print("FPS: ", fps / (t - fps_t), t)
                fps = 0
                fps_t = t

    def start_transition(self, t, new_state):
        if self.transitioning:
            return

        print("Starting transition to ", new_state)
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
        current_modules = set(self.active_modules_by_state[self.state]) if self.state != None else set()
        new_modules = set(self.active_modules_by_state[new_state])

        entering_modules = new_modules - current_modules

        for m in entering_modules:
            m.enter(t)

        self.transitioning = False
        self.state = new_state

    def dispatch_event(self, t, event):
        if event[0] == "finish_transition":
            self.finish_transition(t, event[1])

