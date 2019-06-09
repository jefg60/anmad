#!/usr/bin/env python3
"""Tests for anmad_buttons module."""

import logging
import os
import unittest
import werkzeug

import __main__ as main

import anmad_buttons
import anmad_queues
import anmad_args
import anmad_version

class TestButtonApp(unittest.TestCase):
    """Tests for anmad_buttons APP."""

    def setUp(self):
        self.playbooks = ['deploy.yaml', 'deploy2.yaml']
        self.pre_run_playbooks = ['deploy4.yaml']
        self.playbookroot = 'samples'
        self.version = anmad_version.VERSION
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
        self.app = anmad_buttons.APP.test_client()
        anmad_buttons.ARGS = {
            'ara_url': 'ara',
            'playbook_root_dir': self.playbookroot,
            'playbooks': self.playbooks,
            'pre_run_playbooks': self.pre_run_playbooks,
            'prerun_list': anmad_args.prepend_rootdir(
                self.playbookroot, self.pre_run_playbooks),
            'run_list': anmad_args.prepend_rootdir(
                self.playbookroot, self.playbooks)}
        anmad_buttons.LOGGER = self.logger
        anmad_buttons.QUEUES = self.queues


    def tearDown(self):
        self.playbooks = None
        self.pre_run_playbooks = None
        self.playbookroot = None
        self.testextras = None
        self.queues.clear()
        self.queues.clearinfo()

    def test_mainpage(self):
        """Test mainpage renders as expected."""
        response = self.app.get('/')
        self.assertEqual(response.status, '200 OK')
        self.assertIn(self.version, str(response.data))
        self.assertIn('Other Playbooks', str(response.data))
        self.assertIn('Queued Jobs', str(response.data))
        self.assertIn('More logs...', str(response.data))
        self.assertIn(self.pre_run_playbooks[0], str(response.data))
        self.assertIn(self.playbooks[1], str(response.data))

    def test_logpage(self):
        """Test log page."""
        response = self.app.get('/log')
        self.assertEqual(response.status, '200 OK')
        self.assertIn(self.version, str(response.data))
        self.assertIn("Back to main interface", str(response.data))
        self.assertIn("No messages found yet", str(response.data))

    def test_otherplays_page(self):
        """Test otherplays page."""
        response = self.app.get('/otherplays')
        self.assertEqual(response.status, '200 OK')
        self.assertIn(self.version, str(response.data))
        self.assertIn("deploy9.yml", str(response.data))

    def test_queues(self):
        """Test clearqueues button."""
        response = self.app.get('/runall')
        self.assertEqual(response.status, '302 FOUND')
        self.assertNotEqual(len(self.queues.queue_list), 0)
        self.assertNotEqual(len(self.queues.prequeue_list), 0)
        response = self.app.get('/clearqueues')
        self.assertEqual(response.status, '302 FOUND')
        self.assertEqual(len(self.queues.queue_list), 0)
        self.assertEqual(len(self.queues.prequeue_list), 0)


if __name__ == '__main__':
    unittest.main()
