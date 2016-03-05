
class scope:
    def __init__(self, defs={}):
        self._defins = defs

    def get(self, thing):
        # TODO add custom error handling
        return self._defins[thing]

    def add(self, name, val):
        self._defins[name] = val

    def __copy__(self):
        return scope(self._defins.copy())
