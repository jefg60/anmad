#!/usr/bin/env python3
"""Test http return codes."""

import unittest
import requests

import __main__ as main


class TestReturnCodes(unittest.TestCase):
    """Test http return codes."""

    def setUp(self):
        pass

    def test_ara_button(self):
        """Test the ara button."""
        output = requests.get("http://localhost:9999/")
        self.assertIn('/ara', output.text)


if __name__ == '__main__':
    unittest.main()
