# #!/usr/bin/env python3
from pathlib import Path

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
