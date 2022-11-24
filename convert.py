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
            print("un fn shift")
        elif not self.shfPressed and len(kbd.active_layers) > 2:
            self.shfPressed = True
            kbd.remove_key(Key(1003))
            kbd.add_key(kc.LSFT)
            print("fn shift")

        return super().before_hid_send(kbd)


class Keymap:
    def asKC(self, char, layer=None):
        if char is None:
            return None
        chord = None

        for key in char.split("+"):
            if key[0] == "F":
                try:
                    int(key[1:])
                    tc = key
                except:
                    funlayer = 1 + self.deflayer["sublayers"].index("Fun")
                    if funlayer > 0:
                        return kc.MO(funlayer)
                    tc = "trns"
            elif key == "Shf":
                shflayer = 1 + self.deflayer["sublayers"].index("Shf")
                if shflayer > 0:
                    return kc.MO(shflayer)
                tc = "lsft"
            elif key == "Lyp":
                nl = [ k for k in self.layerOrder if k != layer ][0]
                return kc.TO(self.layerOrder[nl][0])
            elif key == "Lyn":
                pl = [ k for k in self.layerOrder if k != layer ][-1]
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
                }
                tc = table[key]

            if chord is None:
                chord = kc[tc.upper()]
            else:
                chord = chord(kc[tc.upper()])

        return chord

    def __init__(self, kbd, side):
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
            self.deflayer = self.layers[j["start"]]

        self.layerOrder = {}
        i = 0
        for main in self.layers:
            self.layerOrder[main] = [i]
            i += 1
            for sub in self.layers[main]["sublayers"]:
                self.layerOrder[main] += [i]
                i += 1

        lm = [[] for _ in range(i)]
        for kl in self.layers:
            layer = self.layers[kl]
            l = self.layerOrder[kl]

            for ir in range(self.nrows):
#                 if side == "left":
                r = ir
#                 else:
#                     r = ir + self.nrows
#                     layer[f"{r}"].reverse()
                
                for char in layer[f"{r}"]:
                    if isinstance(char, list):
                        for isl, sl in enumerate(self.layerOrder[kl]):
                            if isl >= len(char):
                                lm[sl] += [None]
                                continue

                            slc = char[isl]
                            if slc == 0:
                                lm[sl] += [kc.LSFT(self.asKC(char[0]), kl)]
                            else:
                                lm[sl] += [self.asKC(slc, kl)]
                    else:
                        lm[l[0]] += [self.asKC(char, kl)]
                        if len(lm) > 1:
                            lm[l[1]] += [
                                kc.LSFT(self.asKC(char, kl))
                            ]
                        for sl in l[2:]:
                            lm[sl] += [None]

        self.layout = lm
        self.kbd.keymap = self.layout
        print(*[len(x) for x in self.layout])