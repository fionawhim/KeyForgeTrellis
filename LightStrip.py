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
      background_color = fancy.CRGB(0, 0, 0),
      t = time.monotonic()):
    self.pixels = pixels
    self.speed = speed
    self.palette_shift_speed = palette_shift_speed
    self.palette_range = palette_range
    self.colors = colors if type(colors) is list else [colors]
    self.background_color = background_color

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

    # Compensates for the last 'fence' of the color palette range going back to 0.
    # e.g. in a 4-color palette, 0 -> 0.25 -> 0.5 -> 0.75 -> 1.0
    # We want to render the palette so that value 1 is color 0 and max value is 0.75.
    max_color = (len(self.colors) - 1.0) / len(self.colors)

    # This will be multiplied by value - 1.
    self.palette_step = max_color / (self.max_val - 1) * self.palette_range

  
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
          c = self.background_color
        else:
          c_idx = (i - 1) * self.palette_step + palette_animation_offset
          c = fancy.palette_lookup(self.colors, c_idx)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = self.brightness).pack()

        i = i + 1

