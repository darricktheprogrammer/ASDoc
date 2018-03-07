#!/usr/bin/env python3
from xml.etree import ElementTree as et

import pytest

from asdocs import lib


def load_xml(xml_text):
	return et.fromstring(xml_text)


class TestParameterParsing:
	@pytest.fixture(scope='class')
	def single_parameter(self):
		return (
			'<parameter>\n'
			'   <name>value</name>\n'
			'   <desc>\n'
			'       {}\n'
			'   </desc>\n'
			'</parameter>'
			)

	def test_ParseParameter_GivenSingleParameter_ParsesParameter(self, single_parameter):
		param_text = single_parameter.format('<p>Item description</p>')
		param = lib._parse_parameter(load_xml(param_text))
		assert param['name'] == 'value'
		assert param['description'] == 'Item description'
		assert param['type'] == ''

	def test_ParseParameter_GivenTypeInDescription_ParsesType(self, single_parameter):
		param_text = single_parameter.format('<p>(String): Item description</p>')
		param = lib._parse_parameter(load_xml(param_text))
		assert param['description'] == 'Item description'
		assert param['type'] == 'String'

	def test_ParseParameter_GivenMultipleTypesWithoutSpace_ParsesTypes(self, single_parameter):
		param_text = single_parameter.format('<p>(String,Number): Item description</p>')
		param = lib._parse_parameter(load_xml(param_text))
		assert param['type'] == 'String,Number'

	def test_ParseParameter_GivenMultipleTypesWithSpace_ParsesTypes(self, single_parameter):
		param_text = single_parameter.format('<p>(String, Number): Item description</p>')
		param = lib._parse_parameter(load_xml(param_text))
		assert param['type'] == 'String, Number'

	def test_ParseParameter_GivenTypeWithoutDescription_ParsesType(self, single_parameter):
		# If there is no description you can forego the colon
		param_text = single_parameter.format('<p>(String)</p>')
		param = lib._parse_parameter(load_xml(param_text))
		assert param['description'] == ''
		assert param['type'] == 'String'


class TestDescriptionFormatting:
	def test_FormatDescription_GivenMultilineDescription_CondensesDescriptionToOneLine(self):
		# This is for the cases where documentation is wrapped at (most likely)
		# column 80. There should not actually be line breaks. For that, the
		# user should use paragraphs separated by two returns.
		description = (
			'<desc>\n'
			'    <p>first line\n'
			'second line</p>\n'
			'</desc>'
			)
		formatted = lib._format_description(load_xml(description))
		assert formatted == 'first line second line'

	def test_FormatDescription_GivenMultipleParagraphs_ReturnsSeparatedLines(self):
		description = (
			'<desc>\n'
			'    <p>first paragraph</p>\n'
			'    <p>second paragraph</p>\n'
			'</desc>'
			)
		formatted = lib._format_description(load_xml(description))
		assert formatted == 'first paragraph\n\nsecond paragraph'

	def test_FormatDescription_EmptyDescriptionParagraph_ReturnsEmptyString(self):
		description = (
			'<desc>\n'
			'    <p></p>\n'
			'</desc>'
			)
		formatted = lib._format_description(load_xml(description))
		assert formatted == ''

	def test_FormatDescription_NullParagraph_ReturnsEmptyString(self):
		description = (
			'<desc>\n'
			'    <p/>\n'
			'</desc>'
			)
		formatted = lib._format_description(load_xml(description))
		assert formatted == ''

	def test_FormatDescription_ParagraphWithTrailingLineEnding_TrimsLineEnding(self):
		description = (
			'<desc>\n'
			'    <p>A description\n'
			'</p>\n'
			'</desc>'
			)
		formatted = lib._format_description(load_xml(description))
		assert formatted == 'A description'

	def test_PopExamples_GivenSingleExample_ReturnsDescriptionAndExample(self):
		description = (
			'<desc>\n'
			'    <p>A Description</p>\n'
			'    <p>@example diff({"a", "b", "c", "d"}, {"a", "b", "e", "f"})\n'
			'--> {"c", "d"}\n'
			'</p>\n'
			'</desc>'
			)
		examples, desc = lib._pop_examples(load_xml(description))
		assert len(desc.findall('p')) == 1
		assert len(examples) == 1
		assert examples[0] == 'diff({"a", "b", "c", "d"}, {"a", "b", "e", "f"})\n--> {"c", "d"}'


class TestFunctionParsing:
	def test_GetParams_NoParameters_ReturnsEmptyList(self):
		function_xml = (
			'<function id="//apple_ref/applescript/func/join" lang="applescript">\n'
			'	<name>join</name>\n'
			'	<result>\n'
			'		<p>(String)</p>\n'
			'	</result>\n'
			'	<declaration>\n'
			'		<declaration_keyword>on</declaration_keyword>\n'
			'		<declaration_function>join</declaration_function>()\n'
			'	</declaration>\n'
			'	<desc>\n'
			'		<p>Convert a list to string, inserting a delimiter between each list item.</p>\n'
			'	</desc>\n'
			'</function>'
			)
		func = lib._parse_function(load_xml(function_xml))
		assert len(func['params']) == 0
		assert isinstance(func['params'], list)
