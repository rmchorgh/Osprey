import board
from busio import I2C
from displayio import release_displays, I2CDisplay, Group, Bitmap
from adafruit_displayio_ssd1306 import SSD1306
from adafruit_display_text.label import Label
from terminalio import FONT
from time import sleep

def start():
    release_displays()
    i2c = I2C(scl=board.GP21, sda=board.GP20)
    dbus = I2CDisplay(i2c, device_address=0x3C)
    d = SSD1306(dbus, width=128, height=64)
    
    g = Group()
    d.show(Label(FONT, text="\nhi\n7"))
    sleep(1)
    d.sleep()
    while True:
        pass

start()

