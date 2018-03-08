# #!/usr/bin/env python3
from pathlib import Path
import shutil

import pytest

from asdocs import cli

TEST_PATH = Path(__file__).parent


@pytest.mark.integration
class TestDocumentGeneration:
	def test_GenerateHeaderdocXml_GivenDocumentedFiles_GeneratesDocumentation(self, tmpdir):
		source_files_path = TEST_PATH / 'data' / 'source_files'
		cli.generate_headerdoc_xml(cli.HEADERDOC, source_files_path, tmpdir)
		xml_files = list(tmpdir.visit(fil='*.xml'))
		assert len(xml_files) == 3

	def test_CollectHeaderdocOutput_GivenDirectory_CollectsXMLFiles(self):
		xml_files_path = TEST_PATH / 'data'
		xml_files = cli.collect_headerdoc_output(xml_files_path)
		assert len(xml_files) == 1

	def test_Main_GivenDocumentedFiles_GeneratesDocumentation(self, tmpdir):
		source_files_path = TEST_PATH / 'data' / 'source_files'
		tmpdir = Path(tmpdir)
		tmp_source = tmpdir / source_files_path.stem
		shutil.copytree(source_files_path, tmp_source)
		rendered = cli._main(tmp_source, tmp_source / 'docs')
		assert len(rendered) == 3
		filenames = [fp.name for fp, _ in rendered]
		expected_names = ['functools.md', 'list.md', 'string.md']
		assert all(name in filenames for name in expected_names)


class TestFiltering:
	@pytest.fixture
	def parsed_documentation(self):
		return [
			{
				'name': 'list.applescript',
				'description': 'A Description',
				'functions': [
					{'func1': None},
					{'func2': None},
				],
				'classes': [],
				'globals': [],
			},
			{
				'name': 'functools.applescript',
				'description': 'A Description',
				'functions': [
					{'func1': None},
					{'func2': None},
				],
				'classes': [
					{'class1': None}
				],
				'globals': [],
			},
			{
				'name': 'string.applescript',
				'description': 'A Description',
				'functions': [
					{'func1': None},
					{'func2': None},
				],
				'classes': [],
				'globals': [
					{'global1': None}
				]
			},
			{
				'name': 'undefined',
				'description': '',
				'functions': [],
				'classes': [],
				'globals': []
			}
		]

	def test_FilterDocumented_AllDocumented_ReturnsAll(self, parsed_documentation):
		documented = parsed_documentation[:3]
		filtered = cli.filter_documented(documented)
		assert len(documented) == 3
		assert len(filtered) == 3

	def test_FilterDocumented_PartialDocumentation_ReturnsDocumented(self, parsed_documentation):
		filtered = cli.filter_documented(parsed_documentation)
		assert len(parsed_documentation) == 4
		assert len(filtered) == 3

	def test_FilterDocumented_OnlyDescriptionDefined_ReturnsDocumented(self, parsed_documentation):
		documented = parsed_documentation[:1]
		documented[0]['functions'] = []
		filtered = cli.filter_documented(documented)
		assert len(filtered) == 1

	def test_FilterDocumented_OnlyFunctionsDefined_ReturnsDocumented(self, parsed_documentation):
		documented = parsed_documentation[:1]
		documented[0]['description'] = ''
		filtered = cli.filter_documented(documented)
		assert len(filtered) == 1

	def test_FilterDocumented_OnlyClassesDefined_ReturnsDocumented(self, parsed_documentation):
		documented = parsed_documentation[1:2]
		documented[0]['description'] = ''
		documented[0]['functions'] = []
		filtered = cli.filter_documented(documented)
		assert len(filtered) == 1

	def test_FilterDocumented_OnlyGlobalsDefined_ReturnsDocumented(self, parsed_documentation):
		documented = parsed_documentation[2:3]
		documented[0]['description'] = ''
		documented[0]['functions'] = []
		filtered = cli.filter_documented(documented)
		assert len(filtered) == 1


def test_GetRenderedFilePath_GivenFileName_ReturnsFilePath():
	output_dir = Path('/a/directory')
	filename = 'list.applescript'
	docpath = cli.get_rendered_file_path(output_dir, filename)
	assert str(docpath) == '/a/directory/list.md'
