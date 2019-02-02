import time
import adafruit_fancyled.adafruit_fancyled as fancy

from LightStrip import LightStrip

RED_KEY_PALETTE = [fancy.CHSV(1.0, 0.5, 0.5), fancy.CHSV(1.0)]
YELLOW_KEY_PALETTE = [fancy.CHSV(1.0 / 6.0, 0.5, 0.5), fancy.CHSV(1.0 / 6.0)]
BLUE_KEY_PALETTE = [fancy.CHSV(0.6, 0.5, 0.5), fancy.CHSV(0.6)]

SIDE_LEFT = 'left'
SIDE_RIGHT = 'right'

class PlayerKeyUi:
  def __init__(self, trellis, side):
    x_range = range(4) if side == SIDE_LEFT else range(7, 3, -1)
    self.key_x = 0 if side == SIDE_LEFT else 7

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
        self.toggle_strip(self.strips[y], t)

  def toggle_strip(self, strip, t):
    if strip.value == 1:
      strip.set_value(4, t)
    else:
      strip.set_value(1, t)

class MainUi:
  def __init__(self, trellis):
    self.player_keys = [
      PlayerKeyUi(trellis, SIDE_LEFT),
      PlayerKeyUi(trellis, SIDE_RIGHT),
    ]
  
  def render(self, t = time.monotonic()):
    for p in self.player_keys:
      p.render(t)

  def handle_keys(self, t, pressed):
    for p in self.player_keys:
      p.handle_keys(t, pressed)