import sys
import os
import graph
import argparse
import collections
import glob
from pyparsing import *
from itertools import *
from jinja2 import Environment, PackageLoader, FileSystemLoader

VERBOSE = 0

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def underscore_to_sentence(str):
	s = str.split('_')
	return ''.join(map(lambda x: x.title(), s))

def first_upper(str):
	return str[0].upper() + str[1:]

def render_to_file(file, template_name, args):
	template = ENV.get_template(template_name)
	res = template.render(args)
	open(file, 'wt').writelines(res)

def safe_mkdir(path):
	try:
		os.mkdir(path)
	except OSError:
		pass

builtin_types = set(['int', 'float', 'bool', 'string', 'color', 'vec2', 'vec3', 'vec4', 'mat2', 'mat3', 'mat4'])

# to ensure that the script can be run from any dir, we need to extract
# the script dir to use as a base
script_dir, _ = os.path.split(os.path.realpath(__file__))
template_dir = os.path.join(script_dir, 'templates')
ENV = Environment(loader=FileSystemLoader(template_dir), lstrip_blocks=True, trim_blocks=True)

GRAPH = graph.Graph()

# all the currently loaded modules (tail is the newest). stored as (path, file)
module_stack = []
processed_modules = set()
struct_by_module = collections.defaultdict(set)
dependencies = collections.defaultdict(set)

type_alias = {}
structs = {}

def parse(input):

	array_lit = Literal('[]')
	l_brace = Literal('{')
	r_brace = Literal('}')
	l_paren = Literal('(')
	r_paren = Literal(')')
	semi = Literal(';')
	equals = Literal('=');
	colon = Literal(':')
	quote = Literal("'")
	hashmark = Literal('#')
	at = Literal('@')

	# keywords
	struct_lit = Keyword('struct')
	import_lit = Keyword('import')
	type_alias_lit = Keyword('alias')

	# types
	int_lit = Keyword('int')
	float_lit = Keyword('float')
	bool_lit = Keyword('bool')
	string_lit = Keyword('string')

	color_lit = Keyword('color')

	vec2_lit = Keyword('vec2')
	vec3_lit = Keyword('vec3')
	vec4_lit = Keyword('vec4')

	mat2_lit = Keyword('mat2')
	mat3_lit = Keyword('mat3')
	mat4_lit = Keyword('mat4')

	custom_lit = Word(alphas, alphanums + '_')
	identifier = Word(alphas, alphanums + '_')

	string_value = Suppress(quote) + identifier + Suppress(quote)

	filename_lit = (Suppress(quote) + identifier + Optional('.' + identifier) + Suppress(quote))
	import_lit = Keyword('import')

	# attributes can only have a subset of types
	attr_type_list = int_lit ^ float_lit ^ bool_lit ^ string_lit
	builtin_type_list = int_lit ^ float_lit ^ bool_lit ^ string_lit ^ color_lit ^ vec2_lit ^ vec3_lit ^ vec4_lit ^ mat2_lit ^ mat3_lit ^ mat4_lit
	type_lit = (custom_lit ^ builtin_type_list)
	full_type_lit = Group(type_lit + Optional(array_lit))

	attr_arg = Group(identifier + Suppress(colon) + Word(alphanums))
	attr_args = Suppress(l_paren) + ZeroOrMore(attr_arg + Suppress(Optional(','))) + Suppress(r_paren)

	comment = (hashmark + restOfLine).suppress()
	attribute_lit = Group(Suppress(at) + identifier + attr_args).setParseAction(apply_attribute)

	parent_group = Suppress(colon) + identifier

	struct_member = Group(ZeroOrMore(attribute_lit)) + full_type_lit + identifier + Suppress(semi)

	alias_group = (Suppress(type_alias_lit) + builtin_type_list + Suppress(equals) 
		+ identifier + Suppress(semi)).setParseAction(create_type_alias)

	struct_group = (Group(Optional(OneOrMore(attribute_lit))) + Suppress(struct_lit) 
		+ Group(identifier + Optional(parent_group)) + Suppress(l_brace) 
		+ Group(ZeroOrMore(struct_member)) + Suppress(r_brace + semi)).setParseAction(create_struct)

	import_group = (Suppress(import_lit) + filename_lit + Suppress(semi)).setParseAction(process_import)

	grobb_file = ZeroOrMore(alias_group | struct_group | import_group)
	grobb_file.ignore(comment)

	grobb_file.parseString(input)

