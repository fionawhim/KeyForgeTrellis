import time
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS = 0.3
 
class LightStrip:
  def __init__(self, pixels, x_range, y_range, colors,
      value = 0,
      speed = 0.05,
      t = time.monotonic()):
    self.pixels = pixels
    self.colors = colors if type(colors) is list else [colors]
    self.x_pos = list(x_range)
    self.y_pos = list(y_range)

    self.max_val = (abs(self.x_pos[-1] - self.x_pos[0]) + 1) * (abs(self.y_pos[-1] - self.y_pos[0]) + 1)
    self.max_time = speed * self.max_val

    self.palette_step = 1.0 / self.max_val

    self.speed = speed

    self.rendered_value = 0
    self.value = value
    self.last_value = value
    self.last_value_t = t
  
  def set_value(self, value, t = None):
    t = time.monotonic() if t == None else t
    self.last_value = self.rendered_value
    self.value = value
    self.last_value_t = t 

  def render(self, t = time.monotonic()):
    time_diff = t - self.last_value_t

    if self.value == self.rendered_value:
      return

    time_delta = int(time_diff / self.speed)

    if self.value > self.last_value:
      self.rendered_value = min(self.value, self.last_value + time_delta)
    else:
      self.rendered_value = max(self.value, self.last_value - time_delta)

    i = 1

    for x in self.x_pos:
      for y in self.y_pos:
        if i > self.rendered_value:
          c = fancy.CRGB(0, 0, 0)
        else:
          c = fancy.palette_lookup(self.colors, (i - 1) * self.palette_step)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = BRIGHTNESS).pack()

        i = i + 1

