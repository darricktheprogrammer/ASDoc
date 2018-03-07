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

from asdocs import lib

log = logging.getLogger(__name__)


def get_args():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("filepath",
						type=str,
						help='The absolute path to a directory containing'
						' applescript files to be documented.')
	parser.add_argument("--docs_dir",
						type=str,
						default='docs',
						help='The absolute path to a directory containing'
						' project documentation. This doubles as the MkDocs'
						' top level directory. Default is `{filepath}/docs`.')
	args = parser.parse_args()
	args.filepath = Path(args.filepath)
	if args.docs_dir == 'docs':
		args.docs_dir = args.filepath / 'docs'
	return args


def generate_headerdoc_xml(headerDoc2HTML, input_dir, output_dir):
	applescript_files = [f for f in input_dir.glob('**/*.applescript')]
	command = [
		'perl', headerDoc2HTML,
		'--xml-output',
		'--quiet',
		'--output-directory', output_dir,
		*applescript_files]
	log.info(f'running command: {command}')
	subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def collect_headerdoc_output(top_level):
	all_xml_files = list(Path(top_level).glob('**/*.xml'))
	log.debug(f'found {len(all_xml_files)} headerdoc files')
	return all_xml_files


def filter_documented(parsed_files):
	documented_files = [
		f for f in parsed_files
		if f['description']
		or f['functions']
		or f['classes']
		or f['globals']
		]
	log.debug(f'found {len(documented_files)} documented files')
	return documented_files


def main():
	logging.basicConfig(
		stream=sys.stdout,
		format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
		datefmt='%Y-%m-%d %I:%M:%S',
		level=logging.DEBUG
		)
	args = get_args()
	if not args.filepath.is_dir():
		raise TypeError(f"filepath '{args.filepath}' is not a directory.")
	headerdoc_dir = Path(__file__).parents[1] / 'vendor' / 'headerdoc-8.9.28'
	headerDoc2HTML = headerdoc_dir / 'headerDoc2HTML.pl'
	with tempfile.TemporaryDirectory() as headerdoc_out_dir:
		generate_headerdoc_xml(headerDoc2HTML, args.filepath, headerdoc_out_dir)
		output = collect_headerdoc_output(headerdoc_out_dir)
		parsed_files = [lib.parse_file(f) for f in output]
		documentation = filter_documented(parsed_files)


if __name__ == "__main__":
	main()
