#!/usr/bin/env python3
"""Tests for anmad_version module."""

import unittest
import anmad_version

class TestVersion(unittest.TestCase):
    """Tests for anmad_version module."""


    def test_version(self):
        """Tests for version constant."""
        version = anmad_version.VERSION
        self.assertIsNotNone(version)
        self.assertEqual(version, "0.14.4")


if __name__ == '__main__':
    unittest.main()
