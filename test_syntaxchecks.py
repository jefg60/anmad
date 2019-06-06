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
        self.logger.setLevel(logging.ERROR)
        self.testplay = 'samples/deploy.yaml'
        self.badplay = 'samples/deploy3.yaml'
        self.testinv = 'samples/inventory-internal'
        self.ansible_playbook_cmd = './venv/bin/ansible-playbook'
        self.vaultpw = './vaultpassword'

    def run_syn_check_play_inv(self, play, vaultpw=None):
        if vaultpw is not None:
            output = anmad_syntaxchecks.syntax_check_play_inv(
                self.logger,
                play,
                self.testinv,
                self.ansible_playbook_cmd,
                vaultpw)
        else:
            output = anmad_syntaxchecks.syntax_check_play_inv(
                self.logger,
                play,
                self.testinv,
                self.ansible_playbook_cmd)
        return output

    def test_play_inv(self):
        """Tests for syntaxcheck_play_inv."""
        output = self.run_syn_check_play_inv(self.testplay)
        self.assertEqual(output, 0)

    def test_play_inv_badplay(self):
        """Tests for syntaxcheck_play_inv with a bad playbook."""
        output = self.run_syn_check_play_inv(self.badplay)
        self.assertNotEqual(output, 0)

    def test_play_inv_vaultpw(self):
        """Tests for syntaxcheck_play_inv with vaultpw arg."""
        output = self.run_syn_check_play_inv(self.testplay, self.vaultpw)
        self.assertEqual(output, 0)

    def test_one_play_many_inv(self):
        """Test syntax_check_one_play_many_inv func with single inv
        and multi inv."""
        output = anmad_syntaxchecks.syntax_check_one_play_many_inv(
            self.logger,
            self.testplay,
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertEqual(output, 0)
        output = anmad_syntaxchecks.syntax_check_one_play_many_inv(
            self.logger,
            self.testplay,
            [self.testinv, self.testinv],
            self.ansible_playbook_cmd)
        self.assertEqual(output, 0)

    def test_checkplaybooks(self):
        """Test that checkplaybooks func returns 0 when everything passed,
        and not 0 if there is a bad playbook or inventory."""
        output = anmad_syntaxchecks.checkplaybooks(
            self.logger,
            self.testplay,
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertEqual(output, 0)
        output = anmad_syntaxchecks.checkplaybooks(
            self.logger,
            [self.testplay, self.testplay],
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertEqual(output, 0)
        output = anmad_syntaxchecks.checkplaybooks(
            self.logger,
            [self.testplay, self.badplay],
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertNotEqual(output, 0)
        output = anmad_syntaxchecks.checkplaybooks(
            self.logger,
            self.badplay,
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertNotEqual(output, 0)


if __name__ == '__main__':
    unittest.main()
