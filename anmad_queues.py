#!/usr/bin/env python3
"""Anmad queue module."""
import pickle
import redis
from hotqueue import HotQueue

import anmad_logging

def read_queue(queue):
    """Reads jobs from queue, returns list of jobs."""
    redis_conn = redis.Redis()
    output = []
    for msg in redis_conn.lrange(queue.key, 0, -1):
        output.append(pickle.loads(msg))
    return output


class AnmadQueues:
    """Queues used by anmad."""
    def __init__(self, prequeue, queue, info):
        self.prequeue = HotQueue(prequeue)
        self.queue = HotQueue(queue)
        self.info = HotQueue(info)
        self.update_job_lists()

    def update_job_lists(self):
        """Reset queue_message vars."""
        self.prequeue_list = []
        self.prequeue_list = read_queue(self.prequeue)
        self.queue_list = []
        self.queue_list = read_queue(self.queue)
        self.info_list = []
        self.info_list = read_queue(self.info)


    def prequeue_job(self, job):
        """Adds an item to the pre-run queue."""
        anmad_logging.LOGGER.info("Pre-Queuing %s", [job])
        self.prequeue.put([job])


    def queue_job(self, job):
        """Adds an item to the run queue."""
        anmad_logging.LOGGER.info("Queuing %s", job)
        self.queue.put(job)


    def clear(self):
        """Clears all job queues."""
        self.queue.clear()
        self.prequeue.clear()

    def clearinfo(self):
        """Clears info queue."""
        self.info.clear()
