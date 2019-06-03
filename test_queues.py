#!/usr/bin/env python3
"""Tests for anmad_queues module."""

import unittest
import anmad_queues

class TestQueues(unittest.TestCase):
    """Tests for anmad_queues module."""


    def setUp(self):
        """Setup some test queues."""
        self.queues = anmad_queues.AnmadQueues('test_prerun', 'test_playbooks', 'test_info')
        self.queues.clear()
        self.queues.clearinfo()
        self.queues.prequeue_job('prequeue_test.yml')
        self.queues.queue_job(['queue_test1.yml', 'queue_test2.yaml'])
        self.queues.update_job_lists()

    def tearDown(self):
        """TearDown some test queues."""
        self.queues.clear()
        self.queues.clearinfo()

    def test_queue_init(self):
        """Test queue class init."""
        self.assertEqual(self.queues.prequeue.name, 'test_prerun')
        self.assertEqual(self.queues.queue.name, 'test_playbooks')
        self.assertEqual(self.queues.info.name, 'test_info')

    def test_queue_lengths(self):
        """Test queue lengths."""
        self.assertEqual(len(self.queues.queue_list), 1)
        self.assertEqual(len(self.queues.prequeue_list), 1)
        self.assertLessEqual(len(self.queues.info_list), 100)

    def test_addtoqueues(self):
        """Test queue lengths after adding to them."""
        self.queues.prequeue_job('prequeue_test2.yml')
        self.queues.queue_job(['queue_test3.yml', 'queue_test4.yaml'])
        self.queues.update_job_lists()
        self.assertEqual(len(self.queues.queue_list), 2)
        self.assertEqual(len(self.queues.prequeue_list), 2)
        self.assertLessEqual(len(self.queues.info_list), 100)



if __name__ == '__main__':
    unittest.main()
