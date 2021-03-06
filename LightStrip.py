import time
from math import floor
import adafruit_fancyled.adafruit_fancyled as fancy

BRIGHTNESS = 0.6


class LightStrip:
    def __init__(
        self,
        pixels,
        colors,
        x_range=None,
        y_range=None,
        value=0,
        min_value=0,
        speed=0.05,
        brightness=BRIGHTNESS,
        palette_shift_speed=None,
        palette_scale=1.0,
        background_color=fancy.CRGB(0, 0, 0),
        positions=None,
        color_from_end=False,
        highlight=None,
        highlight_color=fancy.CHSV(0, 0, 1.0),
        highlight_speed=1,
        t=time.monotonic(),
    ):
        self.pixels = pixels
        self.speed = speed
        self.palette_shift_speed = palette_shift_speed
        self.palette_scale = palette_scale
        self.colors = colors if type(colors) is list else [colors]
        self.background_color = background_color
        self.color_from_end = color_from_end
        self.highlight = highlight
        self.highlight_color = highlight_color
        self.highlight_speed = highlight_speed
        self.highlight_t = 0

        self.set_position(x_range, y_range, positions)

        self.brightness = brightness

        self.rendered_value = 0
        self.dirty = False
        self.value = value
        self.min_value = min_value
        self.last_value = value
        self.last_value_t = t

    def set_position(self, x_range=None, y_range=None, positions=None):
        if positions == None:
            positions = []
            for y in y_range:
                for x in x_range:
                    positions.append((x, y))

        self.positions = positions

        self.max_val = len(positions)
        self.max_time = 1 if self.speed is None else self.speed * self.max_val

        # Compensates for the last 'fence' of the color palette range going back to 0.
        # e.g. in a 4-color palette, 0 -> 0.25 -> 0.5 -> 0.75 -> 1.0
        # We want to render the palette so that value 1 is color 0 and max value is 0.75.
        max_color = (len(self.colors) - 1.0) / len(self.colors)

        # This will be multiplied by value - 1.
        self.palette_step = max_color / (self.max_val - 1) * self.palette_scale

    def set_value(self, value, t=None, now=False):
        if value == self.value:
            return
        if now:
            self.rendered_value = 0
        self.last_value = self.rendered_value
        self.value = value
        self.last_value_t = t if t != None else 0

    def set_highlight(self, highlight, t=0):
        if type(highlight) != list:
            highlight = [highlight]

        self.highlight = []

        for h in highlight:
            if type(h) is int:
                self.highlight.append(self.positions[h - 1])
            else:
                self.highlight.append(h)
        self.highlight_t = t

    def clear_highlight(self):
        self.highlight = None
        self.dirty = True

    def render(self, t):
        if (
            self.value == self.rendered_value
            and (self.palette_shift_speed == None or self.value == 0)
            and not self.dirty
            and self.highlight == None
        ):
            return

        if self.last_value_t == None or self.speed is None:
            time_delta = self.max_val
        else:
            time_diff = t - self.last_value_t
            time_delta = int(time_diff / self.speed)

        if self.value > self.last_value:
            self.rendered_value = min(self.value, self.last_value + time_delta)
        else:
            self.rendered_value = max(self.value, self.last_value - time_delta)

        highlight_mix = abs(
            0.5
            - ((t - self.highlight_t) % self.highlight_speed)
            / (self.highlight_speed)
            * 1.5
        ) if self.highlight_speed != None else 0

        if self.palette_shift_speed == None:
            palette_animation_offset = 0
        else:
            palette_t = t if self.last_value_t == None else t - self.last_value_t
            palette_animation_offset = (
                palette_t % self.palette_shift_speed
            ) / self.palette_shift_speed
        i = 1

        if self.color_from_end:
            palette_align = self.max_val - self.rendered_value
        else:
            palette_align = 0

        for (x, y) in self.positions:
            if i <= self.min_value:
                c = None
            elif i <= self.rendered_value:
                c_idx = (
                    i - 1 + palette_align
                ) * self.palette_step + palette_animation_offset
                c = fancy.palette_lookup(self.colors, c_idx)
            else:
                c = self.background_color

            if self.highlight != None and (x, y) in self.highlight:
                if c == None:
                    c = fancy.CHSV(0, 0, 0.0)

                c = fancy.mix(self.highlight_color, c, highlight_mix)

            if c != None:
                c_packed = pack(fancy.gamma_adjust(c, brightness=self.brightness))
                self.pixels[x, y] = c_packed

            i = i + 1

        self.dirty = False


def pack(c):
    return (
        (floor(c.red * 255) << 16) | (floor(c.green * 255) << 8) | (floor(c.blue * 255))
    )
