#!/usr/bin/env python3
"""Tests for anmad_queues module."""

import unittest
import anmad_queues

class TestQueues(unittest.TestCase):
    """Tests for anmad_queues module."""


    def setUp(self):
        """Setup some test queues."""
        self.preq1 = 'prequeue_test1.yml'
        self.preq2 = 'prequeue_test2.yml'
        self.q1 = ['queue_test1.yml', 'queue_test2.yaml']
        self.q2 = ['queue_test3.yml', 'queue_test4.yaml']
        self.queues = anmad_queues.AnmadQueues('test_prerun', 'test_playbooks', 'test_info')
        self.queues.clear()
        self.queues.clearinfo()
        self.queues.prequeue_job(self.preq1)
        self.queues.prequeue_job(self.preq2)
        self.queues.queue_job(self.q1)
        self.queues.queue_job(self.q2)
        # put 105 items in the info queue to fill it up
        for x in range(0, 105):
            self.queues.info.put(x)
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

    def test_queue_initial_lengths(self):
        """Test initial queue lengths."""
        self.assertEqual(len(self.queues.queue_list), 2)
        self.assertEqual(len(self.queues.prequeue_list), 2)
        self.assertLessEqual(len(self.queues.info_list), 100)

    def test_getfromqueues(self):
        """Test that queues can be consumed in correct order."""
        # get first item from each queue
        preQ_job = self.queues.prequeue.get()
        Q_job = self.queues.queue.get()
        self.assertEqual(preQ_job, [self.preq1])
        self.assertEqual(Q_job, self.q1)
        self.queues.update_job_lists()
        self.assertEqual(len(self.queues.queue_list), 1)
        self.assertEqual(len(self.queues.prequeue_list), 1)
        # get second item from each queue
        self.assertEqual(self.queues.prequeue.get(), [self.preq2])
        self.assertEqual(self.queues.queue.get(), self.q2)
        self.queues.update_job_lists()
        self.assertEqual(len(self.queues.queue_list), 0)
        self.assertEqual(len(self.queues.prequeue_list), 0)


if __name__ == '__main__':
    unittest.main()
