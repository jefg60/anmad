#!/usr/bin/env python3
"""Tests for anmad.multi module."""

import logging
import os
import subprocess
import unittest

import __main__ as main

import anmad.multi

class TestMulti(unittest.TestCase):
    """Tests for anmad.multi module."""
    # pylint: disable=too-many-instance-attributes


    def setUp(self):
        """Set up multi arg tests."""
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        # Change logging.ERROR to INFO, to see log messages during testing.
        self.logger.setLevel(logging.CRITICAL)
        self.testplay = 'samples/deploy.yaml'
        self.timedplay = 'samples/deploy6.yaml'
        self.timeout = 2
        self.badplay = 'samples/deploy3.yaml'
        self.testinv = 'samples/inventory-internal'
        self.ansible_playbook_cmd = './venv/bin/ansible-playbook'
        self.vaultpw = 'test/vaultpassword'
        self.checkdir = './samples'
        self.multiobj = anmad.multi.AnmadMulti(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd,
            self.vaultpw)
        self.multimultiobj = anmad.multi.AnmadMulti(
            self.logger,
            [self.testinv, self.testinv],
            self.ansible_playbook_cmd,
            self.vaultpw)

    def test_one_play_many_inv(self):
        """Test syntax_check_one_play_many_inv func with single inv
        and multi inv."""
        output = self.multiobj.syntax_check_one_play_many_inv(
            self.testplay)
        self.assertEqual(output, 0)
        output = self.multimultiobj.syntax_check_one_play_many_inv(
            self.testplay)
        self.assertEqual(output, 0)

    def test_checkplaybooks(self):
        """Test that checkplaybooks func returns 0 when everything passed,
        and not 0 if there is a bad playbook or inventory."""
        output = self.multiobj.checkplaybooks(self.testplay)
        self.assertEqual(output, 0)
        output = self.multiobj.checkplaybooks(
            [self.testplay, self.testplay])
        self.assertEqual(output, 0)
        output = self.multiobj.checkplaybooks(
            [self.testplay, self.badplay])
        self.assertNotEqual(output, 0)
        output = self.multimultiobj.checkplaybooks(
            self.badplay)
        self.assertNotEqual(output, 0)

    def test_syncheck_dir(self):
        """Test syncheck_dir func against samples/. should return 2
        because there are 2 bad playbooks in there, or 255 for missing dir."""
        output = self.multiobj.syncheck_dir(self.checkdir)
        self.assertEqual(output, 2)
        output = self.multiobj.syncheck_dir('asdkjagdkjasgd')
        self.assertEqual(output, 255)

    def test_runplaybooks(self):
        """Test that runplaybooks func returns correct num of failed playbooks
        in testing. note that timedplay should WORK unless timeout <=2
        because it runs against localhost, unlike the other plays"""
        timedmultiobj = anmad.multi.AnmadMulti(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd,
            self.vaultpw,
            self.timeout)
        output = timedmultiobj.runplaybooks(self.timedplay)
        self.assertEqual(output, 1)

        output = self.multiobj.runplaybooks(self.timedplay)
        self.assertEqual(output, 0)

        output = self.multimultiobj.runplaybooks(self.timedplay)
        self.assertEqual(output, 0)

        output = self.multimultiobj.runplaybooks(self.testplay)
        self.assertEqual(output, 1)

        output = self.multiobj.runplaybooks(
            [self.testplay, self.testplay])
        self.assertEqual(output, 2)

        output = self.multiobj.runplaybooks(
            [self.testplay, self.timedplay])
        self.assertEqual(output, 1)

if __name__ == '__main__':
    unittest.main()
