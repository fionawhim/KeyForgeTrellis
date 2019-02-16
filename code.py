import adafruit_trellism4
import adafruit_adxl34x
import board
import busio

from App import App

trellis = adafruit_trellism4.TrellisM4Express()
i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)

app = App(trellis, accelerometer)
app.run()
