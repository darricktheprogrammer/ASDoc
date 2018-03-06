"""
Docstring for main module in ASDocs.

A longer description...
"""
from xml.etree.ElementTree import SubElement
import re


def _pop_examples(desc):
	examples = []
	for p in desc.findall('p'):
		paragraph = p.text
		if paragraph.startswith('@example'):
			paragraph = paragraph.lstrip('@example ')
			paragraph = paragraph.strip()
			examples.append(paragraph)
			desc.remove(p)
	return examples, desc


def _format_description(desc):
	paragraphs = []
	for p in desc.findall('p'):
		try:
			paragraph = p.text.strip()
			paragraph = ' '.join([line.strip() for line in paragraph.splitlines()])
			paragraphs.append(paragraph)
		except AttributeError:
			paragraphs.append('')
	return '\n\n'.join(paragraphs)


def _pop_param_type(desc):
	type_regex = re.compile(r'^\((?P<paramtype>[A-z,]+)\)(:[ ])?')
	match = type_regex.search(desc)
	if match:
		return match.group('paramtype'), type_regex.sub('', desc)
	return '', desc


def _parse_parameter(param):
	paramname = param.find('name').text
	paramdesc = _format_description(param.find('desc'))
	paramtype, paramdesc = _pop_param_type(paramdesc)  # must be called after formatting the description
	return {
		'name': paramname,
		'description': paramdesc,
		'type': paramtype,
	}


def _get_params(func):
	"""
	params do not have to be declared, they can be parsed as well. If no params
	are declared, get any parsed params.
	"""
	paramlist = func.findall('parameterlist/parameter')
	if not paramlist:
		paramlist = func.findall('parsedparameterlist/parsedparameter')
		for param in paramlist:
			param.find('name').text = param.find('type').text
			desc = SubElement(param, 'desc')
			p = SubElement(desc, 'p')
			p.text = ''
	return paramlist


def _get_return(func):
	result = func.find('result')
	if result is None:
		return_type, return_desc = '', ''
	else:
		return_desc = _format_description(func.find('result'))
		return_type, return_desc = _pop_param_type(return_desc)
	return {
		'type': return_type,
		'description': return_desc,
	}


def _parse_function(func):
	funcname = func.find('name').text
	funcdesc = func.find('desc')
	examples, funcdesc = _pop_examples(funcdesc)
	funcdesc = _format_description(funcdesc)
	paramlist = _get_params(func)
	params = [_parse_parameter(p) for p in paramlist]
	return_value = _get_return(func)
	return {
		'name': funcname,
		'description': funcdesc,
		'params': params,
		'examples': examples,
		'return': return_value
	}


def _parse_class(cls):
	class_name = cls.find('name').text
	class_desc = _format_description(cls.find('desc'))
	methods = [_parse_function(f) for f in cls.find('functions')]
	return {
		'name': class_name,
		'description': class_desc,
		'methods': methods,
	}


def _parse_global(g):
	name = g.find('name').text
	desc = _format_description(g.find('desc'))
	value = g.find('value').text
	return {
		'name': name,
		'description': desc,
		'value': value
	}


def _parse_element_list(parent, identifier, parse_function):
	element_list = parent.find(identifier)
	if element_list is None:
		return []
	return [parse_function(e) for e in element_list]


def _parse_script(xml):
	script_name = xml.find('name').text
	desc = xml.find('desc')
	global_vars = _parse_element_list(xml, 'globals', _parse_global)
	funclist = _parse_element_list(xml, 'functions', _parse_function)
	classlist = _parse_element_list(xml, 'classes', _parse_script)
	return {
		'name': script_name,
		'description': _format_description(desc),
		'functions': funclist,
		'classes': classlist,
		'globals': global_vars
	}


def parse(xml):
	"""
	Parse headerdoc XML into a dictionary format.

	Extract classes, functions, and global variables from the given XML output
	by headerdoc. Some formatting and text manipulation takes place while
	parsing. For example, the `@example` is no longer recognized by headerdoc.
	`parse()` will extract examples separately from the given description.

	[Admonitions](https://python-markdown.github.io/extensions/admonition/)
	are also not kept in the correct format by headerdoc. Admonitions text must
	be indented to the same level as the admonition title, but headerdoc strips
	leading whitespace. The dictionary returned from `parse` will have the
	correct indentation restored.

	Args:
		xml (ElementTree): An `ElementTree` read from a headerdoc XML file. The
			root must be the `<header>` element.
	Returns:
		Dict
	"""
	return _parse_script(xml)
