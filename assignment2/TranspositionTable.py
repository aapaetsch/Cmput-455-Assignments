class TT(object):
    def __init__(self):
        self.table = {}

    def __repr__(self):
        return self.table.__repr__()

    def store(self, code, score):
        self.table[code] = {}
        

    def lookup(self, code):
        return self.table.get(code)

# class TT(object):
# 	def __init__(self):
# 		self.table = {}

# 	def __repr__(self):
# 		return self.table.__repr__()

# 	def store(self, code, score, isHeuristic):
# 		self.table[code] = {}
# 		self.table[code]['heuristic'] = isHeuristic
# 		self.table[code]['score'] = score

# 	def edit(self, code, score, isHeuristic):
# 		self.table[code]['heuristic'] = isHeuristic
# 		self.table[code]['score'] = score

# 	def lookup(self, code):
# 		return self.table.get(code)