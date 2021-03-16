#!/usr/bin/env python3
"""Daemon to watch redis queues for ansible jobs."""
import os
import sys

from anmad.daemon.multi import AnmadMulti
from anmad.common.logging import logsetup
from anmad.common.args import parse_anmad_args
from anmad.daemon.ssh import add_ssh_key_to_agent
from anmad.common.queues import AnmadQueues
import anmad.common.version as anmadver

def main_daemon_loop():
    """Loop over queue and run jobs."""
    args = parse_anmad_args()
    queues = AnmadQueues(args.prerun_queue, args.playbook_queue, args.info_queue)
    logger = logsetup(args, 'ANMAD Daemon')
    multiobj = AnmadMulti(
        vault_password_file=args.vault_password_file,
        timeout=args.timeout,
        logger=logger,
        ansible_log_path=args.ansible_log_path,
        inventories=args.inventories,
        ansible_playbook_cmd=args.ansible_playbook_cmd)

    logger.info("anmad_run version: %s starting", str(anmadver.VERSION))
    logger.debug("config file: %s",
                 str(args.configfile)
                 if args.configfile is not None
                 else str(args.default_configfile))
    logger.debug("vault password file: %s", str(args.vault_password_file))
    logger.debug("ssh id: %s", str(args.ssh_id))
    logger.debug("venv: %s", str(args.venv))
    logger.debug("ansible_playbook_cmd: %s", str(args.ansible_playbook_cmd))
    logger.debug("inventorylist: %s", " ".join(args.inventories))
    logger.debug("maininventory: %s", str(args.maininventory))
    if args.pre_run_playbooks:
        logger.debug("pre_run_playbooks: %s",
                     " ".join(args.pre_run_playbooks))
        logger.debug("PRERUN_LIST: %s",
                     " ".join(args.prerun_list))
    logger.debug("playbooks: %s", " ".join(args.playbooks))
    logger.debug("RUN_LIST: %s", " ".join(args.run_list))
    logger.debug("playbook_root_dir: %s", str(args.playbook_root_dir))

    add_ssh_key_to_agent(logger, args.ssh_id, args.ssh_askpass)

    for playbookjob in queues.queue.consume():
        logger.info("Starting to consume playbooks queue...")
        if playbookjob is not None:
            logger.info("Found playbook queue job: %s", str(playbookjob))

            # when an item is found in the PLAYQ, first process all jobs in preQ!
            logger.info("Starting to consume prerun queue...")
            while True:
                # get first item in preQ and check if its a list of 1 item,
                # if so run it
                prequeue_job = queues.prequeue.get()
                if isinstance(prequeue_job, list) and len(prequeue_job) == 1:
                    logger.info(
                        " Found a pre-run queue item: %s", str(prequeue_job))
                    # statements to process pre-Q job
                    multiobj.runplaybooks(prequeue_job)

                # if it wasnt a list, but something is there, something is wrong
                elif prequeue_job is not None:
                    logger.warning(
                        "item found in pre-run queue but its not a single item list")
                    break
                else:
                    logger.info(
                        "processed all items in pre-run queue")
                    break #stop processing pre-Q if its empty

            if playbookjob[0] == 'restart_anmad_run':
                logger.info(
                    'Restarting %s %s %s %s',
                    str(sys.executable),
                    str(sys.executable),
                    str(__file__),
                    " ".join(sys.argv[1:])
                    )
                os.execl(sys.executable, sys.executable, __file__, *sys.argv[1:])

            logger.info('Running job from playqueue: %s', str(playbookjob))
            #Syntax check playbooks, or all playbooks in syntax_check_dir
            if args.syntax_check_dir is None or len(playbookjob) == 1:
                problemcount = multiobj.checkplaybooks(playbookjob)
            else:
                problemcount = multiobj.syncheck_dir(
                    args.syntax_check_dir)

            if problemcount != 0:
                logger.warning(
                    "Refusing to queue requested playbooks until "
                    "syntax checks pass")
                continue

            # if we get to here syntax checks passed. Run the job
            logger.info(
                "Running playbooks %s", str(playbookjob))
            multiobj.runplaybooks(playbookjob)
            logger.info(
                "Continuing to process items in playbooks queue...")

    logger.warning("Stopped processing playbooks queue!")

if __name__ == '__main__':
    main_daemon_loop()
