import time
import adafruit_trellism4
 
trellis = adafruit_trellism4.TrellisM4Express()
 
while True:
    trellis.pixels[0, 0] = (100, 0, 0)
    time.sleep(0.5)
    trellis.pixels[0, 0] = (0, 0, 0)
    time.sleep(0.5)
