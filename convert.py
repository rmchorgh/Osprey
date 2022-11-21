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
    def asKC(self, key):
        if key is None:
            return None
        elif key == "Lyp":
            self.active = (min(self.maxLayers, self.active[0] + 1), 0)
            print("trying layer", self.active)
            try:
                return kc.TO(self.order[self.active])
            except KeyError:
                return kc.TRNS
        elif key == "Lyn":
            self.active = (max(0, self.active[0] - 1), 0)
            print("trying layer", self.active)
            try:
                return kc.TO(self.order[self.active])
            except KeyError:
                return kc.TRNS
        elif key == "Fun":
            if (self.active, 2) in self.order.keys():
                print("on fun sublayer")
                return kc.MO(self.order[self.active, 2])
            return kc.TRNS
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
                    "Shf": "lsft",
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
            tc = "perc"

        return kc[tc.upper()]

    def __init__(self, kbd):
        self.layout = []
        self.order = {}
        self.active = (0, 0)
        self.maxLayers = 0
        layerIndex = -1

        self.kbd = kbd
        self.kbd.modules.append(Layers())
        with open("layout.json", "r") as f:
            j = loads(f.read())
            for ikl, kl in enumerate(["mac"]):  #  j["layers"]
                l = j["layers"][kl]
                cols = [x for x in "fedcba"]
                lm = [
                    [None for x in range(10 * len(cols))]
                    for y in range(1 + len(l["sublayers"]))
                ]

                self.maxLayers += 1
                layerIndex += 1
                self.order[(ikl, 0)] = layerIndex

                for isl, sl in enumerate(l["sublayers"]):
                    layerIndex += 1
                    self.order[(ikl, isl + 1)] = layerIndex

                for ci, c in enumerate(cols):
                    for ri, char in enumerate(l[c]):
                        index = (ri * 6) + ci

                        if isinstance(char, list):
                            for isl, sl in enumerate(char):
                                if l["sublayers"][isl - 1] == "Shf" and sl == 0:
                                    lm[isl][index] = kc.LSFT(self.asKC(char[0]))
                                else:
                                    lm[isl][index] = self.asKC(sl)
                        else:
                            lm[0][index] = self.asKC(char)
                self.layout += lm

        self.kbd.keymap = self.layout
        print(self.layout[0])
        # self.kbd.keymap = [[kc.A for x in range(60)]]
