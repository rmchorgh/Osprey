import board
from digitalio import DigitalInOut, Direction

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation

from storage import getmount
from time import sleep
from json import loads
from convert import Keymap

kbd = KMKKeyboard()

side = "right" if str(getmount("/").label)[-1] == "R" else "left"
with open(f"pinmap.{side}.json") as pinmap:
    pm = loads(pinmap.read())
    cols = pm["cols"]
    rows = pm["rows"]
    if pm["ncols"] != len(cols):
        raise Exception("Check number of cols")

    if pm["nrows"] != len(rows):
        raise Exception("Check number of rows")

    kbd.col_pins = [getattr(board, f"GP{x}") for x in cols]
    kbd.row_pins = [getattr(board, f"GP{x}") for x in rows]

kbd.debug_enabled = True
kbd.diode_orientation = DiodeOrientation.COL2ROW
km = Keymap(kbd, side)

if __name__ == "__main__":
    led = DigitalInOut(board.GP25)
    led.direction = Direction.OUTPUT
    led.value = True
    sleep(0.5)
    led.value = False
    kbd.go()