def apply_attribute(str, loc, toks):
	if VERBOSE > 2:
		print 'found attribute: ', toks
	pass

def collect_attributes(input):
	if len(input) == 0:
		return None

	res = {}
	for attr in input:
		# first item is the attribute name, then the key/value pairs
		name = attr[0]
		attrs = {}
		for x in attr[1:]:
			attrs[x[0]] = x[1]
		res[name] = attrs
	return res

def create_struct(s, l, toks):
	# toks[0] = any attributes
	# toks[1] = struct class (and optional parent)
	# toks[2] = struct members

	# the type can have an optional parent
	name = toks[1][0]
	parent = None
	if len(toks[1]) > 1: parent = toks[1][1]
	s = Struct(name)
	structs[name] = s
	members = toks[2]
	if VERBOSE > 0: 
		print 'Adding struct: %s' % (name)

	# add the attributes
	s.attributes = collect_attributes(toks[0])
	# import pdb; pdb.set_trace()

	# add the parents members first
	if parent:
		p = structs[parent]
		for member in p.members:
			s.add_member(member)

	# add the members
	for attrs, type, name in grouper(members, 3):
		# [0] = attributes
		# [1] = type (tuple)
		# [2] = name
		attributes = collect_attributes(attrs)
		# type = member[1]
		# if the type is aliased, use the alias instead
		base_type = type_alias.get(type[0], type[0])
		# name = member[2]
		is_array = len(type) > 1
		s.add_member(Member(base_type, attributes, is_array, name))

def create_type_alias(s, l, toks):
	tt = toks[0]
	if tt in type_alias:
		print 'Duplicate type alias found: %s' % tt
		exit(1)
	print 'Found alias %s -> %s' % (tt, toks[1])
	type_alias[tt] = toks[1]

def process_import(s, l, t):
	import_name = ''.join(t)
	(module_path, module_name) = module_stack[-1]
	dependencies[module_name].add(import_name)
	# if the module hasn't been seen already, add it to the processing stack, and parse it
	if not import_name in processed_modules:
		# the imported module has the same path as the one that imported it. yeah, this
		# will break for more complicated relative imports, but i'll solve that when i
		# get there :)
		module_stack.append((module_path, import_name))
		r = open(os.path.join(module_path, import_name)).read()
		parse(r)
		processed_modules.add(import_name)
		module_stack.pop()

class Member():
	def __init__(self, type, attributes, is_array, name):
		self.type = type
		self.attributes = attributes
		self.is_array = is_array
		self.name = name
		self.print_type = type
		# if the type isn't built in, use title case
		if not type in builtin_types:
			self.print_type = underscore_to_sentence(type)

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
		self.attributes = {}
		GRAPH.add_node(name)
		self.module_path, self.module = module_stack[-1]
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


