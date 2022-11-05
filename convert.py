from adafruit_hid.keycode import Keycode as K

# selected cols e f rows 6 8
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

                if x in table.keys():
                    c = table[x]
        elif l == 2:
            if x in dir(K):
                c = x
        elif l == 3:
            table = {
                "Shf": ["LEFT_SHIFT", "RIGHT_SHIFT"][side],
                "Sup": ["LEFT_GUI", "RIGHT_GUI"][side],
                "Tab": "TAB",
                "Bsp": "BACKSPACE",
                "Ent": "RETURN",
                "Ctr": ["LEFT_CONTROL", "RIGHT_CONTROL"][side],
                "Spc": "SPACEBAR",
            }

            if x in table.keys():
                c = table[x]

        if c is not None:
            return getattr(K, c)
        else:
            print(x)
            print(sorted(dir(K)[5:]))
            print("")

    def parse(x: str):
        if x is None:
            return

        return [Keycode.lookup(c) for c in x.split("+")]
