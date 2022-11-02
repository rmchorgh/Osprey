from adafruit_hid.keycode import Keycode as K


class Keycode:
    def lookup(x: str, side: int = 0):
        if x is None:
            return

        c = None

        l = len(x)
        if l == 1:
            if x.upper() in dir(K):
                c = x.upper()
            else:
                table = {
                    "'": "QUOTE",
                    "1": "ONE",
                    "2": "TWO",
                    "3": "THREE",
                    "4": "FOUR",
                    "5": "FIVE",
                    "6": "SIX",
                    "7": "SEVEN",
                    "8": "EIGHT",
                    "9": "NINE",
                    "0": "ZERO",
                }
        elif l == 2:
            if x in dir(K):
                c = x
        elif l == 3:
            table = {
                "Shf": ["LEFT_SHIFT", "RIGHT_SHIFT"][side],
                "Sup": ["LEFT_GUI", "RIGHT_GUI"][side],
                "Tab": "TAB",
                "Bsp": "BACKSPACE",
                "Ent": "ENTER",
                "Ctr": ["LEFT_CONTROL", "RIGHT_CONTROL"][side],
            }

            if x in table.keys():
                c = table[x]

        if c is not None:
            return getattr(K, c)

    def parse(x: str):
        if x is None:
            return

        return [Keycode.lookup(c) for c in x.split("+")]
