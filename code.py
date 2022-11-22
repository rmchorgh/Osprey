import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation

from json import loads
from convert import Keymap

kbd = KMKKeyboard()


with open("pinmap.right.json") as pinmap:
    pm = loads(pinmap.read())
    cols = pm["cols"]
    rows = pm["rows"]
    if pm["ncols"] != len(cols):
        raise Exception("Check number of cols")

    if pm["nrows"] != len(rows):
        raise Exception("Check number of rows")

    kbd.col_pins = [getattr(board, f"GP{x}") for x in cols]
    kbd.row_pins = [getattr(board, f"GP{x}") for x in rows]
    side = pm["side"]

kbd.diode_orientation = DiodeOrientation.COL2ROW
km = Keymap(kbd, side)

if __name__ == "__main__":
    kbd.go()
