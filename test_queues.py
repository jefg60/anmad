#!/usr/bin/env python3
"""Tests for anmad_queues module."""

import unittest
import anmad_queues

class TestQueues(unittest.TestCase):
    """Tests for anmad_queues module."""


    def setUp(self):
        self.queues = anmad_queues.AnmadQueues('test_prerun', 'test_playbooks', 'test_info')
        self.queues.clear()
        self.queues.clearinfo()
        self.queues.prequeue_job(['prequeue_test.yml'])
        self.queues.queue_job(['queue_test.yml'])

    def tearDown(self):
        self.queues.clear()
        self.queues.clearinfo()

    def test_queue_init(self):
        """Test queue class init."""
        self.assertEqual(self.queues.prequeue.name, 'test_prerun')
        self.assertEqual(self.queues.queue.name, 'test_playbooks')
        self.assertEqual(self.queues.info.name, 'test_info')


if __name__ == '__main__':
    unittest.main()
