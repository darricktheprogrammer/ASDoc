#!/usr/bin/env python3
import pytest


from asdocs import asdocs


def test_asdocs_Given_Returns():
	assert asdocs.function() == value


@pytest.mark.integration
def test_asdocs_Given_Returns():
	"""integration test"""
	assert asdocs.function() == value


class TestAsdocs():


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_something(self):
        pass
