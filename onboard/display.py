from board import GP20, GP21
from busio import I2C
from displayio import release_displays, I2CDisplay, Group, Bitmap, Palette, TileGrid
from adafruit_displayio_ssd1306 import SSD1306
from time import sleep


class OLED:
    w = 128

    h = 64

    def __init__(self, led):
        release_displays()

        i2c = I2C(scl=GP21, sda=GP20)
        dbus = I2CDisplay(i2c, device_address=0x3C)
        self.d = SSD1306(dbus, width=self.w, height=self.h)

        self.g = Group()
        self.b = Bitmap(self.w, self.h, 2)
        self.p = Palette(2)

        self.p[0] = 0x000000
        self.p[1] = 0xFFFFFF

        led.value = True
        sleep(0.5)
        self.tg = TileGrid(self.b, pixel_shader=self.p)
        sleep(0.5)
        led.value = False
        self.g.append(self.tg)

    def clear(self):
        self.row(0, self.h, 0)

    def row(self, start=0, end=h, v=1):
        for y in range(min(self.h, self.h - start - 1), max(0, self.h - end - 1), -1):
            for x in range(self.w):
                self.b[x, y] = v

        self.d.show(self.g)

    def showLayer(self, order, l):
        for i, o in enumerate(sorted(order)):
            if order[o][0] == l:
                for y in range(1 + i):
                    offset = y * 10
                    self.row(offset, offset + 5)

                sleep(1)
                self.km.oled.clear()
                break
