#!/usr/bin/env python3
"""This daemon polls a directory for changed files and runs ansible
 playbooks when changes are detected."""

import logging
import logging.handlers
import argparse
import subprocess
import time
from os.path import expanduser
from pathlib import Path
import glob

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ssh_agent_setup

# Functions
def parse_args():
    """Read arguments from command line."""
    home = expanduser("~")
    __version__ = "0.3"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "-V",
        "--version",
        action="version",
        version=__version__
        )
    parser.add_argument(
        "--interval",
        type=int,
        help="interval in seconds at which to check for new code",
        default=15
        )
    parser.add_argument(
        "--ssh_id",
        help="ssh id file to use",
        default=home + "/.ssh/id_rsa"
        )
    parser.add_argument(
        "--logdir",
        help="log dir to watch",
        default="/srv/git/log"
        )
    parser.add_argument(
        "--vault_password_file",
        help="vault password file",
        default=home + "/.vaultpw"
        )
    parser.add_argument(
        "--syntax_check_dir",
        help="Optional directory to search for *.yml and *.yaml files to "
             "syntax check when changes are detected"
        )
    parser.add_argument(
        "--playbooks",
        "-p",
        nargs='*',
        required=True,
        help="space separated list of ansible playbooks to run. "
        )
    parser.add_argument(
        "--inventories",
        "-i",
        nargs='*',
        required=True,
        help="space separated list of ansible inventories to syntax check "
             "against. The first inventory file "
             "will be the one that playbooks are run against if syntax "
             "checks pass"
        )
    parser.add_argument(
        "--no-syslog",
        dest="syslog",
        action="store_false",
        help="disable logging to syslog"
        )
    parser.add_argument(
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="don't actually run anything, for testing"
        )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="print debugging info to logs"
        )

    parser.set_defaults(debug=False, syslog=True, dryrun=False)

    myargs = parser.parse_args()

    return myargs



def add_ssh_key_to_agent():
    """Attempt to load ssh key into ssh-agent."""
    LOGGER.info("Loading ssh key...")
    try:
        ssh_agent_setup.setup()
        ssh_agent_setup.addKey(ARGS.ssh_id)
    except Exception:
        LOGGER.exception("Exception adding ssh key, shutting down")
        exit()
    else:
        LOGGER.info("SSH key loaded")


def checkplaybooks(listofplaybooks, listofinventories):
    """Syntax check playbooks passed on command line."""

    # Check that files exist before continuing
    fileargs = ARGS.inventories + ARGS.playbooks

    fileargs.append(ARGS.ssh_id)
    fileargs.append(ARGS.logdir)
    try:
        fileargs.append(ARGS.vault_password_file)
    except NameError:
        pass
    for filename in fileargs:
        filenamepath = Path(filename)
        if not filenamepath.exists():
            LOGGER.info("Unable to find path %s , aborting", filename)
            return [filename]

    bad_syntax_playbooks = []
    bad_syntax_inventories = []
    for my_playbook in listofplaybooks:
        for my_inventory in listofinventories:
            LOGGER.debug("Syntax Checking ansible playbook %s against "
                         "inventory %s", my_playbook, my_inventory)

            print("Syntax Checking ansible playbook %s against inventory %s"
                  % (my_playbook, my_inventory))

            ret = subprocess.call(
                [
                    'ansible-playbook',
                    '--inventory', my_inventory,
                    '--vault-password-file', ARGS.vault_password_file,
                    my_playbook,
                    '--syntax-check'
                ]
            )

            if ret == 0:
                LOGGER.info(
                    "ansible-playbook syntax check return code: "
                    "%s", ret)

            else:
                print(
                    "ansible-playbook %s failed syntax check!!!", my_playbook)
                LOGGER.error(
                    "Playbook %s failed syntax check!!!", my_playbook)
                LOGGER.error(
                    "ansible-playbook syntax check return code: "
                    "%s", ret)

                bad_syntax_playbooks.append(my_playbook)
                bad_syntax_inventories.append(my_inventory)
    return bad_syntax_playbooks + bad_syntax_inventories


