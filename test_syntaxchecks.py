#!/usr/bin/env python3
"""Tests for anmad_syntaxchecks module."""

import logging
import os
import unittest

import __main__ as main

import anmad_syntaxchecks

class TestSyntaxCheck(unittest.TestCase):
    """Tests for anmad_version module."""


    def setUp(self):
        """Set up syntax check tests."""
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        self.testplay = 'samples/deploy.yaml'
        self.testinv = 'samples/inventory-internal'
        self.ansible_playbook_cmd = './venv/bin/ansible-playbook'

    def test_syntax_check_play_inv(self):
        """Tests for syntaxcheck_play_inv."""
        output = anmad_syntaxchecks.syntax_check_play_inv(
            self.logger,
            self.testplay,
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertEqual(output, '')


if __name__ == '__main__':
    unittest.main()
