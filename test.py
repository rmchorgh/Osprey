from usb_hid import devices
from adafruit_hid.keyboard import Keyboard
from json import loads, dumps
from digitalio import DigitalInOut as dio, Direction, Pull

import board
from busio import I2C
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


class Matrix:
    def __init__(self):
        with open("pinmap.json", "r") as f:
            matrix = loads(f.read())
            if matrix["ncols"] != len(matrix["cols"]):
                raise Exception(
                    f"ncols and added cols do not match.{len(matrix['cols'])}"
                )
            if matrix["nrows"] != len(matrix["rows"]):
                raise Exception("nrows and added rows do not match.")

            self.cols = {}
            for kc in matrix["cols"]:
                c = matrix["cols"][kc]
                if f"GP{c}" not in dir(board):
                    raise Exception(f"Column: GP{c} is not a pin.")

                self.cols[kc] = dio(getattr(board, f"GP{c}"))
                self.cols[kc].switch_to_input(pull=Pull.DOWN)

            self.rows = []
            for r in matrix["rows"]:
                if f"GP{r}" not in dir(board):
                    raise Exception(f"Row: GP{r} is not a pin.")

                self.rows += [dio(getattr(board, f"GP{r}"))]
                self.rows[-1].switch_to_output()
                self.rows[-1].value = 0

            # for ki in matrix["i2c"]:
            #     i = matrix["i2c"][ki]
            #     if f"GP{i}" not in dir(board):
            #         raise Exception(f"i2c: GP{r} is not a pin.")

            # scl = getattr(board, f"GP{matrix['i2c']['scl']}")
            # sda = getattr(board, f"GP{matrix['i2c']['sda']}")
            # self.i2c = I2C(scl, sda)

    def __getitem__(self, i):
        if isinstance(i, str):
            return self.cols[i]
        elif isinstance(i, int):
            return self.rows[i]

def listen(kbd, lm, m):
    pressed = set([])
    while True:
        for kr, r in enumerate(m.rows):
            r.value = 1
            for kc in m.cols:
                c = m[kc]
                cr = f"{kc}{kr}"  # lm[kc, kr, 0, True]
                if c.value and (cr not in pressed):
                    pressed.add(cr)
                    for x in lm[kc, kr, 0]:
                        if x is not None:
                            kbd.press(x)
                    print(pressed)

                if not c.value and cr in pressed:
                    pressed.remove(cr)
                    for x in lm[kc, kr, 0]:
                        if x is not None:
                            kbd.release(x)
            r.value = 0
        sleep(0.001)


kbd = Keyboard(devices)
lm = LayerManager()
m = Matrix()

listen(kbd, lm, m)
