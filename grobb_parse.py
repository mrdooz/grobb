from pyparsing import Word, Optional, ZeroOrMore, Suppress, OneOrMore, Group, ParseException, Literal, Keyword, alphas, alphanums
import sys
from jinja2 import Environment, PackageLoader, FileSystemLoader

ENV = Environment(loader=FileSystemLoader('./templates'), lstrip_blocks=True, trim_blocks=True)

struct_lit = Keyword('struct')
demo_lit = Keyword('demo')
effect_lit = Keyword('effect')
import_lit = Keyword('import')

vec2_type_lit = Keyword('vec2_type')
vec3_type_lit = Keyword('vec3_type')
vec4_type_lit = Keyword('vec4_type')

mat2_type_lit = Keyword('mat2_type')
mat3_type_lit = Keyword('mat3_type')
mat4_type_lit = Keyword('mat4_type')

int_lit = Keyword('int')
float_lit = Keyword('float')
bool_lit = Keyword('bool')
string_lit = Keyword('string')

vec2_lit = Keyword('vec2')
vec3_lit = Keyword('vec3')
vec4_lit = Keyword('vec4')

mat2_lit = Keyword('mat2')
mat3_lit = Keyword('mat3')
mat4_lit = Keyword('mat4')

builtin_types = set(['int', 'float', 'bool', 'string', 'vec2', 'vec3', 'vec4', 'mat2', 'mat3', 'mat4'])

custom_lit = Word(alphas, alphanums + '_')
identifier = Word(alphas, alphanums + '_')

string_value = Suppress(Literal("'")) + identifier + Suppress(Literal("'"))

filename_lit = (Suppress(Literal("'")) + identifier + Optional('.' + identifier) + Suppress(Literal("'")))
import_lit = Keyword('import')

array_lit = Literal('[]')
l_brace = Literal('{')
r_brace = Literal('}')
semi = Literal(';')
equals = Literal('=');
colon = Literal(':')

type_lit = (custom_lit ^ int_lit ^ float_lit ^ bool_lit ^ string_lit ^ vec2_lit ^ vec3_lit ^ vec4_lit ^ mat2_lit ^ mat3_lit ^ mat4_lit).setName('type')
full_type_lit = Group(type_lit + Optional(array_lit))

parent_group = Suppress(colon) + identifier

var = Group(full_type_lit + identifier + Suppress(semi))

def create_struct(s, l, t):
	# the type can have an optional parent
	name = t[0][0]
	parent = parent = t[0][1] if len(t[0]) > 1 else None
	s = Struct(name)
	structs[name] = s
	# add the members
	if len(t) > 1:
		# add the parents members first
		if parent:
			p = structs[parent]
			for member in p.members:
				s.add_member(member)

		for member in t[1]:
			type = member[0]
			name = member[1]
			s.add_member(Type(type[0], len(type) > 1, name))
	# print t

def create_type_alias(s, l, t):
	tt = t[0]
	if tt in type_alias:
		print 'Duplicate type alias found: %s' % tt
		exit(1)
	type_alias[tt] = t[1]

def process_import(s, l, t):
	import_name = ''.join(t)
	r = open(import_name).read()
	grobb_file.parseString(r)

type_alias = {}
structs = {}

type_group = ((vec2_type_lit | vec3_type_lit | vec4_type_lit | mat2_type_lit | mat3_type_lit | mat4_type_lit)
			  + Suppress(equals) + string_value + Suppress(semi)).setParseAction(create_type_alias)

struct_group = (Suppress(struct_lit) + Group(identifier + Optional(parent_group)) + Suppress(l_brace) 
				+ Group(OneOrMore(var)) + Suppress(r_brace + semi)).setParseAction(create_struct)

import_group = (Suppress(import_lit) + filename_lit).setParseAction(process_import)

grobb_file = ZeroOrMore(type_group('t') | struct_group('s') | import_group)

class Type():
	def __init__(self, type, array, name):
		self.type = type
		self.array = array
		self.name = name

	def __repr__(self):
		return "%s: %s%s" % (self.name, self.type, '[]' if self.array else '')

	def is_builtin(self):
		return self.type in builtin_types

class Node():
	def __init__(self, name):
		self.name = name
		self.incoming = []

	def __repr__(self):
		return self.name

graph = {}

def add_node(name):
	if name not in graph:
		graph[name] = Node(name)

class Struct():
	def __init__(self, name):
		self.name = name
		self.members = []
		add_node(name)

	def __repr__(self):
		return self.name + ':' + repr(self.members)

	def add_member(self, member):
		self.members.append(member)
		# if the member type isn't a built in type, add an edge from the member to the struct
		# (the member is a leaf of the struct)
		if not member.is_builtin():
			n = member.type
			add_node(n)
			graph[self.name].incoming.append(graph[n])

def collect_leaves():
	s = []
	for k, v in graph.iteritems():
		if len(v.incoming) == 0:
			s.append(v)

	for x in s:
		del(graph[x.name])

	return s

def underscore_to_sentence(str):
	s = str.split('_')
	return ''.join(map(lambda x: x.title(), s))

def topological_sort():
	res = []
	# create set of nodes with no incoming edges
	s = collect_leaves()

	while len(s) > 0:
		cur = s.pop()
		res.append(cur)

		for k,v in graph.iteritems():
			if cur in v.incoming:
				v.incoming.remove(cur)

		s = s + collect_leaves()

	return res


r = open(sys.argv[1]).read()
grobb_file.parseString(r)

# perform a topological sort over the types so we can print them in non-dependant order
order = topological_sort()
t = []
for x in order:
	name = x.name
	s = structs[name]
	members = []
	for member in s.members:
		members.append({'name': member.name, 'type': member.type})
	ss = { 'name': underscore_to_sentence(name), 'members': members }
	t.append(ss)
print order

template = ENV.get_template('c_struct.tmpl')
print template.render({'structs': t})
