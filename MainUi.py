import time
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
from LightStrip import LightStrip

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
  def __init__(self, trellis, app, player):
    self.app = app
    self.player = player
    self.button_down_t = None

    self.mode = 'normal'

    if player.side == SIDE_LEFT:
      self.x_range = range(4)
    else:
      self.x_range = range(7, 3, -1)

    self.strip = LightStrip(
      pixels = trellis.pixels,
      x_range = self.x_range,
      y_range = range(3, 4),
      colors = palettes.CHAINS,
      value = 0,
    )

    self.decrement_strip = LightStrip(
      pixels = trellis.pixels,
      x_range = self.x_range,
      y_range = range(3, 4),
      colors = [
        fancy.CHSV(2.2/6, 1.0, 0.5),
        fancy.CHSV(2.2/6, 0.25, 0.25),
        fancy.CHSV(2.2/6, 0.25, 0.25),
        fancy.CHSV(2.2/6, 0.25, 0.25),
        fancy.CHSV(2.2/6, 0.25, 0.25),
        fancy.CHSV(2.2/6, 0.25, 0.25),
        fancy.CHSV(2.2/6, 0.25, 0.25),
        fancy.CHSV(2.2/6, 0.25, 0.25),
      ],
      palette_shift_speed = 0.5,
      palette_scale = 0.6,
      speed = 0.000001,
      value = 4,
    )

    self.update_strip()

  def render(self, t): 
    if self.mode == 'normal':
      if self.button_down_t != None and t > self.button_down_t + 0.4 and self.player.chains > 0:
        self.mode = 'chain_down'
        self.player.decrease_chains()
        self.decrement_strip.set_value(4, t)
        self.update_strip()
      self.strip.render(t)
    elif self.mode == 'chain_down':
      self.decrement_strip.render(t)

  def handle_keys(self, t, pressed, down, up):
    for key in down:
      (x, y) = key
      if y == 3 and x in self.x_range:
        self.button_down_t = t

    for key in up:
      (x, y) = key
      if y == 3 and x in self.x_range:
        if self.button_down_t != None:
          self.button_down_t = None
          if self.mode == 'normal':
            self.app.switch_ui('chains', self.player)
          else:
            self.mode = 'normal'
            self.strip.set_value(-1)
            self.strip.render(t)
            self.update_strip(t)

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
    self.children = []

    for p in app.players:
      self.children.append(PlayerKeyUi(trellis, p))
      self.children.append(PlayerChainsUi(trellis, app, p))
  
  def render(self, t = time.monotonic()):
    for p in self.children:
      p.render(t)

  def handle_keys(self, t, pressed, down, up):
    for p in self.children:
      p.handle_keys(t, pressed, down, up)