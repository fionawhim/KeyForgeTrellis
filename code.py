import time
import adafruit_trellism4
import adafruit_fancyled.adafruit_fancyled as fancy

from LightStrip import LightStrip

trellis = adafruit_trellism4.TrellisM4Express()
trellis.pixels.auto_write = False

RED_KEY_PALETTE = [fancy.CHSV(1.0, 0.5, 0.5), fancy.CHSV(1.0)]
YELLOW_KEY_PALETTE = [fancy.CHSV(1.0 / 6.0, 0.5, 0.5), fancy.CHSV(1.0 / 6.0)]
BLUE_KEY_PALETTE = [fancy.CHSV(0.6, 0.5, 0.5), fancy.CHSV(0.6)]



# class MainUi:
#   __init__(self):

#     return


STRIP_1 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(4),
  y_range = range(1),
  colors = RED_KEY_PALETTE,
  value = 1,
)

STRIP_4 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(7, 3, -1),
  y_range = range(1),
  colors = RED_KEY_PALETTE,
  value = 1,
)

STRIP_2 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(4),
  y_range = range(1, 2),
  colors = YELLOW_KEY_PALETTE,
  value = 1,  
)

STRIP_5 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(7, 3, -1),
  y_range = range(1, 2),
  colors = YELLOW_KEY_PALETTE,
  value = 1,
)

STRIP_3 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(4),
  y_range = range(2, 3),
  colors = BLUE_KEY_PALETTE,
  value = 1,
)

STRIP_6 = LightStrip(
  pixels = trellis.pixels,
  x_range = range(7, 3, -1),
  y_range = range(2, 3),
  colors = BLUE_KEY_PALETTE,
  value = 1,
)

last_pressed = set()
last_pressed_t = 0

fps = 0
fps_t = time.monotonic()

SIXTY_FPS = 1 / 60.0
KEY_CHECK_INTERVAL = 0.125

while True:
  t = time.monotonic()

  if t >= last_pressed_t + KEY_CHECK_INTERVAL:
    pressed = set(trellis.pressed_keys)

    for press in pressed - last_pressed:
      if press == (0, 0):
        if STRIP_1.value == 1:
          STRIP_1.set_value(4, t)
        else:
          STRIP_1.set_value(1, t)
      if press == (0, 1):
        if STRIP_2.value == 1:
          STRIP_2.set_value(4, t)
        else:
          STRIP_2.set_value(1, t)
      if press == (0, 2):
        if STRIP_3.value == 1:
          STRIP_3.set_value(4, t)
        else:
          STRIP_3.set_value(1, t)
      if press == (7, 0):
        if STRIP_4.value == 1:
          STRIP_4.set_value(4, t)
        else:
          STRIP_4.set_value(1, t)
      if press == (7, 1):
        if STRIP_5.value == 1:
          STRIP_5.set_value(4, t)
        else:
          STRIP_5.set_value(1, t)
      if press == (7, 2):
        if STRIP_6.value == 1:
          STRIP_6.set_value(4, t)
        else:
          STRIP_6.set_value(1, t)

    last_pressed = pressed
    last_pressed_t = t

  STRIP_1.render(t)
  STRIP_2.render(t)
  STRIP_3.render(t)
  STRIP_4.render(t)
  STRIP_5.render(t)
  STRIP_6.render(t)
  trellis.pixels.show()

  t_diff = time.monotonic() - t
  if t_diff < SIXTY_FPS:
    time.sleep(SIXTY_FPS - t_diff)

  fps = fps + 1

  if t > fps_t + 1:
    print("FPS: ", fps / (t - fps_t))
    fps = 0
    fps_t = t
