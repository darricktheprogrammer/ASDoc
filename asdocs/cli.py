#!/usr/bin/env python3
"""
Command line entry point into ASDocs.

More details...
"""
from argparse import ArgumentParser


def main(args=None):
	pass


if __name__ == "__main__":
	parser = ArgumentParser(description=__doc__)
	parser.add_argument('-s', '--string',
						type=str,
						required=True,
						help='a required argument represented as a string.')
	parser.add_argument('-i', '--int',
						type=int,
						required=False,
						help='an optional argument represented as an integer.')
	parser.add_argument('-l', '--list',
						nargs='*',
						action='append',
						help='a list argument that takes more than one value.'
						' it can be called with spaces between each value.'
						' `*` allows an empty value. Change to `+` to make'
						' it required.')
	parser.add_argument('-b', '--bool',
						action='store_true',
						default=False,
						help='a boolean flag.')
	main(parser.parse_args())
