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

from asdocs import lib


log = logging.getLogger(__name__)


_package_dir = Path(__file__).parent
HEADERDOC = _package_dir / 'vendor' / 'headerdoc-8.9.28' / 'headerDoc2HTML.pl'
DEFAULT_TEMPLATE = _package_dir / 'templates' / 'default.md'
RELATIVE_OUTPUT_DIR = 'api-reference'
DEFAULT_RELATIVE_DOCS_DIR = 'docs'


def get_args():
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
	return args


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


def main():
	_set_logging()
	args = get_args()
	if not args.filepath.is_dir():
		raise TypeError(f"filepath '{args.filepath}' is not a directory.")
	with tempfile.TemporaryDirectory() as headerdoc_out_dir:
		generate_headerdoc_xml(HEADERDOC, args.filepath, headerdoc_out_dir)
		output = collect_headerdoc_output(headerdoc_out_dir)
		parsed_files = [lib.parse_file(f) for f in output]
	documentation = filter_documented(parsed_files)
	generated_docs_dir = Path(args.docs_dir) / RELATIVE_OUTPUT_DIR
	generated_docs_dir.mkdir(parents=True, exist_ok=True)
	for d in documentation:
		docpath = generated_docs_dir / d['name'].replace('applescript', 'md')
		markdown = render_template(d, DEFAULT_TEMPLATE)
		# Jinja2 won't accept a PosixPath class as an argument. The Path must
		# be converted to its string representation before attempting to write.
		markdown.dump(str(docpath))


if __name__ == "__main__":
	main()
