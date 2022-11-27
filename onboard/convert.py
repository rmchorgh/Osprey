from json import loads
from board import GP0, GP1

from kmk.keys import KC as kc, Key
from kmk.modules.layers import Layers as L
from kmk.modules.modtap import ModTap
from kmk.modules.split import Split, SplitType


class Layers(L):
    def __init__(self, km):
        self.km = km
        self.shfPressed = False
        super().__init__()

    def before_hid_send(self, kbd):
        if self.shfPressed and len(kbd.active_layers) == 1:
            self.shfPressed = False
            kbd.remove_key(kc.LSFT)
        elif not self.shfPressed and len(kbd.active_layers) > 2:
            self.shfPressed = True
            kbd.remove_key(Key(1003))
            kbd.add_key(kc.LSFT)

        return super().before_hid_send(kbd)

    def _to_pressed(self, key, kbd, *args, **kwargs):
        self.km.oled.clear()
        for i in range(key.meta.layer):
            offset = (i + 1) * 3
            self.km.oled.row(offset, offset + 2)

        super()._to_pressed(key, kbd, *args, **kwargs)


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
            elif key == "Shf":
                isl = 1 + self.layers[layer]["sublayers"].index("Shf")
                if isl > 0:
                    shflayer = self.layerOrder[layer][isl]
                    return kc.MO(shflayer)
                tc = "lsft"
            elif key == "Lyp":
                keys = sorted(self.layerOrder.keys())
                nl = keys[keys.index(layer) - 1]
                return kc.TO(self.layerOrder[nl][0])
            elif key == "Lyn":
                keys = sorted(self.layerOrder.keys())
                pl = keys.index(layer) + 1
                if pl == len(keys):
                    pl = keys[0]
                else:
                    pl = keys[pl]
                return kc.TO(self.layerOrder[pl][0])
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
                    "Sup": "left_super",
                    "Alt": "lalt",
                    "Bsp": "bksp",
                    "Ctr": "lctl",
                    "Ent": "ent",
                    "Dho": "home",
                    "Den": "end",
                    "Dup": "up",
                    "Ddo": "down",
                    "Dle": "left",
                    "Dri": "right",
                    "Del": "del",
                    "Pst": "trns",
                    "Lyp": "trns",
                    "Lyn": "trns",
                    "Rsh": "rsft",
                    "Plu": "+",
                    "Lys": "trns",
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
        self.split = Split(split_type=SplitType.UART, data_pin=GP1, data_pin2=GP0)
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

        for kl in self.layers:
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
                            if slc == 0:
                                lm[sl] += [kc.LSFT(self.asKC(char[0], kl))]
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

        try:
            from display import OLED

            self.oled = OLED(led)
            self.oled.clear()
        except Exception as e:
            print(e)
