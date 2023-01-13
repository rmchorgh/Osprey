from board import GP15, GP22, GP26_A0
from pwmio import PWMOut as pwm

LEDMAX = 65535

pins = [GP22, GP26_A0, GP15]
r, g, b = map(lambda x: pwm(x, frequency=5000, duty_cycle=LEDMAX), pins)

def per(x):
    v = LEDMAX * (1 - (x / 255))
    print(v)

    return int(v)

def layerShine(layers, order, active):
    for i, o in enumerate(sorted(order)):
        if order[o][0] == active:
            print(layers[o]['color'])
            red, green, blue = layers[o]['color']
            shine(red, green, blue)

def shine(red, green, blue):
    r.duty_cycle = per(red)
    g.duty_cycle = per(green)
    b.duty_cycle = per(blue)
