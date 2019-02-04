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

  def render(self, t):
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
          self.main.show_chains(self.player)
          self.player.increase_chains()
          self.update_strip(t)
        elif x == self.decrement_x:
          self.main.show_chains(self.player)
          self.player.decrease_chains()
          self.update_strip(t)

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

    self.events = EventQueue()
    self.events.add_task('highlight_chains', 0.25)
    self.events.add_task('reset_chains', 1)

    for p in app.players:
      self.keys_uis.append(PlayerKeyUi(trellis, p))
      self.chains_uis.append(PlayerChainsUi(trellis, app, self, p))
  
  def render(self, t):
    while 1:
      event = self.events.next_event(t)
      if event:
        self.dispatch_event(t, event)
      else:
        break

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
    try:
      self.events.remove_task('close_chains')
      self.events.remove_task('back_to_summary')
    except KeyError:
      pass
    self.events.add_task('close_chains', 1.5)

  def back_to_summary(self):
    self.mode = 'summary'
    self.chains_ui = None

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
    elif event == 'close_chains':
      wait = self.chains_ui.close(t)
      self.events.add_task('back_to_summary', wait, t)
    elif event == 'back_to_summary':
      self.back_to_summary()
  
