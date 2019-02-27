#!/usr/bin/env python3
"""Daemon to watch a redis queue for ansible jobs."""

from hotqueue import HotQueue
queue = HotQueue('playbooks')

for item in queue.consume():
    print(item)
