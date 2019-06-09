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

class TestButtonApp(unittest.TestCase):
    """Tests for anmad_buttons APP."""

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
        self.app = anmad_buttons.APP.test_client()
        anmad_buttons.ARGS = {
            'ara_url': 'ara',
            'playbook_root_dir': self.playbookroot,
            'playbooks': self.playbooks,
            'pre_run_playbooks': self.pre_run_playbooks,
            'prerun_list': anmad_args.prepend_rootdir(self.playbookroot, self.pre_run_playbooks),
            'run_list': anmad_args.prepend_rootdir(self.playbookroot, self.playbooks)}
        anmad_buttons.LOGGER = self.logger


    def tearDown(self):
        self.playbooks = None
        self.pre_run_playbooks = None
        self.playbookroot = None
        self.testextras = None
        self.queues.clear()
        self.queues.clearinfo()

    def test_mainpage(self):
        """Test mainpage renders as expected."""
        rv = self.app.get('/')
        self.assertEqual(rv.status, '200 OK')
        self.assertIn('0.15.0', str(rv.data))
        self.assertIn('Other Playbooks', str(rv.data))
        self.assertIn('Queued Jobs', str(rv.data))
        self.assertIn('More logs...', str(rv.data))
        self.assertIn(self.pre_run_playbooks[0], str(rv.data))
        self.assertIn(self.playbooks[1], str(rv.data))


if __name__ == '__main__':
    unittest.main()
