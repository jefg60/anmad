#!/usr/bin/env python3
"""Anmad queue module."""
import threading
from hotqueue import HotQueue

import anmad_logging

class AnmadQueues:
    """Queues used by anmad."""
    def __init__(self, prequeue, queue):
        self.prequeue = HotQueue(prequeue)
        self.prequeue_message = []
        self.queue = HotQueue(queue)
        self.queue_message = []
        self.cond = threading.Condition()

    def prequeue_job(self, job):
        """Adds an item to the pre-run queue."""
        anmad_logging.LOGGER.info("Pre-Queuing %s", [job])
        self.prequeue_message.append([job])
        self.prequeue.put([job])


    def queue_job(self, job):
        """Adds an item to the run queue."""
        anmad_logging.LOGGER.info("Queuing %s", job)
        self.queue_message.append(job)
        self.queue.put(job)

