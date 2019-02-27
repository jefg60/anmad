#!/usr/bin/env python3
"""Daemon to watch redis queues for ansible jobs."""

from hotqueue import HotQueue

import anmad_args
import anmad_logging
import anmad_syntaxchecks
import ansible_run

PLAYQ = HotQueue('playbooks')
PREQ = HotQueue('prerun')

for playbookjob in PLAYQ.consume():

    # when an item is found in the PLAYQ, first process all jobs in preQ!
    while True:
        # get first item in preQ and check if its a list, if so run it
        preQ_job = PREQ.get()
        if isinstance(preQ_job, list):
            anmad_logging.LOGGER.info(
                "Found a pre-run queue item: %s", preQ_job)
            # statements to process pre-Q job
            ansible_run.runplaybooks(preQ_job)

        # if it wasnt a list, but something is there, something is wrong
        elif preQ_job is not None:
            anmad_logging.LOGGER.info(
                "WARNING: non list item found in pre-run queue")
            break
        else:
            anmad_logging.LOGGER.info(
                "INFO: processed all items in pre-run queue")
            break #stop processing pre-Q if its empty

    anmad_logging.LOGGER.info('Running job from playqueue: %s', playbookjob)
    #Syntax check playbooks, or all playbooks in syntax_check_dir
    if anmad_args.ARGS.syntax_check_dir is None:
        problemlist = anmad_syntaxchecks.checkplaybooks(
            playbookjob)
    else:
        problemlist = anmad_syntaxchecks.syntax_check_dir(
            anmad_args.ARGS.syntax_check_dir)

    if  ''.join(problemlist):
        anmad_logging.LOGGER.info(
            "Playbooks/inventories that failed syntax check: "
            "%s", " \n".join(problemlist))
        anmad_logging.LOGGER.info(
            "Refusing to queue requested playbooks until "
            "syntax checks pass")
        break

    # if we get to here syntax checks passed. Run the playbooks
    anmad_logging.LOGGER.info(
        "Running playbooks %s", anmad_args.ARGS.playbooks)
    ansible_run.runplaybooks(anmad_args.ARGS.playbooks)