def checkeverything():
    """Check all YAML in a directory for ansible syntax."""
    syntax_check_dir_path = Path(ARGS.syntax_check_dir)
    if not syntax_check_dir_path.exists():
        LOGGER.info(
            "--syntax_check_dir option passed but %s cannot be found",
            ARGS.syntax_check_dir)
        return ARGS.syntax_check_dir

    yamlfiles = glob.glob(ARGS.syntax_check_dir + '/*.yaml')
    ymlfiles = glob.glob(ARGS.syntax_check_dir + '/*.yml')
    yamlfiles = yamlfiles + ymlfiles
    problemlist = checkplaybooks(yamlfiles, ARGS.inventories)
    return problemlist


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks."""
    for my_playbook in listofplaybooks:
        LOGGER.debug("Attempting to run ansible-playbook --inventory %s %s",
                     MAININVENTORY, my_playbook)
        ret = subprocess.call(
            [
                'ansible-playbook',
                '--inventory', MAININVENTORY,
                '--vault-password-file', ARGS.vault_password_file,
                my_playbook
            ]
        )

        if ret == 0:
            LOGGER.info("ansible-playbook return code: %s", ret)
        else:
            LOGGER.error("ansible-playbook return code: %s", ret)
            # Is this break a good idea or not? should it be a bool param?
            break


class Watcher:
    """Class to watch ARGS.logdir for changes."""
    ARGS = parse_args()
    DIRECTORY_TO_WATCH = ARGS.logdir

    def __init__(self):
        """Set up event handler to check for changed files."""
        self.observer = Observer()

    def run(self):
        """Run event handler to check for changed files."""
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(ARGS.interval)
                if ARGS.dryrun:
                    exit()
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()


class Handler(FileSystemEventHandler):
    """Handle file events."""

    @staticmethod
    def on_any_event(event):
        """Tasks to perform if any events are received."""
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # actions when a file is first created.
            LOGGER.info("Received created event - %s.", event.src_path)

        elif event.event_type == 'modified':
            # actions when a file is modified.
            LOGGER.info("Received modified event - %s.", event.src_path)
            LOGGER.debug("ssh id: %s", ARGS.ssh_id)
            LOGGER.debug("logdir: %s", ARGS.logdir)
            LOGGER.debug("interval: %s", str(ARGS.interval))
            LOGGER.debug("maininventory: %s", MAININVENTORY)
            LOGGER.debug("workinginventorylist: %s", ARGS.inventories)

            # Additional syntax check of everything if requested
            if ARGS.syntax_check_dir is not None:
                problemlisteverything = checkeverything()
            else:
                problemlisteverything = []

            # Now do the syntax check of the playbooks we're about to run.
            problemlist = checkplaybooks(ARGS.playbooks, ARGS.inventories)

            if not problemlist and not problemlisteverything:
                LOGGER.info("Running playbooks %s", ARGS.playbooks)
                runplaybooks(ARGS.playbooks)
            elif ARGS.syntax_check_dir is not None:
                print("Playbooks/inventories that had failures: ",
                      " ".join(problemlisteverything))

                LOGGER.info("Playbooks/inventories that had failures: %s",
                            " ".join(problemlisteverything))

                print("Refusing to run requested playbooks until "
                      "syntax checks pass")
                LOGGER.info("Refusing to run requested playbooks until "
                            "syntax checks pass")
            else:
                print("Playbooks/inventories that failed syntax check: ",
                      " ".join(problemlist))
                LOGGER.info("Playbooks/inventories that failed syntax check: %s",
                            " ".join(problemlist))



if __name__ == '__main__':
    # Setup Logging globally
    LOGGER = logging.getLogger('ansible_logpoll')
    # create sysloghandler
    SYSLOGHANDLER = logging.handlers.SysLogHandler(address='/dev/log')
    SYSLOGHANDLER.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    CONSOLEHANDLER = logging.StreamHandler()
    CONSOLEHANDLER.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    FORMATTER = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    SYSLOGHANDLER.setFormatter(FORMATTER)
    CONSOLEHANDLER.setFormatter(FORMATTER)

    # add handlers to the logger
    LOGGER.addHandler(CONSOLEHANDLER)
    ARGS = parse_args()
    # decide which args to use
    if ARGS.debug:
        LOGGER.setLevel(logging.DEBUG)
    if ARGS.syslog:
        LOGGER.addHandler(SYSLOGHANDLER)

    MAININVENTORY = ARGS.inventories[0]

    # log main arguments used
    LOGGER.info("ssh id: %s", ARGS.ssh_id)
    LOGGER.info("logdir: %s", ARGS.logdir)
    LOGGER.info("inventorylist: %s", " ".join(ARGS.inventories))
    LOGGER.info("maininventory: %s", MAININVENTORY)
    LOGGER.info("playbooks: %s", " ".join(ARGS.playbooks))
    LOGGER.info("interval: %s", str(ARGS.interval))

    add_ssh_key_to_agent()
    LOGGER.info("Polling for updates...")
    W = Watcher()
    W.run()
