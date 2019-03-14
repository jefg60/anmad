#!/usr/bin/env python3
"""Anmad queue module."""
import pickle
from hotqueue import HotQueue

import anmad_logging

def write_queue_to_file(message_list, filename):
    """Dumps a queue message list to a file."""
    with open(filename, 'wb+') as q_file:
        pickle.dump(message_list, q_file)


def read_queue_from_file(filename):
    """Reads a queue message list from a file."""
    anmad_logging.LOGGER.debug("Importing queue messages from file")
    with open(filename, 'rb') as q_file:
        return pickle.load(q_file)


class AnmadQueues:
    """Queues used by anmad."""
    def __init__(self, prequeue, queue):
        self.prequeue = HotQueue(prequeue)
        self.prequeue_file = '/tmp/anmad_prequeue'
        self.queue = HotQueue(queue)
        self.queue_file = '/tmp/anmad_queue'
        self.reset()

    def reset(self):
        """Reset queue_message vars."""
        try:
            self.prequeue_message = read_queue_from_file(self.prequeue_file)
        except (FileNotFoundError, EOFError):
            self.prequeue_message = []

        try:
            self.queue_message = read_queue_from_file(self.queue_file)
        except (FileNotFoundError, EOFError):
            self.queue_message = []


    def prequeue_job(self, job):
        """Adds an item to the pre-run queue."""
        anmad_logging.LOGGER.info("Pre-Queuing %s", [job])
        self.prequeue_message.append([job])
        self.prequeue.put([job])
        anmad_logging.LOGGER.debug("Exporting prequeue messages to file")
        write_queue_to_file(self.prequeue_message, self.prequeue_file)


    def remove_prejob(self, job):
        """Removes a prejob from the running job list."""
        anmad_logging.LOGGER.info("Marking prejob complete: %s", job)
        self.prequeue_message.remove(job)
        anmad_logging.LOGGER.debug("Exporting prequeue messages to file")
        write_queue_to_file(self.prequeue_message, self.prequeue_file)


    def queue_job(self, job):
        """Adds an item to the run queue."""
        anmad_logging.LOGGER.info("Queuing %s", job)
        self.queue_message.append(job)
        self.queue.put(job)
        anmad_logging.LOGGER.debug("Exporting queue messages to file")
        write_queue_to_file(self.queue_message, self.queue_file)


    def remove_job(self, job):
        """Removes a job from the running job list."""
        anmad_logging.LOGGER.info("Marking job complete: %s", job)
        self.queue_message.remove(job)
        anmad_logging.LOGGER.debug("Exporting queue messages to file")
        write_queue_to_file(self.queue_message, self.queue_file)
