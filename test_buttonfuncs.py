#!/usr/bin/env python3
"""Tests for anmad_buttons module."""

import logging
import os
import unittest
import werkzeug

import __main__ as main

import anmad_buttonfuncs
import anmad_queues

class TestButtonFuncs(unittest.TestCase):
    """Tests for anmad_buttons module."""

    def setUp(self):
        self.playbooks = ['deploy.yaml', 'deploy2.yaml']
        self.pre_run_playbooks = ['deploy4.yaml']
        self.playbookroot = 'samples'
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        # Change logging.ERROR to INFO, to see log messages during testing.
        self.logger.setLevel(logging.CRITICAL)
        self.testextras = ['deploy3.yaml']
        for num in range(5, 9):
            dnum = [('deploy' + str(num) + '.yaml')]
            self.testextras.extend(dnum)
        self.testextras.extend(['deploy9.yml'])
        self.queues = anmad_queues.AnmadQueues(
            'test_prerun', 'test_playbooks', 'test_info')

    def tearDown(self):
        self.playbooks = None
        self.pre_run_playbooks = None
        self.playbookroot = None
        self.testextras = None
        self.queues.clear()
        self.queues.clearinfo()

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
        self.assertEqual(
            buttons, ['deploy4.yaml', 'deploy.yaml', 'deploy2.yaml'])

    def test_nopre_extraplays(self):
        """Test extraplays behavior without prerun.
        adds pre_run_playbooks to expected list of extras for this test."""
        self.testextras.extend(self.pre_run_playbooks)
        self.testextras.sort()
        extraplaybooks = anmad_buttonfuncs.extraplays(
            self.logger, self.playbookroot, self.playbooks)
        self.assertEqual(extraplaybooks, self.testextras)

    def test_pre_extraplays(self):
        """Test extraplays behavior with prerun."""
        extraplaybooks = anmad_buttonfuncs.extraplays(
            self.logger,
            self.playbookroot,
            self.playbooks,
            self.pre_run_playbooks)
        self.assertEqual(extraplaybooks, self.testextras)

    def test_oneplaybook(self):
        """Test oneplaybook func to queue one play."""
        playbook = 'deploy.yaml'
        anmad_buttonfuncs.oneplaybook(
            self.logger,
            self.queues,
            playbook,
            self.playbooks,
            self.playbookroot)
        self.queues.update_job_lists()
        self.assertTrue([('samples/' + playbook)] in self.queues.queue_list)

    def test_one_badplaybook(self):
        """Test that requests are denied to add playbooks not in list."""
        playbook = 'badstuff.yaml'
        with self.assertRaises(werkzeug.exceptions.NotFound):
            anmad_buttonfuncs.oneplaybook(
                self.logger,
                self.queues,
                playbook,
                self.playbooks,
                self.playbookroot)
        self.queues.update_job_lists()
        self.assertFalse([('samples/' + playbook)] in self.queues.queue_list)


if __name__ == '__main__':
    unittest.main()
