#!/usr/bin/env python3
"""Tests for anmad_buttons module."""

import unittest
import anmad_buttonfuncs

class TestVersion(unittest.TestCase):
    """Tests for anmad_buttons module."""


    def test_1arg_buttonlist(self):
        """Test buttonlist with one list."""
        buttons = anmad_buttonfuncs.buttonlist(['play1.yml', 'play2.yaml'])
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons, ['play1.yml', 'play2.yaml'])

    def test_2arg_buttonlist(self):
        """Test buttonlist joins two lists."""
        buttons = anmad_buttonfuncs.buttonlist(['play1.yml', 'play2.yaml'], ['prerun1.yaml'])
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 3)
        self.assertEqual(buttons, ['prerun1.yaml', 'play1.yml', 'play2.yaml'])

    def test_noarg_buttonlist(self):
        """Test buttonlist behavior without args."""
        with self.assertRaises(TypeError):
            self.buttons = anmad_buttonfuncs.buttonlist()


if __name__ == '__main__':
    unittest.main()
