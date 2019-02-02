import time
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
from LightStrip import LightStrip

class ChainsUi:
  def __init__(self, trellis, app):
    self.player = None

    self.side_strips = [
      LightStrip(
        pixels = trellis.pixels,
        x_range = range(0, 1),
        y_range = range(0, 4),
        colors = palettes.CHAINS,
        value = 4,
        brightness = 0.05,
      ),
      LightStrip(
        pixels = trellis.pixels,
        x_range = range(7, 8),
        y_range = range(0, 4),
        colors = palettes.CHAINS,
        value = 4,
        brightness = 0.05,
      ),
    ]

    self.chain_strip = LightStrip(
      pixels = trellis.pixels,
      x_range = range(1, 7),
      y_range = range(0, 4),
      colors = [fancy.CRGB(150, 150, 150), fancy.CRGB(100, 100, 255)],
      speed = 0.02,
      value = 0,
    )
  
  def render(self, t): 
    for strip in self.side_strips:
      strip.render(t)

    self.chain_strip.render(t)

    if self.chain_strip.value != self.player.chains:
      self.update_strip(t)
  
  def handle_keys(self, t, keys):
    for key in keys:
      (x, y) = key
      if x in range(1, 7):
        self.player.chains = x + y * 6
        self.update_strip(t)
      elif x == 0:
        self.player.decrease_chains()
        self.update_strip(t)
      elif x == 7:
        self.player.increase_chains()
        self.update_strip(t)

  def set_player(self, player):
    self.player = player
    self.chain_strip.set_value(0)

  def update_strip(self, t = None):
    self.chain_strip.set_value(self.player.chains, t)
