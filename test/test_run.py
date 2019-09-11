#!/usr/bin/env python3
"""Tests for anmad.run module."""

import logging
import os
import unittest
import subprocess

import __main__ as main

import anmad.run

class TestPlaybook(unittest.TestCase):
    """Tests for anmad.run module."""


    def setUp(self):
        """Set up playbook tests."""
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        self.logger.setLevel(logging.CRITICAL)
        self.testplay = '/vagrant/samples/deploy.yaml'
        self.timedplay = '/vagrant/samples/deploy2.yaml'
        self.badplay = '/vagrant/samples/deploy3.yaml'
        self.testinv = '/vagrant/samples/inventory-internal'
        self.ansible_playbook_cmd = '/home/vagrant/venv/bin/ansible-playbook'
        self.vaultpw = '/vagrant/test/vaultpassword'
        self.timeout = 2
        self.playbookobject = anmad.run.AnmadRun(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd)

    def test_ansible_playbook_novault_syn(self):
        """Test run_playbook with no vault and syntax check."""
        returned = self.playbookobject.run_playbook(
            self.testplay, syncheck=True)
        self.assertEqual(returned.returncode, 0)

    def test_ansible_playbook_novault_nosyn(self):
        """Test run_playbook with no vault and no syntax check."""
        returned = self.playbookobject.run_playbook(self.testplay)
        self.assertEqual(returned.returncode, 4)
        returned = self.playbookobject.run_playbook(
            self.testplay, syncheck=False)
        self.assertEqual(returned.returncode, 4)

    def test_ansible_playbook_novault_nosyn_check(self):
        """Test run_playbook with no vault,  no syntax check,
        plus --check --diff mode."""
        returned = self.playbookobject.run_playbook(
            self.testplay, checkmode=True)
        self.assertEqual(returned.returncode, 4)

    def test_ansible_playbook_vault_syn(self):
        """Test run_playbook with vault."""
        playbookobject = anmad.run.AnmadRun(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd,
            self.vaultpw)
        returned = playbookobject.run_playbook(self.testplay, syncheck=True)
        self.assertEqual(returned.returncode, 0)

    def test_syncheck_playbook(self):
        """Test syncheck_playbook method."""
        returned = self.playbookobject.syncheck_playbook(
            self.testplay)
        self.assertEqual(returned.returncode, 0)
        returned = self.playbookobject.syncheck_playbook(
            self.badplay)
        self.assertEqual(returned.returncode, 4)

    def test_ansible_playbook_timeout(self):
        """Test run_playbook with timeout. must set vault_password_file
        if also setting timeout"""
        playbookobject = anmad.run.AnmadRun(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd,
            self.vaultpw,
            self.timeout)
        returned = playbookobject.run_playbook(self.timedplay)
        self.assertEqual(returned.returncode, 255)
        returned = playbookobject.run_playbook(self.timedplay, syncheck = True)
        self.assertEqual(returned.returncode, 0)


if __name__ == '__main__':
    unittest.main()
