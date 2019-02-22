#!/usr/bin/env python3
"""This daemon polls a directory for changed files and runs ansible
 playbooks when changes are detected."""

import subprocess
import time
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ssh_agent_setup

import constants
import syntaxchecks
import ansible_run

def add_ssh_key_to_agent(key_file):
    """Adds ssh key, with ssh_askpass if possible"""
    constants.LOGGER.info("Loading ssh key...")
    ssh_agent_setup.setup()
    my_env = os.environ.copy()
    if constants.ARGS.ssh_askpass is not None:
        my_env["SSH_ASKPASS"] = constants.ARGS.ssh_askpass
        my_env["DISPLAY"] = ":0"

    constants.LOGGER.debug("environment: %s", my_env)
    try:
        subprocess.run(['ssh-add', key_file],
                       env=my_env,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL
                       )
    except subprocess.CalledProcessError:
        constants.LOGGER.exception("Exception adding ssh key, shutting down")
        raise Exception
    else:
        constants.LOGGER.info("SSH key loaded")


def poll_for_updates(my_path):
    """Func to watch a file."""
    while True:
        event_handler = Handler()
        observer = Observer()
        observer.schedule(event_handler, my_path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(constants.ARGS.interval)
                if constants.ARGS.dryrun:
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
            constants.LOGGER.debug(
                "Received directory event for %s, ignoring",
                event.src_path)

        elif event.event_type == 'created':
            # actions when a file is first created.
            constants.LOGGER.info(
                "Received created event - %s.", event.src_path)

        elif event.event_type == 'modified':
            # actions when a file is modified.
            constants.LOGGER.info(
                "Received modified event - %s.", event.src_path)
            constants.LOGGER.debug(
                "ssh id: %s", constants.ARGS.ssh_id)
            constants.LOGGER.debug(
                "dir_to_watch: %s", constants.ARGS.dir_to_watch)
            constants.LOGGER.debug(
                "interval: %s", str(constants.ARGS.interval))
            constants.LOGGER.debug(
                "maininventory: %s", constants.MAININVENTORY)
            constants.LOGGER.debug(
                "inventorylist: %s", constants.ARGS.inventories)

            try:
                syntaxchecks.verify_files_exist()
            except FileNotFoundError:
                return

            if constants.ARGS.pre_run_playbooks is not None:
                constants.LOGGER.info(
                    "Pre-Running playbooks %s",
                    constants.ARGS.pre_run_playbooks)
                for my_playbook in constants.ARGS.pre_run_playbooks:
                    ansible_run.run_one_playbook(my_playbook)

            #Syntax check playbooks, or all playbooks in syntax_check_dir
            if constants.ARGS.syntax_check_dir is None:
                problemlist = syntaxchecks.checkplaybooks(
                    constants.ARGS.playbooks)
            else:
                problemlist = syntaxchecks.syntax_check_dir(
                    constants.ARGS.syntax_check_dir)

            if  ''.join(problemlist):
                constants.LOGGER.info(
                    "Playbooks/inventories that failed syntax check: "
                    "%s", " \n".join(problemlist))
                constants.LOGGER.info(
                    "Refusing to run requested playbooks until "
                    "syntax checks pass")
                return

            # if we get to here without returning, run the playbooks
            constants.LOGGER.info(
                "Running playbooks %s", constants.ARGS.playbooks)
            ansible_run.runplaybooks(constants.ARGS.playbooks)



if __name__ == '__main__':

    add_ssh_key_to_agent(constants.ARGS.ssh_id)
    constants.LOGGER.info(
        "Polling %s directory for updated files every %s seconds...",
        constants.ARGS.dir_to_watch, constants.ARGS.interval)
    subprocess.Popen(['python3', 'interface.py', '--logdir', constants.ARGS.dir_to_watch])
    poll_for_updates(constants.ARGS.dir_to_watch)
