#!/usr/bin/env python3
"""Simple script to add a restart job to anmad queue."""
from anmad.common.queues import AnmadQueues
from anmad.common.args import parse_anmad_args

ARGS = parse_anmad_args()
QUEUES = AnmadQueues(ARGS.prerun_queue, ARGS.playbook_queue, ARGS.info_queue)

QUEUES.queue_job(['restart_anmad_run'])
