#!/usr/bin/env python3
"""Daemon to watch redis queues for ansible jobs."""

from hotqueue import HotQueue
PLAYQ = HotQueue('playbooks')
PREQ = HotQueue('prerun')

for playbookjob in PLAYQ.consume():

    # when an item is found in the PLAYQ, first process all jobs in preQ!
    while True:
        # get first item in preQ and check if its a list, if so run it
        preQ_job = PREQ.get()
        if isinstance(preQ_job, list):
            print('Found a pre-run queue item: %s', str(preQ_job))
            # statements to process pre-Q job

        # if it wasnt a list, but something is there, something is wrong
        elif preQ_job is not None:
            print('WARNING: non list item found in pre-run queue')
            break
        else:
            print('INFO: processed all items in pre-run queue')
            break #stop processing pre-Q if its empty

    print('Processing %s', str(playbookjob))
    # statements to process playbookjob.