def process_file(args, first_file, filename):
	# note, we drop the directory part of the input when we save to module_name
	_, module_name = os.path.split(filename)
	p = os.path.dirname(os.path.realpath(filename))
	module_path = os.path.join(p, module_name)
	module_stack.append((p, module_name))
	r = file(module_path).read()
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
					'alias': type_alias,
					'attributes': member.attributes,
					'is_array': member.is_array,
					'print_type': member.print_type,
					'inner_type': member.inner_type,
					'parser': 'Parse' + first_upper(member.inner_type),
					'writer': 'Serialize'
				})
			params.append({ 
				'name': underscore_to_sentence(name),
				'attributes': s.attributes,
				'members': members
			})

		module_base, tail = os.path.splitext(module)
		types_hpp_base = module_base + '.types.hpp'
		parse_hpp_base = module_base + '.parse.hpp'
		parse_cpp_base = module_base + '.parse.cpp'
		compare_hpp_base = module_base + '.compare.hpp'
		compare_cpp_base = module_base + '.compare.cpp'
		imgui_hpp_base = module_base + '.imgui.hpp'
		imgui_cpp_base = module_base + '.imgui.cpp'
		types_hpp_file = os.path.join(out_dir, types_hpp_base)
		parse_hpp_file = os.path.join(out_dir, parse_hpp_base)
		parse_cpp_file = os.path.join(out_dir, parse_cpp_base)
		compare_hpp_file = os.path.join(out_dir, compare_hpp_base)
		compare_cpp_file = os.path.join(out_dir, compare_cpp_base)
		imgui_hpp_file = os.path.join(out_dir, imgui_hpp_base)
		imgui_cpp_file = os.path.join(out_dir, imgui_cpp_base)

		type_deps = []
		parse_deps = []
		for dep in dependencies[module]:
			# only add the dependency if the module has any structs
			if dep in struct_by_module:
				dep_head, _ = os.path.splitext(dep)
				type_deps.append(dep_head + '.types.hpp')
				parse_deps.append(dep_head + '.parse.hpp')

		# compute relative path from the output dir to the directory containing
		# the parse types
		types_file = None
		if args.types_file:
			head, tail = os.path.split(args.types_file)
			if not head: head = './'
			types_file = os.path.join(os.path.relpath(head, out_dir), tail)

		template_args = {
			'structs': params, 
			'alias': type_alias,
			'type_deps': type_deps,
			'parse_deps': parse_deps,
			'parse_hpp': parse_hpp_base,
			'types_hpp': types_hpp_base,
			'compare_hpp': compare_hpp_base,
			'types_file': types_file,
			'basic_types': args.basic_types,
			'lib_dir': args.lib_dir if args.lib_dir else '',
			'namespace': args.namespace
		}

		render_to_file(types_hpp_file, 'types_hpp.j2', template_args)
		render_to_file(parse_hpp_file, 'parse_hpp.j2', template_args)
		render_to_file(parse_cpp_file, 'parse_cpp.j2', template_args)

		if args.compare:
			render_to_file(compare_hpp_file, 'compare_hpp.j2', template_args)
			render_to_file(compare_cpp_file, 'compare_cpp.j2', template_args)

		if args.imgui:
			render_to_file(imgui_hpp_file, 'imgui_hpp.j2', template_args)
			render_to_file(imgui_cpp_file, 'imgui_cpp.j2', template_args)

		if args.generate_lib and first_file:
			files = { 
				'input_buffer_hpp.j2': 'input_buffer.hpp',
				'input_buffer_cpp.j2': 'input_buffer.cpp',
				'output_buffer_hpp.j2': 'output_buffer.hpp',
				'output_buffer_cpp.j2': 'output_buffer.cpp',
				'parse_base_hpp.j2': 'parse_base.hpp',
				'parse_base_cpp.j2': 'parse_base.cpp'
			}

			for t, f in files.iteritems():
				render_to_file(os.path.join(out_dir, f), t, template_args)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--lib_dir", help="location of additional cpp files", action="store")
group.add_argument("--generate_lib", help='Should the library files also be generated', default=False, action='store_true')
parser.add_argument("--namespace", action="store")
parser.add_argument("--out_dir", help='Output directory', action='store', default='gen')
parser.add_argument("--basic_types", help='Only generate code for basic types (no vector/matrix)', action='store_true')
parser.add_argument('--types_file', action='store')
parser.add_argument('--imgui', action='store_true')
parser.add_argument('--compare', action='store_true')
parser.add_argument('--verbose', type=int, action='store', default=0)
parser.add_argument("input")
args = parser.parse_args()

out_dir = args.out_dir
VERBOSE = args.verbose
safe_mkdir(out_dir)

first_file = True
for input in glob.glob(args.input):
	process_file(args, first_file, input)
	first_file = False

