import time
import adafruit_trellism4
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS = 0.5
 
trellis = adafruit_trellism4.TrellisM4Express()
trellis.pixels.auto_write = False

color = fancy.CRGB(255, 85, 0)  


class LightStrip:
  def __init__(self, pixels, x_range, y_range, colors, value = 0):
    self.pixels = pixels
    self.colors = colors if type(colors) is list else [colors]
    self.x_pos = list(x_range)
    self.y_pos = list(y_range)

    self.max_val = (self.x_pos[-1] - self.x_pos[0] + 1) * (self.y_pos[-1] - self.y_pos[0] + 1)
    self.palette_step = 1.0 / self.max_val

    self.value = value
  
  def render(self, t):
    i = 0

    for x in self.x_pos:
      for y in self.y_pos:
        if i == self.value:
          break

        c = fancy.palette_lookup(self.colors, i * self.palette_step)
        self.pixels[x, y] = fancy.gamma_adjust(c, brightness = BRIGHTNESS).pack()
        i = i + 1


STRIP_1 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(4),
  y_range = range(1),
  colors = [fancy.CHSV(1.0), fancy.CHSV(0.5)],
  value = 4
)

while True:
  t = time.monotonic()
  STRIP_1.render(t)
  trellis.pixels.show()
