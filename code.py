print("Starting")

import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from convert import Keymap
from json import loads

kbd = KMKKeyboard()


with open("pinmap.json") as pinmap:
    pm = loads(pinmap.read())
    cols = pm["cols"]
    rows = pm["rows"]
    if pm["ncols"] != len(cols):
        raise Exception("Check number of cols")

    if pm["nrows"] != len(rows):
        raise Exception("Check number of rows")

    kbd.col_pins = [
        getattr(board, f"GP{cols[x]}") for x in reversed(sorted(cols.keys()))
    ]
    kbd.row_pins = [getattr(board, f"GP{x}") for x in rows]

kbd.diode_orientation = DiodeOrientation.COL2ROW

km = Keymap(kbd)

if __name__ == "__main__":
    kbd.go()
