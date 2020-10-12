#!/usr/bin/env python3
"""Tests for anmad interface_backend module."""

import logging
import os
import unittest
import werkzeug

import __main__ as main

import anmad.interface_backend
import anmad.api_backend
import anmad.queues

from argparse import Namespace

class TestInterfaceBackend(unittest.TestCase):
    """Tests for anmad_buttons module."""
     # pylint: disable=duplicate-code

    def setUp(self):
        self.maxDiff = None
        if 'unittest.util' in __import__('sys').modules:
            # Show full diff in self.assertEqual.
            __import__('sys').modules['unittest.util']._MAX_LENGTH = 999999999

        self.args = Namespace(
            playbooks = ['deploy.yaml', 'deploy2.yaml'],
            pre_run_playbooks = ['deploy4.yaml'],
            playbook_root_dir = '/vagrant/samples'
        )
        self.config = {
            "args": self.args,
            "logger": logging.getLogger(os.path.basename(main.__file__)),
            "queues": anmad.queues.AnmadQueues(
                'test_prerun', 'test_playbooks', 'test_info'),
            "testextras": ['deploy3.yaml']
        }
        # Change logging.ERROR to INFO, to see log messages during testing.
        self.config["logger"].setLevel(logging.CRITICAL)
        for num in range(5, 9):
            dnum = [('deploy' + str(num) + '.yaml')]
            self.config["testextras"].extend(dnum)
        self.config["testextras"].extend(['deploy9.yml'])

    def tearDown(self):
        self.config["args"].playbooks = None
        self.config["args"].pre_run_playbooks = None
        self.config["args"].playbook_root_dir = None
        self.config["testextras"] = None
        self.config["queues"].clear()
        self.config["queues"].clearinfo()

    def test_nopre_buttonlist(self):
        """Test buttonlist without prerun."""
        buttons = anmad.interface_backend.buttonlist(self.config["args"].playbooks)
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons, ['deploy.yaml', 'deploy2.yaml'])

    def test_prerun_buttonlist(self):
        """Test buttonlist with prerun."""
        buttons = anmad.interface_backend.buttonlist(
            self.config["args"].playbooks, self.config["args"].pre_run_playbooks)
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 3)
        self.assertEqual(
            buttons, ['deploy4.yaml', 'deploy.yaml', 'deploy2.yaml'])

    def test_nopre_extraplays(self):
        """Test extraplays behavior without prerun.
        adds pre_run_playbooks to expected list of extras for this test."""
        self.config["testextras"].extend(self.config["args"].pre_run_playbooks)
        self.config["testextras"].sort()
        extraplaybooks = anmad.interface_backend.extraplays(**self.config)
        self.assertEqual(extraplaybooks, self.config["testextras"])

    def test_pre_extraplays(self):
        """Test extraplays behavior with prerun."""
        extraplaybooks = anmad.interface_backend.extraplays(prerun=True, **self.config)
        self.assertEqual(extraplaybooks, self.config["testextras"])

    def test_oneplaybook(self):
        """Test oneplaybook func to queue one play."""
        playbook = 'deploy.yaml'
        anmad.api_backend.oneplaybook(
            playbook,
            self.config["args"].playbooks,
            **self.config)
        self.config["queues"].update_job_lists()
        self.assertTrue([('/vagrant/samples/' + playbook)] in self.config["queues"].queue_list)

    def test_one_badplaybook(self):
        """Test that requests are denied to add playbooks not in list."""
        playbook = 'badstuff.yaml'
        with self.assertRaises(werkzeug.exceptions.NotFound):
            anmad.api_backend.oneplaybook(
                playbook,
                self.config["args"].playbooks,
                **self.config)
        self.config["queues"].update_job_lists()
        self.assertFalse([('/vagrant/samples/' + playbook)] in self.config["queues"].queue_list)


if __name__ == '__main__':
    unittest.main()
