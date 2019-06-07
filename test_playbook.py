#!/usr/bin/env python3
"""Tests for anmad_playbook module."""

import logging
import os
import unittest

import __main__ as main

import anmad_playbook

class TestPlaybook(unittest.TestCase):
    """Tests for anmad_playbook module."""


    def setUp(self):
        """Set up playbook tests."""
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        self.logger.setLevel(logging.ERROR)
        self.testplay = 'samples/deploy.yaml'
        self.badplay = 'samples/deploy3.yaml'
        self.testinv = 'samples/inventory-internal'
        self.ansible_playbook_cmd = './venv/bin/ansible-playbook'
        self.vaultpw = './vaultpassword'

    def test_ansible_playbook_novault_nosyn(self):
        playbookobject = anmad_playbook.ansibleRun(
            self.logger,
            self.testinv,
            self.ansible_playbook_cmd)
        self.assertEqual(playbookobject.run_playbook(self.testplay), 4)


if __name__ == '__main__':
    unittest.main()

