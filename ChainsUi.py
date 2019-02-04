import time
import adafruit_fancyled.adafruit_fancyled as fancy

import palettes
from LightStrip import LightStrip

DECREASE_STRIP_COLORS = [
  fancy.CHSV(2.2/6, 1.0, 0.5),
  fancy.CHSV(2.2/6, 0.25, 0.25),
  fancy.CHSV(2.2/6, 0.25, 0.25),
]

INCREASE_STRIP_COLORS = [
  fancy.CHSV(0, 1.0, 0.5),
  fancy.CHSV(0, 0.25, 0.25),
  fancy.CHSV(0, 0.25, 0.25),
]

BLUE_WITH_WHITE_HIGHLIGHT_PALETTE = [
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.7, 1.0),
  fancy.CHSV(4/6.0, 0.0, 1.0),
]

CHAIN_STRIP_SPEED = 0.02

class ChainsUi:
  def __init__(self, trellis, app, player):
    self.app = app
    self.player = player

    if player.side == 'left':
      player_x = range(0, 1)
      controls_x = range(7, 8)
      chains_x = range(1, 7)
    else:
      player_x = range(7, 8)
      controls_x = range(0, 1)
      chains_x = range(6, 0, -1)

    self.player_strip = LightStrip(
      pixels = trellis.pixels,
      x_range = player_x,
      y_range = range(0, 4),
      colors = BLUE_WITH_WHITE_HIGHLIGHT_PALETTE,
      value = 0,
      brightness = 0.6,
      palette_shift_speed = -2,
      palette_scale = 0.2,
    )

    self.chain_bg_strip = LightStrip(
      pixels = trellis.pixels,
      x_range = chains_x,
      y_range = range(0, 4),
      colors = [
        fancy.CHSV(4/6.0, 0.7, 0.4),
        fancy.CHSV(4/6.0, 0.0, 0.4),
        fancy.CHSV(4/6.0, 0.0, 0.4),
        fancy.CHSV(4/6.0, 0.0, 0.4),
        fancy.CHSV(4/6.0, 0.0, 0.4),
      ], 
      brightness = 0.8,
      speed = CHAIN_STRIP_SPEED,
      palette_shift_speed = 1,
      value = self.player.chains,
    )

    self.chain_strip = LightStrip(
      pixels = trellis.pixels,
      x_range = chains_x,
      y_range = range(0, 4),
      colors = palettes.CHAINS, 
      brightness = 0.8,
      speed = CHAIN_STRIP_SPEED,
      value = -1,
      background_color = None,
    )

    self.strips = [
      self.player_strip,
      self.chain_bg_strip,
      self.chain_strip,
    ]

    self.closing = False
  
  def render(self, t): 
    for strip in self.strips:
      strip.render(t)

    if self.chain_strip.value != self.player.chains and not self.closing:
      self.update_strip(t)
  
  def handle_keys(self, t, pressed, down, up):
    close_x = 0 if self.player.side == 'left' else 7
    function_x = 7 if self.player.side == 'left' else 0

    for key in down:
      (x, y) = key
      if x in range(1, 7):
        new_chains = x + y * 6
        if new_chains == 1 and self.player.chains == 1:
          new_chains = 0
        self.player.chains = new_chains
        self.update_strip(t)
      elif x == close_x:
        self.app.switch_ui('main')

      elif x == function_x:
        if y < 2:
          self.player.decrease_chains()
        elif y >= 2:
          self.player.increase_chains()
        self.update_strip(t)

  def set_player(self, player):
    self.player = player

  def update_strip(self, t = None):
    self.chain_strip.set_value(self.player.chains, t)
    self.chain_bg_strip.min_value = self.player.chains

  def close(self, t):
    self.closing = True
    self.chain_strip.set_value(0, t)
    self.chain_strip.background_color = fancy.CRGB(0, 0, 0)
    self.chain_bg_strip.min_value = 24
    return CHAIN_STRIP_SPEED * self.player.chains + 0.1
