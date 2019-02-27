#!/usr/bin/env python3
"""This daemon polls a directory for changed files and runs ansible
 playbooks when changes are detected."""

import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hotqueue import HotQueue

import anmad_args
import anmad_logging
import anmad_syntaxchecks
import ansible_run
import anmad_ssh

PLAYQ = HotQueue('playbooks')
PREQ = HotQueue('prerun')

def poll_for_updates(my_path):
    """Func to watch a file."""
    while True:
        event_handler = Handler()
        observer = Observer()
        observer.schedule(event_handler, my_path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(anmad_args.ARGS.interval)
                if anmad_args.ARGS.dryrun:
                    exit()
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


class Handler(FileSystemEventHandler):
    """Handle file events."""

    @staticmethod
    def on_any_event(event):
        """Tasks to perform if any events are received."""
        if event.is_directory:
            anmad_logging.LOGGER.debug(
                "Received directory event for %s, ignoring",
                event.src_path)

        elif event.event_type == 'created':
            # actions when a file is first created.
            anmad_logging.LOGGER.info(
                "Received created event - %s.", event.src_path)

        elif event.event_type == 'modified':
            # actions when a file is modified.
            anmad_logging.LOGGER.info(
                "Received modified event - %s.", event.src_path)
            anmad_logging.LOGGER.debug(
                "ssh id: %s", anmad_args.ARGS.ssh_id)
            anmad_logging.LOGGER.debug(
                "dir_to_watch: %s", anmad_args.ARGS.dir_to_watch)
            anmad_logging.LOGGER.debug(
                "interval: %s", str(anmad_args.ARGS.interval))
            anmad_logging.LOGGER.debug(
                "maininventory: %s", anmad_args.MAININVENTORY)
            anmad_logging.LOGGER.debug(
                "inventorylist: %s", anmad_args.ARGS.inventories)

            try:
                anmad_syntaxchecks.verify_files_exist()
            except FileNotFoundError:
                return

            if anmad_args.ARGS.pre_run_playbooks is not None:
                anmad_logging.LOGGER.info(
                    "Pre-Running playbooks %s",
                    anmad_args.ARGS.pre_run_playbooks)
                for my_playbook in anmad_args.ARGS.pre_run_playbooks:
                    ansible_run.runplaybooks([my_playbook])

            #Syntax check playbooks, or all playbooks in syntax_check_dir
            if anmad_args.ARGS.syntax_check_dir is None:
                problemlist = anmad_syntaxchecks.checkplaybooks(
                    anmad_args.ARGS.playbooks)
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
                return

            # if we get to here without returning, run the playbooks
            anmad_logging.LOGGER.info(
                "Queuing playbooks %s", anmad_args.ARGS.playbooks)
            PLAYQ.put(anmad_args.ARGS.playbooks)



if __name__ == '__main__':

    anmad_ssh.add_ssh_key_to_agent(anmad_args.ARGS.ssh_id)

    anmad_logging.LOGGER.info(
        "Polling %s directory for updated files every %s seconds...",
        anmad_args.ARGS.dir_to_watch, anmad_args.ARGS.interval)

    poll_for_updates(anmad_args.ARGS.dir_to_watch)
