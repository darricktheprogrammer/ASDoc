#!/usr/bin/env python3
"""
Command line entry point into ASDocs.

More details...
"""
import logging
import sys
import tempfile
import subprocess
from pathlib import Path
from argparse import ArgumentParser

import jinja2
import yaml

from asdocs import lib


log = logging.getLogger(__name__)


_package_dir = Path(__file__).parent
HEADERDOC = _package_dir / 'vendor' / 'headerdoc-8.9.28' / 'headerDoc2HTML.pl'
DEFAULT_TEMPLATE = _package_dir / 'templates' / 'default.md'
RELATIVE_OUTPUT_DIR = 'api-reference'
RELATIVE_MKDOCS_CONFIG_PATH = 'mkdocs.yml'
DEFAULT_RELATIVE_DOCS_DIR = 'docs'


def generate_headerdoc_xml(headerDoc2HTML, input_dir, output_dir):
	applescript_files = [f for f in input_dir.glob('**/*.applescript')]
	command = [
		'perl', headerDoc2HTML,
		'--xml-output',
		'--quiet',
		'--output-directory', output_dir,
		*applescript_files]
	log.debug(f'running command: {command}')
	subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def collect_headerdoc_output(top_level):
	all_xml_files = list(Path(top_level).glob('**/*.xml'))
	log.info(f'found {len(all_xml_files)} headerdoc files')
	return all_xml_files


def filter_documented(parsed_files):
	"""
	Remove files that aren't documented.

	Headerdoc will create XML files for all applescript files found in the
	directory, whether they are documented or not. Remove anything that has
	no data in the XML.

	This still allows for the most basic of documentation, since as long as
	either the file is documented at the file level, or headerdoc finds any
	functions, classes, or globals documented, then the file will still be
	included in ASDoc's output.
	"""
	documented_files = [
		f for f in parsed_files
		if f['description']
		or f['functions']
		or f['classes']
		or f['globals']
		]
	log.info(f'found {len(documented_files)} documented files')
	return documented_files


def render_template(documentation, template_file):
	with open(template_file, 'r') as f:
		template_text = f.read()
	# Jinja2 templates are hard to read without nesting, but Jinja retains
	# whitespace. Strip all leading whitespace so that the template can use
	# nesting.
	#
	# This means that things such as nested lists and indented code cannot
	# be used. Only fenced code blocks and single level lists are available.
	stripped_lines = [line.lstrip() for line in template_text.splitlines()]
	template_text = '\n'.join(stripped_lines)
	env = jinja2.Environment(
		loader=jinja2.BaseLoader(),
		trim_blocks=True,
		)
	template = env.from_string(template_text)
	return template.stream(documentation)


def _set_logging():
	logging.basicConfig(
		stream=sys.stdout,
		format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
		datefmt='%Y-%m-%d %I:%M:%S',
		level=logging.INFO
		)


def make_output_dir(parentdir, relative_dir):
	output_dir = Path(parentdir) / relative_dir
	output_dir.mkdir(parents=True, exist_ok=True)
	return output_dir


def get_rendered_file_path(output_dir, file_name):
	return output_dir / file_name.replace('applescript', 'md')


def _load_mkdocs_config(config_path):
	with open(config_path, 'r') as config_file:
		config = yaml.load(config_file)
	return config


def update_mkdocs_config_with_api_pages(config, modules, docs_dir):
	def _get_dict_from_list_by_key(ls, key):
		for item in ls:
			if key in item.keys():
				return item[key]
		raise AttributeError(f"No item with key '{key}' in {ls}")

	def _strip_absolute_path(pth, absolute_path):
		leading_path = f'{absolute_path}/'
		return str(pth).replace(leading_path, '')

	config_pages = config.setdefault('pages', [])
	try:
		api_reference = _get_dict_from_list_by_key(config_pages, 'API Reference')
	except AttributeError:
		config['pages'].append({'API Reference': []})
		api_reference = config['pages'][-1]['API Reference']
	for module in modules:
		relative_path = _strip_absolute_path(module['path'], docs_dir)
		api_reference.append({module['name']: relative_path})
	return config


def _main(filepath, docs_dir):
	if not filepath.is_dir():
		raise TypeError(f"filepath '{filepath}' is not a directory.")
	with tempfile.TemporaryDirectory() as headerdoc_out_dir:
		generate_headerdoc_xml(HEADERDOC, filepath, headerdoc_out_dir)
		xml_files = collect_headerdoc_output(headerdoc_out_dir)
		parsed = [lib.parse_file(f) for f in xml_files]
	documentation = filter_documented(parsed)
	output_dir = make_output_dir(docs_dir, RELATIVE_OUTPUT_DIR)
	for module in documentation:
		docpath = get_rendered_file_path(output_dir, module['name'])
		markdown = render_template(module, DEFAULT_TEMPLATE)
		# Jinja2 won't accept a PosixPath class as an argument. The Path must
		# be converted to its string representation before attempting to write.
		markdown.dump(str(docpath))
		module['rendered_text'] = markdown
		module['path'] = docpath
	mkdocs_config = _load_mkdocs_config(filepath / RELATIVE_MKDOCS_CONFIG_PATH)
	update_mkdocs_config_with_api_pages(mkdocs_config, documentation, docs_dir)
	return documentation


def main():
	_set_logging()
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("filepath",
						type=str,
						help='The absolute path to a directory containing'
						' applescript files to be documented.')
	parser.add_argument("--docs_dir",
						type=str,
						default=DEFAULT_RELATIVE_DOCS_DIR,
						help='The absolute path to a directory containing'
						' project documentation. This doubles as the MkDocs'
						' top level directory. Default is `{filepath}/docs`.')
	args = parser.parse_args()
	args.filepath = Path(args.filepath)
	if args.docs_dir == DEFAULT_RELATIVE_DOCS_DIR:
		args.docs_dir = args.filepath / DEFAULT_RELATIVE_DOCS_DIR
	return _main(args.filepath, args.docs_dir)


if __name__ == "__main__":
	main()
