from board import GP15, GP22, GP26_A0
from pwmio import PWMOut as pwm

class LED:
    shouldToggle = False
    MAX = 65535
    pins = [GP22, GP26_A0, GP15]

    def __init__(self, km):
        self.km = km
        self.r, self.g, self.b = map(lambda x: pwm(x, frequency=5000, duty_cycle=self.MAX), self.pins)

    def calculateDutyCycle(self, x):
        return int(self.MAX * (1 - (x / 255)))

    def shine(self, r, g, b):
        self.r.duty_cycle = self.calculateDutyCycle(r)
        self.g.duty_cycle = self.calculateDutyCycle(g)
        self.b.duty_cycle = self.calculateDutyCycle(b)
        
    def layerShine(self, active):
        for o in sorted(self.km.layerOrder):
            print(f'o is {o}, looking for {active}')
            if self.km.layerOrder[o][0] == active:
                print('found layer')
                r, g, b = self.km.layers[o]['color']
                self.shine(r, g, b)

                if self.shouldToggle:
                    sleep(0.25)
                    self.shine(0, 0, 0)

                break
