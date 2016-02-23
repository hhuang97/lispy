
class scope:
    def __init__(self, defs={}):
        self._defins = defs

    def get(self, thing):
        return self._defins[thing]
