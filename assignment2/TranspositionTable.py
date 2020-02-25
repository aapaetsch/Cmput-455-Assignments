class TT(object):
    def __init__(self):
        self.table = {}

    def __repr__(self):
        return self.table.__repr__()

    def store(self, code, score):
        self.table[code] = score
        

    def lookup(self, code):
        return self.table.get(code)

