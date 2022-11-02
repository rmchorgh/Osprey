from usb_hid import devices
from adafruit_hid.keyboard import Keyboard
from json import loads, dumps
from digitalio import DigitalInOut as dio, Direction, Pull
from board import GP15
from time import sleep
from convert import Keycode


class LayerManager:
    def __init__(self):
        with open("layout.json", "r") as f:
            self.layers = loads(f.read())

        self.active = self.layers["start"]

    def __getitem__(self, i):
        s = False
        sl = 0
        if len(i) == 4:
            c, r, sl, s = i
        else:
            c, r, sl = i

        code = self.layers["layers"][self.active][c][r]
        if isinstance(code, list):
            m = min(len(code) - 1, sl)
            code = code[m]

        return code if s else Keycode.parse(code)


kbd = Keyboard(devices)

lm = LayerManager()

a0 = dio(GP15)
a0.switch_to_input(pull=Pull.UP)

pressed = False
while True:
    if not (a0.value or pressed):
        pressed = True
        for x in lm["b", 3, 3]:
            kbd.press(x)
    if a0.value and pressed:
        pressed = False
        kbd.release_all()

    sleep(0.001)
