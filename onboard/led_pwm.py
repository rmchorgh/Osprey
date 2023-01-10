from board import GP15, GP22, GP26_A0
from time import sleep
from digitalio import DigitalInOut, Direction

b = DigitalInOut(GP15)
r = DigitalInOut(GP22)
g = DigitalInOut(GP26_A0)

def shine(R, G, B):
    leds = [r, g, b]

    for l in leds:
        l.direction = Direction.OUTPUT

    r.value = R
    g.value = G
    b.value = B
