from usb_hid import devices
from adafruit_hid.keyboard import Keyboard
from json import loads
from digitalio import DigitalInOut as dio, Pull

import board
from busio import I2C
from time import sleep
from convert import Keycode


class LayerManager:
    def __init__(self):
        with open("layout.json", "r") as f:
            ljson = loads(f.read())
            self.layers = ljson["layers"]
            self.active = ljson["start"]
            self.sublayer = 0

        self.matrix = Matrix()
        self.kbd = Keyboard(devices)
        self.pressed = {}

    def __getitem__(self, i):
        s = False
        if len(i) == 3:
            c, r, s = i
        else:
            c, r = i

        code = self.layers[self.active][c][r]
        return code if s else Keycode.parse(code)

    def getKeySublayer(self, key):
        if self.sublayer > 0:
            return self.sublayer

        sls = self.layers[self.active]["sublayers"]
        sublayer = 0
        for i, sl in enumerate(sls):
            if sl == key or (isinstance(key, list) and sl == key[0]):
                sublayer = 1 + i
                break

        return sublayer

    def press(self, key, cr):
        self.sublayer = self.getKeySublayer(key)
        if cr not in self.pressed.keys():
            self.sublayer = self.getKeySublayer(key)
            if isinstance(key, list):
                if key[self.sublayer] == 0:
                    key = f"Shf+{key[0]}"
                else:
                    key = key[self.sublayer]

            self.pressed[cr] = self.sublayer

            for x in key.split("+"):
                try:
                    self.kbd.press(Keycode.lookup(x))
                except:
                    print(x)

    def release(self, key, cr):
        if cr in self.pressed.keys():
            if isinstance(key, list):
                if key[self.pressed[cr]] == 0:
                    key = f"Shf+{key[0]}"
                else:
                    key = key[self.pressed[cr]]

            del self.pressed[cr]

            for x in key.split("+"):
                self.kbd.release(Keycode.lookup(x))

    def listen(self):
        try:
            while True:
                for kr, r in enumerate(self.matrix.rows):
                    r.value = 1
                    for kc in self.matrix.cols:
                        key = self[kc, kr, True]
                        cr = f"{kc}{kr}"
                        if self.matrix.cols[kc].value:
                            self.press(key, cr)
                        else:
                            self.release(key, cr)
                    r.value = 0
                sleep(0.001)
        except KeyboardInterrupt:
            self.kbd.release_all()
        except TypeError:
            self.kbd.release_all()


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


lm = LayerManager()
lm.listen()


# lm.matrix[2].value = 1
# while True:
#     if lm.matrix['_d'].value:
#         lm.press(lm['_d', 2, True], '_d2')
#     else:
#         lm.release(lm['_d', 2, True], '_d2')
