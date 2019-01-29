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
      speed = 0.05,
      t = time.monotonic()):
    self.pixels = pixels
    self.colors = colors if type(colors) is list else [colors]
    self.x_pos = list(x_range)
    self.y_pos = list(y_range)

    self.max_val = (self.x_pos[-1] - self.x_pos[0] + 1) * (self.y_pos[-1] - self.y_pos[0] + 1)
    self.max_time = speed * self.max_val

    color_count = len(self.colors)
    palette_linearizer = (color_count - 1) / color_count if color_count > 1 else 1
    self.palette_step = 1.0 / self.max_val * palette_linearizer

    self.speed = speed

    self.rendered_value = 0
    self.value = value
    self.last_value = value
    self.last_value_t = t
  
  def set_value(self, value, t = time.monotonic()):
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
          c = fancy.palette_lookup(self.colors, i * self.palette_step)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = BRIGHTNESS).pack()
        i = i + 1


STRIP_1 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(8),
  y_range = range(1),
  colors = [fancy.CHSV(1.0, 0.5, 0.5), fancy.CHSV(1.0)],
  value = 1
)

STRIP_2 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(8),
  y_range = range(1, 2),
  colors = [fancy.CHSV(1.0 / 6.0, 0.5, 0.5), fancy.CHSV(1.0 / 6.0)],
  value = 1
)

STRIP_3 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(8),
  y_range = range(2, 3),
  colors = [fancy.CHSV(0.6, 0.5, 0.5), fancy.CHSV(0.6)],
  value = 1
)


last_pressed = set()
last_pressed_t = 0

fps = 0
fps_t = time.monotonic()

KEY_CHECK_INTERVAL = 0.125

while True:
  t = time.monotonic()

  if t >= last_pressed_t + KEY_CHECK_INTERVAL:
    pressed = set(trellis.pressed_keys)

    for press in pressed - last_pressed:
      if press == (0, 0):
        if STRIP_1.value == 1:
          STRIP_1.set_value(8, t)
        else:
          STRIP_1.set_value(1, t)
      if press == (0, 1):
        if STRIP_2.value == 1:
          STRIP_2.set_value(8, t)
        else:
          STRIP_2.set_value(1, t)
      if press == (0, 2):
        if STRIP_3.value == 1:
          STRIP_3.set_value(8, t)
        else:
          STRIP_3.set_value(1, t)


    last_pressed = pressed
    last_pressed_t = t

  STRIP_1.render(t)
  STRIP_2.render(t)
  STRIP_3.render(t)
  trellis.pixels.show()

  fps = fps + 1

  if t > fps_t + 1:
    print("FPS: ", fps / (t - fps_t))
    fps = 0
    fps_t = t
