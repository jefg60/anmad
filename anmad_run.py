#!/usr/bin/env python3
"""Daemon to watch a redis queue for ansible jobs."""

from hotqueue import HotQueue
queue = HotQueue('playbooks')

for item in queue.consume():
    if type(item) is not list:
        print('WARNING: %s from playbook queue is not a list, ignoring it', item)
    else:
        print(item)
