#!/usr/bin/env python3
"""Anmad queue module."""
import pickle
import redis
from hotqueue import HotQueue
import boto3

def read_queue(queue, queue_system):
    """Reads jobs from queue, returns list of jobs."""
    output = []
    if queue_system == "localredis":
        redis_conn = redis.Redis()
        for msg in redis_conn.lrange(queue.key, 0, -1):
            output.append(pickle.loads(msg))
    elif queue_system == "sqs":
        pass
    else:
        raise ValueError
    return output

def trim_queue(queue, length, queue_system):
    """Trims a redis queue to last N items."""
    if queue_system == "localredis":
        redis_conn = redis.Redis()
        redis_conn.ltrim(queue.key, -length, -1)
    elif queue_system == "sqs":
        pass
    else:
        raise ValueError

class SqsQueue:
    """One SQS queue."""
    def __init__(self, queue_name, profile, region):
        # Create a session:
        session = boto3.session.Session(
                profile_name=profile,
                region_name=region)
        # Get the service resource
        sqs = session.resource('sqs')
        # Get the queue. This returns an SQS.Queue instance
        self.queue = sqs.get_queue_by_name(QueueName=queue_name)

    def put(self, message):
        response = self.queue.send_message(MessageBody=message)
        return response

    def clear(self):
        for message in self.queue.receive_messages():
            message.delete()

    def consume(self):
        """ Return a generator that yields whenever a message is waiting in the
        queue. Will block otherwise."""

        try:
            while True:
                msg = self.queue.receive_messages()
                if msg is None:
                    break
                yield msg
        except KeyboardInterrupt:
            print; return


class AnmadQueues:
    """Queues used by anmad."""
    def __init__(self, prequeue, queue, info, queue_system, aws_profile, region):
        if queue_system == "localredis":
            self.prequeue = HotQueue(prequeue)
            self.queue = HotQueue(queue)
            self.info = HotQueue(info)
        elif queue_system == "sqs":
            self.prequeue = SqsQueue(prequeue, aws_profile, region)
            self.queue = SqsQueue(queue, aws_profile, region)
            self.info = SqsQueue(info, aws_profile, region)
            # create sqs queue objects
        else:
            raise ValueError
        #self.update_job_lists()

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
