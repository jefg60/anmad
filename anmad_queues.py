#!/usr/bin/env python3
"""Anmad queue module."""
import datetime
import pickle
import redis
from hotqueue import HotQueue

def read_queue(queue):
    """Reads jobs from queue, returns list of jobs."""
    redis_conn = redis.Redis()
    output = []
    for msg in redis_conn.lrange(queue.key, 0, -1):
        output.append(pickle.loads(msg))
    return output

def trim_queue(queue, length):
    """Trims a redis queue to last N items."""
    redis_conn = redis.Redis()
    redis_conn.ltrim(queue.key, -length, -1)


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
        trim_queue(self.info, 100)
        self.info_list = read_queue(self.info)
        self.info_list.reverse()

    def prequeue_job(self, job):
        """Adds an item to the pre-run queue."""
        self.prequeue.put([job])

    def queue_job(self, job):
        """Adds an item to the run queue."""
        self.queue.put(job)

    def clear(self):
        """Clears all job queues."""
        self.queue.clear()
        self.prequeue.clear()

    def clearinfo(self):
        """Clears info queue."""
        self.info.clear()
