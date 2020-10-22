#!/usr/bin/env python3
"""Tests for anmad.interface module."""

import logging
import os
import unittest

import __main__ as main

import anmad.interface
from anmad.interface.routes import flaskapp
from anmad.common.queues import AnmadQueues
import anmad.common.args as anmadargs
import anmad.common.version as anmadver

class TestInterfaceApp(unittest.TestCase):
    """Tests for anmad.interface APP."""
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=duplicate-code

    def setUp(self):
        self.playbooks = ['deploy.yaml', 'deploy2.yaml']
        self.pre_run_playbooks = ['deploy4.yaml']
        self.playbookroot = '/vagrant/samples'
        self.version = anmadver.VERSION
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        # Change logging.ERROR to INFO, to see log messages during testing.
        self.logger.setLevel(logging.CRITICAL)
        self.testextras = ['deploy3.yaml']
        for num in range(5, 9):
            dnum = [('deploy' + str(num) + '.yaml')]
            self.testextras.extend(dnum)
        self.testextras.extend(['deploy9.yml'])
        self.queues = AnmadQueues(
            'test_prerun', 'test_playbooks', 'test_info')
        self.app = flaskapp.test_client()
        anmad.interface.routes.config['playbook_root_dir'] =  self.playbookroot
        anmad.interface.routes.config['playbooks'] =  self.playbooks
        anmad.interface.routes.config['pre_run_playbooks'] =  self.pre_run_playbooks
        anmad.interface.routes.config['prerun_list'] =  anmadargs.prepend_rootdir(
            self.playbookroot, self.pre_run_playbooks)
        anmad.interface.routes.config['run_list'] =  anmadargs.prepend_rootdir(
            self.playbookroot, self.playbooks)
        anmad.interface.routes.config['logger'] = self.logger
        anmad.interface.routes.config['queues'] = self.queues

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

    def test_logpage_playbook_button(self):
        """Test log page before / after playbook/deploy4."""
        response = self.app.get('/log')
        self.assertEqual(response.status, '200 OK')
        self.assertIn(self.version, str(response.data))
        self.assertIn("Back to main interface", str(response.data))
        self.assertIn("No messages found yet", str(response.data))
        self.assertNotIn("deploy4.yaml", str(response.data))
        response = self.app.get('/playbooks/deploy4.yaml')
        self.assertEqual(response.status, '302 FOUND')
        response = self.app.get('/playbooks/deploy7.yaml')
        self.assertEqual(response.status, '404 NOT FOUND')
        self.assertNotEqual(len(self.queues.queue_list), 0)
        self.assertEqual(len(self.queues.prequeue_list), 0)
        response = self.app.get('/clearqueues')
        self.assertEqual(response.status, '302 FOUND')
        self.assertEqual(len(self.queues.queue_list), 0)
        self.assertEqual(len(self.queues.prequeue_list), 0)

    def test_logpage_otherplaybook_button(self):
        """Test log page before / after playbook/deploy9."""
        response = self.app.get('/log')
        self.assertEqual(response.status, '200 OK')
        self.assertIn(self.version, str(response.data))
        self.assertIn("Back to main interface", str(response.data))
        self.assertIn("No messages found yet", str(response.data))
        self.assertNotIn("deploy4.yaml", str(response.data))
        response = self.app.get('/otherplaybooks/deploy8.yaml')
        self.assertEqual(response.status, '302 FOUND')
        self.assertNotEqual(len(self.queues.queue_list), 0)
        self.assertEqual(len(self.queues.prequeue_list), 0)
        response = self.app.get('/clearqueues')
        self.assertEqual(response.status, '302 FOUND')
        self.assertEqual(len(self.queues.queue_list), 0)
        self.assertEqual(len(self.queues.prequeue_list), 0)

    def test_otherplays_page(self):
        """Test otherplays page."""
        response = self.app.get('/otherplays')
        self.assertEqual(response.status, '200 OK')
        self.assertIn(self.version, str(response.data))
        self.assertIn("deploy9.yml", str(response.data))

    def test_queues(self):
        """Test runall and clearqueues button."""
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
