import adafruit_fancyled.adafruit_fancyled as fancy

RED_KEY = [fancy.CHSV(1.0, 0.5, 0.5), fancy.CHSV(1.0)]
YELLOW_KEY = [fancy.CHSV(1.0 / 6.0, 0.5, 0.5), fancy.CHSV(1.0 / 6.0)]
BLUE_KEY = [fancy.CHSV(0.6, 0.5, 0.5), fancy.CHSV(0.6)]

CHAINS = [
  fancy.CRGB(96, 149, 64),
  fancy.CRGB(234,209,83),
  fancy.CRGB(243,169,87),
  fancy.CRGB(178,31,31),
]
