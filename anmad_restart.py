#!/usr/bin/env python3
"""Simple script to add a restart job to anmad queue."""
import anmad.queues

QUEUES = anmad.queues.AnmadQueues('prerun', 'playbooks', 'info')

QUEUES.queue_job(['restart_anmad_run'])
