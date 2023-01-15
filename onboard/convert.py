from json import loads
from board import GP0, GP1

from kmk.keys import KC as kc, Key
from kmk.modules.layers import Layers as L
from kmk.modules.modtap import ModTap
from kmk.modules.split import Split, SplitType, SplitSide

from display import OLED
from led_pwm import LED

LED_INSTALLED = True
OLED_INSTALLED = False

class Layers(L):
    def __init__(self, km):
        self.km = km

        if LED_INSTALLED:
            self.led = LED(self.km)

        if OLED_INSTALLED:
            self.oled = OLED(self.km)
        
        super().__init__()

    # swap layers
    def _to_pressed(self, key, kbd, *args, **kwargs):
        if LED_INSTALLED: 
            self.led.layerShine(key.meta.layer)

        if OLED_INSTALLED:
            self.oled.clear()
            self.oled.showLayer(self.km.layerOrder, key.meta.layer)

        super()._to_pressed(key, kbd, *args, **kwargs)

    # toggle led shine
    def _tg_pressed(self, key, kbd, *args, **kwargs):
        if LED_INSTALLED:
            self.led.shouldToggle = not self.led.shouldToggle
            print('should shine' if self.led.shouldToggle else "shouldn't shine")

    def _tg_released(self, key, kbd, *args, **kwargs):
        print('idk if i need this')

class Keymap:
    def asKC(self, char, layer):
        if char is None:
            return None
        chord = None

        for key in char.split("+"):
            if key[0] == "F":
                try:
                    int(key[1:])
                    tc = key
                except:
                    isl = 1 + self.layers[layer]["sublayers"].index("Fun")
                    if isl > 0:
                        funlayer = self.layerOrder[layer][isl]
                        return kc.MO(funlayer)
                    tc = "trns"
            elif key == "Lnu":
                keys = sorted(self.layerOrder.keys())
                nl = keys[keys.index(layer) - 1]
                return kc.TO(self.layerOrder[nl][0])
            elif key == "Lne":
                keys = sorted(self.layerOrder.keys())
                pl = keys.index(layer) + 1
                if pl == len(keys):
                    pl = keys[0]
                else:
                    pl = keys[pl]
                return kc.TT(self.layerOrder[pl][0])
            elif key == "Etg":
                return kc.TG(0)
            elif len(key) == 1:
                cn = ord(key)

                # is a number
                if cn >= 48 and cn <= 57:
                    tc = f"N{key}"
                else:
                    tc = key
            elif len(key) == 3:
                table = {
                    "Esc": "esc",
                    "Tab": "tab",
                    "Spc": "spc",
                    "Sul": "left_super",
                    "Sur": "right_super",
                    "All": "lalt",
                    "Alr": "ralt",
                    "Bsp": "bksp",
                    "Ctl": "lctl",
                    "Ctr": "rctl",
                    "Ent": "ent",
                    "Dho": "home",
                    "Den": "end",
                    "Dup": "up",
                    "Ddo": "down",
                    "Dle": "left",
                    "Dri": "right",
                    "Ins": "ins",
                    "Dpu": "pgup",
                    "Dpd": "pgdn",
                    "Del": "del",
                    "Pst": "trns",
                    "Lsh": "lsft",
                    "Rsh": "rsft",
                    "Plu": "+",
                }
                tc = table[key]

            if chord is None:
                chord = kc[tc.upper()]
            else:
                chord = chord(kc[tc.upper()])

        return chord

    def __init__(self, kbd, side, led):
        self.layout = []
        self.side = side

        self.kbd = kbd
        self.kbd.modules.append(Layers(self))
        self.kbd.modules.append(ModTap())

        self.split = Split(
            data_pin=GP1 if side == 'left' else GP0,
            data_pin2=GP0 if side == 'left' else GP1,
            use_pio=True
        )
        self.kbd.modules.append(self.split)

        with open("layout.json", "r") as f:
            j = loads(f.read())
            self.nrows = j["nrows"]
            self.ncols = j["ncols"]
            self.layers = j["layers"]
            self.start = j["start"]

        self.layerOrder = {}
        i = 0
        for main in self.layers:
            self.layerOrder[main] = [i]
            i += 1
            for sub in self.layers[main]["sublayers"]:
                self.layerOrder[main] += [i]
                i += 1

        self.kbd.active_layers[-1] = self.layerOrder[self.start][0]
        lm = [[] for _ in range(i)]

        for kl in sorted(self.layers.keys()):
            layer = self.layers[kl]
            l = self.layerOrder[kl]

            for ir in range(self.nrows):
                r = ir

                for char in layer[f"{r}"]:
                    if isinstance(char, list):
                        for isl, sl in enumerate(self.layerOrder[kl]):
                            if isl >= len(char):
                                lm[sl] += [None]
                                continue

                            slc = char[isl]
                            if isl == 1 or slc == 0:
                                continue
                            if isl == 0 and char[isl + 1] != 0:
                                lm[sl] += [
                                    kc.MT(
                                        self.asKC(slc, kl),
                                        self.asKC(char[isl + 1], kl),
                                        prefer_hold=False,
                                    )
                                ]
                            else:
                                lm[sl] += [self.asKC(slc, kl)]
                    else:
                        lm[l[0]] += [self.asKC(char, kl)]
                        if len(lm) > 1:
                            lm[l[1]] += [kc.LSFT(self.asKC(char, kl))]
                        for sl in l[2:]:
                            lm[sl] += [None]

        self.layout = lm
        self.kbd.keymap = self.layout

        if OLED_INSTALLED:
            self.oled.clear()
            self.oled.showLayer(self.layerOrder, self.layerOrder[self.start][0])
