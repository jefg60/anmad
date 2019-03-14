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
    for msg in redis_conn.lrange('hotqueue:'+queue.name, 0, -1):
        output.append(pickle.loads(msg))
    return output


class AnmadQueues:
    """Queues used by anmad."""
    def __init__(self, prequeue, queue):
        self.prequeue = HotQueue(prequeue)
        self.queue = HotQueue(queue)
        self.reset()

    def reset(self):
        """Reset queue_message vars."""
        self.prequeue_message = []
        self.prequeue_message = read_queue(self.prequeue)
        self.queue_message = []
        self.queue_message = read_queue(self.queue)


    def prequeue_job(self, job):
        """Adds an item to the pre-run queue."""
        anmad_logging.LOGGER.info("Pre-Queuing %s", [job])
        self.prequeue.put([job])


    def queue_job(self, job):
        """Adds an item to the run queue."""
        anmad_logging.LOGGER.info("Queuing %s", job)
        self.queue.put(job)
