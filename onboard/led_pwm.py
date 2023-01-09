from board import GP10, GP22, GP26
from time import sleep
from digitalio import DigitalInOut, Direction

def shine():
    g = DigitalInOut(GP10)
    b = DigitalInOut(GP22)
    r = DigitalInOut(GP26)

    leds = [r, g, b]

    for l in leds:
        l.direction = Direction.OUTPUT

    r.value = True
    g.value = True
    b.value = False
