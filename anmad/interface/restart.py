#!/usr/bin/env python3
"""Simple script to add a restart job to anmad queue."""
from anmad.common.queues import AnmadQueues

QUEUES = AnmadQueues('prerun', 'playbooks', 'info')

QUEUES.queue_job(['restart_anmad_run'])
