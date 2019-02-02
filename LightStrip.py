import time
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS = 0.3
 
class LightStrip:
  def __init__(self, pixels, x_range, y_range, colors,
      value = 0,
      speed = 0.05,
      brightness = BRIGHTNESS,
      t = time.monotonic()):
    self.pixels = pixels
    self.colors = colors if type(colors) is list else [colors]
    self.x_pos = list(x_range)
    self.y_pos = list(y_range)

    self.max_val = (abs(self.x_pos[-1] - self.x_pos[0]) + 1) * (abs(self.y_pos[-1] - self.y_pos[0]) + 1)
    self.max_time = speed * self.max_val

    self.palette_step = 1.0 / self.max_val

    self.speed = speed
    self.brightness = brightness

    self.rendered_value = 0
    self.value = value
    self.last_value = value
    self.last_value_t = t
  
  def set_value(self, value, t = None):
    self.last_value = self.rendered_value
    self.value = value
    self.last_value_t = t if t != None else 0

  def render(self, t = time.monotonic()):
    if self.value == self.rendered_value:
      return

    if self.last_value_t == None:
      time_delta = self.max_val
    else:
      time_diff = t - self.last_value_t
      time_delta = int(time_diff / self.speed)

    if self.value > self.last_value:
      self.rendered_value = min(self.value, self.last_value + time_delta)
    else:
      self.rendered_value = max(self.value, self.last_value - time_delta)

    i = 1

    for y in self.y_pos:
      for x in self.x_pos:
        if i > self.rendered_value:
          c = fancy.CRGB(0, 0, 0)
        else:
          c = fancy.palette_lookup(self.colors, (i - 1) * self.palette_step)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = self.brightness).pack()

        i = i + 1

