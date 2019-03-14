#!/usr/bin/env python3
"""Daemon to watch redis queues for ansible jobs."""

from hotqueue import HotQueue

import anmad_args
import anmad_logging
import anmad_syntaxchecks
import anmad_ssh
import ansible_run
import anmad_buttons
import anmad_queues

PLAYQ = HotQueue('playbooks')
PREQ = HotQueue('prerun')
QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks')

anmad_ssh.add_ssh_key_to_agent(anmad_args.ARGS.ssh_id)

anmad_logging.LOGGER.info("Starting to consume playbooks queue...")
for playbookjob in PLAYQ.consume():

    # when an item is found in the PLAYQ, first process all jobs in preQ!
    anmad_logging.LOGGER.info("Starting to consume prerun queue...")
    while True:
        # get first item in preQ and check if its a list of 1 item,
        # if so run it
        preQ_job = PREQ.get()
        if isinstance(preQ_job, list) and len(preQ_job) == 1:
            anmad_logging.LOGGER.info(
                "Found a pre-run queue item: %s", preQ_job)
            # statements to process pre-Q job
            ansible_run.runplaybooks(preQ_job)
            print(anmad_buttons.PREQ_MESSAGE)
            anmad_buttons.PREQ_MESSAGE.remove(preQ_job)

        # if it wasnt a list, but something is there, something is wrong
        elif preQ_job is not None:
            anmad_logging.LOGGER.warning(
                "item found in pre-run queue but its not a single item list")
            break
        else:
            anmad_logging.LOGGER.info(
                "processed all items in pre-run queue")
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
        anmad_logging.LOGGER.warning(
            "Playbooks/inventories that failed syntax check: "
            "%s", " \n".join(problemlist))
        anmad_logging.LOGGER.warning(
            "Refusing to queue requested playbooks until "
            "syntax checks pass")
        continue

    # if we get to here syntax checks passed. Run the job
    anmad_logging.LOGGER.info(
        "Running playbooks %s", playbookjob)
    ansible_run.runplaybooks(playbookjob)
    anmad_buttons.Q_MESSAGE.remove(playbookjob)
    anmad_logging.LOGGER.info(
        "Continuing to process items in playbooks queue...")

anmad_logging.LOGGER.warning("Stopped processing playbooks queue!")
