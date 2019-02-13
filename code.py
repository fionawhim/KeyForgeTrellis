import adafruit_trellism4

from App import App

trellis = adafruit_trellism4.TrellisM4Express()

app = App(trellis)
app.run()
