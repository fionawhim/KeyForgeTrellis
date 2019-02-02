import time
import adafruit_fancyled.adafruit_fancyled as fancy

from LightStrip import LightStrip

RED_KEY_PALETTE = [fancy.CHSV(1.0, 0.5, 0.5), fancy.CHSV(1.0)]
YELLOW_KEY_PALETTE = [fancy.CHSV(1.0 / 6.0, 0.5, 0.5), fancy.CHSV(1.0 / 6.0)]
BLUE_KEY_PALETTE = [fancy.CHSV(0.6, 0.5, 0.5), fancy.CHSV(0.6)]

CHAINS_PALETTE = [
  fancy.CRGB(96, 149, 64),
  fancy.CRGB(234,209,83),
  fancy.CRGB(243,169,87),
  fancy.CRGB(178,31,31),
]

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
        colors = RED_KEY_PALETTE,
        value = 1,
      ),
      LightStrip(
        pixels = trellis.pixels,
        x_range = x_range,
        y_range = range(1, 2),
        colors = YELLOW_KEY_PALETTE,
        value = 1,  
      ),
      LightStrip(
        pixels = trellis.pixels,
        x_range = x_range,
        y_range = range(2, 3),
        colors = BLUE_KEY_PALETTE,
        value = 1,
      )
    ]

  def render(self, t = time.monotonic()):
    for strip in self.strips:
      strip.render(t)

  def handle_keys(self, t, pressed): 
    for key in pressed:
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
  def __init__(self, trellis, player):
    self.player = player

    if player.side == SIDE_LEFT:
      x_range = range(4)
      self.down_x = 0
      self.up_x = 3
    else:
      x_range = range(7, 3, -1)
      self.down_x = 7
      self.up_x = 4

    self.strip = LightStrip(
      pixels = trellis.pixels,
      x_range = x_range,
      y_range = range(3, 4),
      colors = CHAINS_PALETTE,
      value = 0,
    )

    self.update_strip()

  def render(self, t): 
    self.strip.render(t)

  def handle_keys(self, t, pressed):
    for key in pressed:
      (x, y) = key
      if y == 3:
        if x == self.down_x:
          self.player.decrease_chains()
        elif x == self.up_x:
          self.player.increase_chains()
        
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
    self.children = []

    for p in app.players:
      self.children.append(PlayerKeyUi(trellis, p))
      self.children.append(PlayerChainsUi(trellis, p))
  
  def render(self, t = time.monotonic()):
    for p in self.children:
      p.render(t)

  def handle_keys(self, t, pressed):
    for p in self.children:
      p.handle_keys(t, pressed)