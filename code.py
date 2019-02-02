import time
import adafruit_trellism4
import adafruit_fancyled.adafruit_fancyled as fancy

from App import App

trellis = adafruit_trellism4.TrellisM4Express()
trellis.pixels.auto_write = False

app = App(trellis)

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

    app.handle_keys(t, pressed - last_pressed)

    last_pressed = pressed
    last_pressed_t = t

  app.render(t)
  trellis.pixels.show()

  t_diff = time.monotonic() - t
  if t_diff < SIXTY_FPS:
    time.sleep(SIXTY_FPS - t_diff)

  fps = fps + 1

  if t > fps_t + 1:
    print("FPS: ", fps / (t - fps_t))
    fps = 0
    fps_t = t
