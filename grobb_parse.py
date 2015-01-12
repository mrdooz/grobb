import sys
import os
import graph
import argparse
import collections
from pyparsing import Word, Optional, ZeroOrMore, Suppress, OneOrMore, Group, ParseException, Literal, Keyword, alphas, alphanums
from jinja2 import Environment, PackageLoader, FileSystemLoader

ENV = Environment(loader=FileSystemLoader('./templates'), lstrip_blocks=True, trim_blocks=True)
GRAPH = graph.Graph()

# all the currently loaded modules (tail is the newest)
module_stack = []
processed_modules = set()
struct_by_module = collections.defaultdict(set)
dependencies = collections.defaultdict(set)

builtin_types = set(['int', 'float', 'bool', 'string', 'vec2', 'vec3', 'vec4', 'mat2', 'mat3', 'mat4'])

def parse(input):
	# keywords
	struct_lit = Keyword('struct')
	import_lit = Keyword('import')
	type_alias_lit = Keyword('alias')

	# types
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

	builtin_type_list = int_lit ^ float_lit ^ bool_lit ^ string_lit ^ vec2_lit ^ vec3_lit ^ vec4_lit ^ mat2_lit ^ mat3_lit ^ mat4_lit
	type_lit = (custom_lit ^ builtin_type_list)
	full_type_lit = Group(type_lit + Optional(array_lit))

	parent_group = Suppress(colon) + identifier

	member = Group(full_type_lit + identifier + Suppress(semi))

	alias_group = (Suppress(type_alias_lit) + builtin_type_list + Suppress(equals) + identifier + Suppress(semi)).setParseAction(create_type_alias)

	struct_group = (Suppress(struct_lit) + Group(identifier + Optional(parent_group)) + Suppress(l_brace) 
					+ Group(OneOrMore(member)) + Suppress(r_brace + semi)).setParseAction(create_struct)

	import_group = (Suppress(import_lit) + filename_lit).setParseAction(process_import)

	grobb_file = ZeroOrMore(alias_group | struct_group | import_group)

	grobb_file.parseString(input)

type_alias = {}
structs = {}

def safe_mkdir(path):
	try:
		os.mkdir(path)
	except OSError:
		pass

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
			is_array = len(type) > 1
			s.add_member(Member(type[0], is_array, name))

def create_type_alias(s, l, t):
	tt = t[0]
	if tt in type_alias:
		print 'Duplicate type alias found: %s' % tt
		exit(1)
	type_alias[tt] = t[1]

def process_import(s, l, t):
	import_name = ''.join(t)
	cur_module = module_stack[-1]
	dependencies[cur_module].add(import_name)
	# if the module hasn't been seen already, add it to the processing stack, and parse it
	if not import_name in processed_modules:
		module_stack.append(import_name)
		r = open(import_name).read()
		parse(r)
		processed_modules.add(import_name)
		module_stack.pop()

class Member():
	def __init__(self, type, is_array, name):
		self.type = type
		self.is_array = is_array
		self.name = name
		self.print_type = type
		# if the type isn't built in, use title case
		if not type in builtin_types:
			self.print_type = type.title()

		self.inner_type = self.print_type
		if is_array:
			self.print_type = 'vector<%s>' % self.inner_type

	def __repr__(self):
		return "%s: %s%s" % (self.name, self.type, '[]' if self.array else '')

	def is_builtin(self):
		return self.type in builtin_types

class Struct():
	def __init__(self, name):
		self.name = name
		self.members = []
		GRAPH.add_node(name)
		self.module = module_stack[-1]
		struct_by_module[self.module].add(name)

	def __repr__(self):
		return self.name + ':' + repr(self.members)

	def add_member(self, member):
		self.members.append(member)
		# if the member type isn't a built in type, add an edge from the member to the struct
		# (the member is a leaf of the struct)
		if not member.is_builtin():
			n = member.type
			GRAPH.add_node(n, self.name)

def underscore_to_sentence(str):
	s = str.split('_')
	return ''.join(map(lambda x: x.title(), s))

parser = argparse.ArgumentParser()
parser.add_argument("--lib_dir", help="location of additional cpp files", default='../', action="store")
parser.add_argument("--namespace", action="store")
parser.add_argument("input")
args = parser.parse_args()

out_dir = 'gen'
safe_mkdir(out_dir)

module_name = args.input
module_stack.append(module_name)
r = file(module_name).read()

parse(r)

# perform a topological sort over the types so we can print them in non-dependant order
order = GRAPH.topological_sort()

# output the generated code per module
for module, ss in struct_by_module.iteritems():
	# grab the structs that are in the current module
	to_process = [x.name for x in order if x.name in ss]
	params = []
	for name in to_process:
		s = structs[name]
		members = []
		for member in s.members:
			members.append({
				'name': member.name, 
				'is_array': member.is_array,
				'print_type': member.print_type,
				'inner_type': member.inner_type,
				'parser': 'Parse' + member.inner_type.title()
			})
		params.append({ 
			'name': underscore_to_sentence(name), 
			'members': members
		})

	head, tail = os.path.splitext(module)
	types_hpp_base = head + '.types.hpp'
	parse_hpp_base = head + '.parse.hpp'
	parse_cpp_base = head + '.parse.cpp'
	types_hpp_file = os.path.join(out_dir, types_hpp_base)
	parse_hpp_file = os.path.join(out_dir, parse_hpp_base)
	parse_cpp_file = os.path.join(out_dir, parse_cpp_base)

	type_deps = []
	parse_deps = []
	for dep in dependencies[module]:
		dep_head, _ = os.path.splitext(dep)
		type_deps.append(dep_head + '.types.hpp')
		parse_deps.append(dep_head + '.parse.hpp')

	template = ENV.get_template('types_hpp.tmpl')
	types_hpp = template.render({
		'structs': params, 
		'type_deps': type_deps,
		'namespace': args.namespace
	})
	open(types_hpp_file, 'wt').writelines(types_hpp)

	template = ENV.get_template('parse_hpp.tmpl')
	parse_hpp = template.render({
		'structs': params, 
		'parse_deps': parse_deps,
		'namespace': args.namespace
	})
	open(parse_hpp_file, 'wt').writelines(parse_hpp)

	template = ENV.get_template('parse_cpp.tmpl')
	parse_cpp = template.render({
		'structs': params, 
		'parse_deps': parse_deps, 
		'type_deps': type_deps, 
		'parse_hpp': parse_hpp_base,
		'types_hpp': types_hpp_base,
		'lib_dir': args.lib_dir,
		'namespace': args.namespace
	})
	open(parse_cpp_file, 'wt').writelines(parse_cpp)

