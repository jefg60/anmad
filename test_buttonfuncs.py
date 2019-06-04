#!/usr/bin/env python3
"""Tests for anmad_buttons module."""

import logging
import os
import unittest

import __main__ as main

import anmad_buttonfuncs

class TestVersion(unittest.TestCase):
    """Tests for anmad_buttons module."""

    def setUp(self):
        self.playbooks = ['deploy.yaml', 'deploy2.yaml']
        self.pre_run_playbooks = ['deploy4.yaml']
        self.playbookroot = 'samples'
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        self.testextras = ['deploy3.yaml']
        for x in range(5, 9):
            dx = [('deploy' + str(x) + '.yaml')]
            self.testextras.extend(dx)
        self.testextras.extend(['deploy9.yml'])

    def test_noarg_buttonlist(self):
        """Test buttonlist behavior without args."""
        with self.assertRaises(TypeError):
            anmad_buttonfuncs.buttonlist()

    def test_nopre_buttonlist(self):
        """Test buttonlist without prerun."""
        buttons = anmad_buttonfuncs.buttonlist(self.playbooks)
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons, ['deploy.yaml', 'deploy2.yaml'])

    def test_prerun_buttonlist(self):
        """Test buttonlist with prerun."""
        buttons = anmad_buttonfuncs.buttonlist(
            self.playbooks, self.pre_run_playbooks)
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 3)
        self.assertEqual(buttons, ['deploy4.yaml', 'deploy.yaml', 'deploy2.yaml'])

    def test_noarg_extraplays(self):
        """Test extraplays behavior without args."""
        with self.assertRaises(TypeError):
            anmad_buttonfuncs.extraplays()

    def test_nopre_extraplays(self):
        """Test extraplays behavior without prerun.
        adds pre_run_playbooks to expected list of extras for this test."""
        self.testextras.extend(self.pre_run_playbooks)
        self.testextras.sort()
        extraplaybooks = anmad_buttonfuncs.extraplays(
            self.logger, self.playbookroot, self.playbooks)
        self.assertEqual(extraplaybooks, self.testextras)

if __name__ == '__main__':
    unittest.main()
