#!/usr/bin/env python3
"""Daemon to watch redis queues for ansible jobs."""
import os
import sys

import anmad_syntaxchecks
import anmad_ssh

QUEUES = anmad_syntaxchecks.QUEUES
ARGS = anmad_syntaxchecks.ARGS
VERSION = anmad_syntaxchecks.VERSION
DEFAULT_CONFIGFILE = anmad_syntaxchecks.DEFAULT_CONFIGFILE
ANSIBLE_PLAYBOOK_CMD = anmad_syntaxchecks.ANSIBLE_PLAYBOOK_CMD
MAININVENTORY = anmad_syntaxchecks.MAININVENTORY
PRERUN_LIST = anmad_syntaxchecks.PRERUN_LIST
RUN_LIST = anmad_syntaxchecks.RUN_LIST
LOGGER = anmad_syntaxchecks.LOGGER

anmad_ssh.add_ssh_key_to_agent(ARGS.ssh_id)

for playbookjob in QUEUES.queue.consume():
    LOGGER.info("Starting to consume playbooks queue...")
    if playbookjob is not None:
        LOGGER.info("Found playbook queue job: %s", str(playbookjob))

        # when an item is found in the PLAYQ, first process all jobs in preQ!
        LOGGER.info("Starting to consume prerun queue...")
        while True:
            # get first item in preQ and check if its a list of 1 item,
            # if so run it
            preQ_job = QUEUES.prequeue.get()
            if isinstance(preQ_job, list) and len(preQ_job) == 1:
                LOGGER.info(
                    " Found a pre-run queue item: %s", str(preQ_job))
                # statements to process pre-Q job
                anmad_syntaxchecks.runplaybooks(preQ_job)

            # if it wasnt a list, but something is there, something is wrong
            elif preQ_job is not None:
                LOGGER.warning(
                    "item found in pre-run queue but its not a single item list")
                break
            else:
                LOGGER.info(
                    "processed all items in pre-run queue")
                break #stop processing pre-Q if its empty

        if playbookjob[0] == 'restart_anmad_run':
            LOGGER.info(
                'Restarting %s %s %s %s',
                str(sys.executable),
                str(sys.executable),
                str(__file__),
                " ".join(sys.argv[1:])
                )
            os.execl(sys.executable, sys.executable, __file__, *sys.argv[1:])

        LOGGER.info('Running job from playqueue: %s', str(playbookjob))
        #Syntax check playbooks, or all playbooks in syntax_check_dir
        if ARGS.syntax_check_dir is None:
            problemlist = anmad_syntaxchecks.checkplaybooks(playbookjob)
        else:
            problemlist = anmad_syntaxchecks.syntax_check_dir(
                ARGS.syntax_check_dir)

        if  ''.join(problemlist):
            LOGGER.warning(
                "Playbooks/inventories that failed syntax check: "
                "%s", " \n".join(problemlist))
            LOGGER.warning(
                "Refusing to queue requested playbooks until "
                "syntax checks pass")
            continue

        # if we get to here syntax checks passed. Run the job
        LOGGER.info(
            "Running playbooks %s", str(playbookjob))
        anmad_syntaxchecks.runplaybooks(playbookjob)
        LOGGER.info(
            "Continuing to process items in playbooks queue...")

LOGGER.warning("Stopped processing playbooks queue!")
