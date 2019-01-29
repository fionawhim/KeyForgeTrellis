import time
import adafruit_trellism4
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS = 0.5
 
trellis = adafruit_trellism4.TrellisM4Express()
trellis.pixels.auto_write = False

color = fancy.CRGB(255, 85, 0)  


class LightStrip:
  def __init__(self, pixels, x_range, y_range, colors,
      value = 0,
      speed = 0.025,
      t = time.monotonic()):
    self.pixels = pixels
    self.colors = colors if type(colors) is list else [colors]
    self.x_pos = list(x_range)
    self.y_pos = list(y_range)

    self.max_val = (self.x_pos[-1] - self.x_pos[0] + 1) * (self.y_pos[-1] - self.y_pos[0] + 1)

    color_count = len(self.colors)
    palette_linearizer = (color_count - 1) / color_count if color_count > 1 else 1
    self.palette_step = 1.0 / self.max_val * palette_linearizer

    self.speed = speed

    self.value = value
    self.last_value = value
    self.last_value_t = t
  
  def set_value(self, value, t = time.monotonic()):
    self.last_value = self.value
    self.value = value
    self.last_value_t = t

  def render(self, t = time.monotonic()):
    time_delta = int((t - self.last_value_t) / self.speed)

    if self.value > self.last_value:
      render_value = min(self.value, self.last_value + time_delta)
    else:
      render_value = max(self.value, self.last_value - time_delta)

    i = 1

    for x in self.x_pos:
      for y in self.y_pos:
        if i > render_value:
          c = fancy.CRGB(0, 0, 0)
        else:
          c = fancy.palette_lookup(self.colors, i * self.palette_step)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = BRIGHTNESS).pack()
        i = i + 1


STRIP_1 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(8),
  y_range = range(1),
  colors = [fancy.CHSV(1.0, 0.7), fancy.CHSV(1.0, 1.0)],
  value = 8
)

val = 8
last_change_t = time.monotonic()

while True:
  t = time.monotonic()
  STRIP_1.render(t)
  trellis.pixels.show()

  if t > last_change_t + 3:
    if val == 8:
      val = 0
    else:
      val = 8
    STRIP_1.set_value(val, t=t)
    last_change_t = t