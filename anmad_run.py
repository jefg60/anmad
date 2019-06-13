#!/usr/bin/env python3
"""Daemon to watch redis queues for ansible jobs."""
import os
import sys

import anmad_multi
import anmad_logging
import anmad_args
import anmad_ssh
import anmad_queues
import anmad_version

QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')
ARGS = anmad_args.parse_args()
LOGGER = anmad_logging.logsetup()
MULTIOBJ = anmad_multi.AnmadMulti(
    LOGGER,
    ARGS.inventories,
    ARGS.ansible_playbook_cmd,
    ARGS.vault_password_file,
    ARGS.timeout)

LOGGER.info("anmad_run version: %s starting", str(anmad_version.VERSION))
LOGGER.debug("config file: %s",
             str(ARGS.configfile)
             if ARGS.configfile is not None
             else str(ARGS.default_configfile))
LOGGER.debug("vault password file: %s", str(ARGS.vault_password_file))
LOGGER.debug("ssh id: %s", str(ARGS.ssh_id))
LOGGER.debug("venv: %s", str(ARGS.venv))
LOGGER.debug("ansible_playbook_cmd: %s", str(ARGS.ansible_playbook_cmd))
LOGGER.debug("inventorylist: %s", " ".join(ARGS.inventories))
LOGGER.debug("maininventory: %s", str(ARGS.maininventory))
if ARGS.pre_run_playbooks:
    LOGGER.debug("pre_run_playbooks: %s",
                 " ".join(ARGS.pre_run_playbooks))
    LOGGER.debug("PRERUN_LIST: %s",
                 " ".join(ARGS.prerun_list))
LOGGER.debug("playbooks: %s", " ".join(ARGS.playbooks))
LOGGER.debug("RUN_LIST: %s", " ".join(ARGS.run_list))
LOGGER.debug("playbook_root_dir: %s", str(ARGS.playbook_root_dir))

anmad_ssh.add_ssh_key_to_agent(LOGGER, ARGS.ssh_id, ARGS.ssh_askpass)

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
                MULTIOBJ.runplaybooks(preQ_job)

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
        if ARGS.syntax_check_dir is None or len(playbookjob) == 1:
            problemcount = MULTIOBJ.checkplaybooks(playbookjob)
        else:
            problemcount = MULTIOBJ.syncheck_dir(
                ARGS.syntax_check_dir)

        if problemcount != 0:
            LOGGER.warning(
                "Refusing to queue requested playbooks until "
                "syntax checks pass")
            continue

        # if we get to here syntax checks passed. Run the job
        LOGGER.info(
            "Running playbooks %s", str(playbookjob))
        MULTIOBJ.runplaybooks(playbookjob)
        LOGGER.info(
            "Continuing to process items in playbooks queue...")

LOGGER.warning("Stopped processing playbooks queue!")
