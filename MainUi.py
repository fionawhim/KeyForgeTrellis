import time
import math
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
from LightStrip import LightStrip
from ChainsUi import ChainsUi
from EventQueue import EventQueue

SIDE_LEFT = 'left'
SIDE_RIGHT = 'right'

class PlayerKeyUi:
  def __init__(self, trellis, player):
    self.player = player

    x_range = range(4) if player.side == SIDE_LEFT else range(7, 3, -1)
    self.key_x = 0 if player.side == SIDE_LEFT else 7

    self.strips = [
      LightStrip(
        pixels = trellis.pixels,
        x_range = x_range,
        y_range = range(1),
        colors = palettes.RED_KEY,
        value = 1,
      ),
      LightStrip(
        pixels = trellis.pixels,
        x_range = x_range,
        y_range = range(1, 2),
        colors = palettes.YELLOW_KEY,
        value = 1,  
      ),
      LightStrip(
        pixels = trellis.pixels,
        x_range = x_range,
        y_range = range(2, 3),
        colors = palettes.BLUE_KEY,
        value = 1,
      )
    ]

    self.update_strips(None)

  def render(self, t = time.monotonic()):
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

class PlayerChainsUi:
  def __init__(self, trellis, app, main, player):
    self.app = app
    self.main = main
    self.player = player
    self.button_down_t = None

    self.mode = 'normal'

    if player.side == SIDE_LEFT:
      self.x_range = range(4)
      self.decrement_x = 0
      self.increment_x = 3
    else:
      self.x_range = range(7, 3, -1)
      self.decrement_x = 7
      self.increment_x = 4

    self.strip = LightStrip(
      pixels = trellis.pixels,
      x_range = self.x_range,
      y_range = range(3, 4),
      colors = palettes.CHAINS,
      value = 0,
    )

    self.update_strip()

  def render(self, t):
    self.strip.render(t)

  def dirty(self):
    self.strip.dirty = True

  def handle_keys(self, t, pressed, down, up):
    for key in down:
      (x, y) = key
      if y == 3:
        if x == self.increment_x:
          self.player.increase_chains()
          self.update_strip(t)
          self.main.show_chains(self.player)
        elif x == self.decrement_x:
          self.player.decrease_chains()
          self.update_strip(t)
          self.main.show_chains(self.player)

  def highlight_chains(self, t = None):
    self.strip.set_value(4, t)

  def update_strip(self, t = None):
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


class MainUi:
  def __init__(self, trellis, app):
    self.app = app
    self.trellis = trellis
    self.mode = 'summary'
    self.chains_ui = None

    self.keys_uis = []
    self.chains_uis = []
    self.last_chains_t = None

    self.events = EventQueue()
    self.events.add_task('highlight_chains', 0.25)
    self.events.add_task('reset_chains', 1)

    for p in app.players:
      self.keys_uis.append(PlayerKeyUi(trellis, p))
      self.chains_uis.append(PlayerChainsUi(trellis, app, self, p))
  
  def render(self, t = time.monotonic()):
    while 1:
      event = self.events.next_event(t)
      if event:
        self.dispatch_event(t, event)
      else:
        break

    if self.last_chains_t != None and t > self.last_chains_t + 2:
      self.back_to_summary()

    for ui in self.keys_uis:
      ui.render(t)

    if self.mode == 'summary':
      for ui in self.chains_uis:
        ui.render(t)
    elif self.mode == 'chains':
      self.chains_ui.render(t)

  def handle_keys(self, t, pressed, down, up):
    for ui in self.keys_uis:
      ui.handle_keys(t, pressed, down, up)
    for ui in self.chains_uis:
      ui.handle_keys(t, pressed, down, up)

  def show_chains(self, p):
    if self.mode != 'chains':
      self.chains_ui = ChainsUi(self.trellis, self.app, p)
      self.mode = 'chains'
    self.last_chains_t = time.monotonic()

  def back_to_summary(self):
    self.mode = 'summary'
    self.chains_ui = None
    self.last_chains_t = None

    for ui in self.keys_uis:
      ui.dirty()
    for ui in self.chains_uis:
      ui.dirty()

  def dispatch_event(self, t, event):
    if event == 'highlight_chains':
      for ui in self.chains_uis:
        ui.highlight_chains(t)
    elif event == 'reset_chains':
      for ui in self.chains_uis:
        ui.update_strip(t)
