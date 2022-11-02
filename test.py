from usb_hid import devices
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from json import loads, dumps
from digitalio import DigitalInOut as dio, Direction, Pull
from board import GP15
from time import sleep


class LayerManager:
    def __init__(self):
        with open("layout.json", "r") as f:
            self.layers = loads(f.read())

        self.active = self.layers["start"]

    def setDefault(self, layer):
        self.layers["start"] = layer
        with open("layout.json", "w") as f:
            f.write(dumps(self.layers, indent=4))

    def __getitem__(self, i):
        s = False
        if len(i) == 4:
            c, r, sl, s = i
        else:
            c, r, sl = i

        code = self.layers["layers"][self.active][c][r][s]
        return code if s else self.findKey(code)

    def findKey(self, code):
        return Keycode.FIVE


kbd = Keyboard(devices)
lm = LayerManager()

a0 = dio(GP15)
a0.switch_to_input(pull=Pull.UP)

pressed = False
while True:
    if not (a0.value or pressed):
        pressed = True
        print(lm["a", 0, 0, True])
        kbd.send(Keycode.FIVE)

    sleep(0.001)
