import time
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS = 0.3
 
class LightStrip:
  def __init__(self, pixels, x_range, y_range, colors,
      value = 0,
      speed = 0.05,
      brightness = BRIGHTNESS,
      palette_shift_speed = None,
      palette_range = 1.0,
      t = time.monotonic()):
    self.pixels = pixels
    self.speed = speed
    self.palette_shift_speed = palette_shift_speed
    self.palette_range = palette_range
    self.colors = colors if type(colors) is list else [colors]

    self.set_position(x_range, y_range)

    self.brightness = brightness

    self.rendered_value = 0
    self.value = value
    self.last_value = value
    self.last_value_t = t

  def set_position(self, x_range = None, y_range = None):
    if x_range != None:
      self.x_pos = list(x_range)
    if y_range != None:
      self.y_pos = list(y_range)

    self.max_val = (abs(self.x_pos[-1] - self.x_pos[0]) + 1) * (abs(self.y_pos[-1] - self.y_pos[0]) + 1)
    self.max_time = self.speed * self.max_val
    self.palette_step = 1.0 / self.max_val * self.palette_range

  
  def set_value(self, value, t = None):
    self.last_value = self.rendered_value
    self.value = value
    self.last_value_t = t if t != None else 0


  def render(self, t = time.monotonic()):
    if self.value == self.rendered_value and self.palette_shift_speed == None:
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

    if self.palette_shift_speed == None:
      palette_animation_offset = 0
    else:
      palette_animation_offset = (t % self.palette_shift_speed) / self.palette_shift_speed
    i = 1

    for y in self.y_pos:
      for x in self.x_pos:
        if i > self.rendered_value:
          c = fancy.CRGB(0, 0, 0)
        else:
          c_idx = (i - 1) * self.palette_step + palette_animation_offset
          c = fancy.palette_lookup(self.colors, c_idx)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = self.brightness).pack()

        i = i + 1

