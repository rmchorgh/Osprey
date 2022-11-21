from json import loads
from kmk.keys import KC as kc, Key
from kmk.modules.layers import Layers as L


class Layers(L):
    def __init__(self, km):
        self.km = km
        self.shfPressed = False

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


class Keymap:
    def asKC(self, char):
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
                        tc = kc.MO(funlayer)
                    else:
                        tc = "trns"
            elif key == "Shf":
                shflayer = 1 + self.deflayer["sublayers"].index("Shf")
                if shflayer > 0:
                    tc = kc.MO(shflayer)
                else:
                    tc = "lsft"
            elif len(key) == 1:
                cn = ord(key)

                # is a number
                if cn >= 48 and cn <= 57:
                    tc = f"N{key}"
                else:
                    tc = key
            elif len(key) == 3:
                try:
                    # is a function greater than f9
                    int(key[1:])
                    tc = key
                except:
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
                    }
                    tc = table[key]
            else:
                tc = "trns"

            if chord is None:
                chord = kc[tc.upper()]
            else:
                chord = chord(tc.upper())

        return chord

    def __init__(self, kbd):
        self.layout = []

        self.kbd = kbd
        self.kbd.modules.append(Layers(self))

        with open("layout.row.json", "r") as f:
            j = loads(f.read())
            self.nrows = j["nrows"]
            self.ncols = j["ncols"]
            self.deflayer = j["layers"][j["start"]]
            self.nsublayers = len(self.deflayer["sublayers"])

        lm = [[] for _ in range(self.nsublayers)]
        for r in range(nrows):
            for char in self.deflayer[f"{r}"]:
                if isinstance(char, list):
                    for isl, sl in enumerate(char):
                        if sl == 0:
                            lm[1 + isl] += [kc.LSFT(self.asKC(char[0]))]
                        else:
                            lm[1 + isl] += [self.asKC(sl)]
                else:
                    lm[0] += [self.asKC(char)]
                    lm[1] += [kc.LSFT(self.asKC(char))]
                    for isl in range(2, self.nsublayers):
                        lm[isl] += [None]

        self.kbd.keymap = self.layout = lm
        print(self.layout[0])
