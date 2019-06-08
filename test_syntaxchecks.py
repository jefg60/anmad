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
        # Change logging.ERROR to INFO, to see log messages during testing.
        self.logger.setLevel(logging.CRITICAL)
        self.testplay = 'samples/deploy.yaml'
        self.badplay = 'samples/deploy3.yaml'
        self.testinv = 'samples/inventory-internal'
        self.ansible_playbook_cmd = './venv/bin/ansible-playbook'
        self.vaultpw = './vaultpassword'
        self.checkdir = './samples'
        self.syncheckobj = anmad_syntaxchecks.ansibleSyntaxCheck(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd,
            self.vaultpw)
        self.syncheckobj_multi_inv = anmad_syntaxchecks.ansibleSyntaxCheck(
            self.logger,
            [self.testinv, self.testinv],
            self.ansible_playbook_cmd,
            self.vaultpw)

    def test_one_play_many_inv(self):
        """Test syntax_check_one_play_many_inv func with single inv
        and multi inv."""
        output = self.syncheckobj.syntax_check_one_play_many_inv(
            self.testplay)
        self.assertEqual(output, 0)
        output = self.syncheckobj_multi_inv.syntax_check_one_play_many_inv(
            self.testplay)
        self.assertEqual(output, 0)

    def test_checkplaybooks(self):
        """Test that checkplaybooks func returns 0 when everything passed,
        and not 0 if there is a bad playbook or inventory."""
        output = self.syncheckobj.checkplaybooks(self.testplay)
        self.assertEqual(output, 0)
        output = self.syncheckobj.checkplaybooks(
            [self.testplay, self.testplay])
        self.assertEqual(output, 0)
        output = self.syncheckobj.checkplaybooks(
            [self.testplay, self.badplay])
        self.assertNotEqual(output, 0)
        output = self.syncheckobj.checkplaybooks(
            self.badplay)
        self.assertNotEqual(output, 0)

    def test_syncheck_dir(self):
        """Test syncheck_dir func against samples/. should return 2
        because there are 2 bad playbooks in there, or 255 for missing dir."""
        output = self.syncheckobj.syncheck_dir(self.checkdir)
        self.assertEqual(output, 2)
        output = self.syncheckobj.syncheck_dir('asdkjagdkjasgd')
        self.assertEqual(output, 255)

    def test_runplaybooks(self):
        """Test that runplaybooks func returns correct num of failed playbooks
        in testing."""
        output = self.syncheckobj.runplaybooks(self.testplay)
        self.assertEqual(output, 1)
        output = self.syncheckobj.runplaybooks(
            [self.testplay, self.testplay])
        self.assertEqual(output, 2)

if __name__ == '__main__':
    unittest.main()
