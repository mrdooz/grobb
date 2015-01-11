class Graph():
	class Node():
		def __init__(self, name):
			self.name = name
			self.incoming = []

		def __repr__(self):
			return self.name

	def __init__(self):
		self.nodes = {}

	def add_node(self, name, parent = None):
		if name not in self.nodes:
			self.nodes[name] = Graph.Node(name)

		if parent:
			self.nodes[parent].incoming.append(self.nodes[name])

	def collect_leaves(self):
		s = []
		for k, v in self.nodes.iteritems():
			if len(v.incoming) == 0:
				s.append(v)

		for x in s:
			del(self.nodes[x.name])

		return s

	def topological_sort(self):
		res = []
		# create set of nodes with no incoming edges
		s = self.collect_leaves()

		while len(s) > 0:
			cur = s.pop()
			res.append(cur)

			for k,v in self.nodes.iteritems():
				if cur in v.incoming:
					v.incoming.remove(cur)

			s = s + self.collect_leaves()

		return res
