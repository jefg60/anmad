#!/usr/bin/env python3
"""This daemon polls a directory for changed files and runs ansible
 playbooks when changes are detected."""

import logging
import logging.handlers
import argparse
import subprocess
import time
import shutil
import os
from os.path import expanduser
from pathlib import Path
import glob

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ssh_agent_setup

# Functions
def parse_args():
    """Read arguments from command line."""

    __version__ = "0.7"

    home = expanduser("~")

    try:
        ansible_home = os.path.dirname(
            os.path.dirname(shutil.which("ansible-playbook"))
        )
    except TypeError:
        ansible_home = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "-V",
        "--version",
        action="version",
        version=__version__
        )
    parser.add_argument(
        "--venv",
        help="python virtualenv to run ansible from",
        default=ansible_home
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
        "--pre_run_playbooks",
        nargs='*',
        help="space separated list of ansible playbooks to run "
             "before doing any syntax checking. Useful "
             "for playbooks that fetch roles required by other playbooks"
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
        "--ssh_askpass",
        help="location of a script to pass as SSH_ASKPASS env var,"
             "which will enable this program to load an ssh key if "
             "it has a passphrase. Only works if not running in a terminal"
        )
    parser.add_argument(
        "--no-syslog",
        dest="syslog",
        action="store_false",
        help="disable logging to syslog"
        )
    parser.add_argument(
        "--syslogdevice",
        help="syslog device to use",
        default="/dev/log"
        )
    parser.add_argument(
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="only wait for one --interval, for testing"
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


def add_ssh_key_to_agent(key_file):
    """Adds ssh key, with ssh_askpass if possible"""
    LOGGER.info("Loading ssh key...")
    ssh_agent_setup.setup()
    my_env = os.environ.copy()
    try:
        my_env["SSH_ASKPASS"] = ARGS.ssh_askpass
        my_env["DISPLAY"] = ":0"
    except TypeError:
        my_env = os.environ.copy()

    try:
        subprocess.run(['ssh-add', key_file], env=my_env, check=True)
    except TypeError:
        subprocess.run(['ssh-add', key_file], check=True)
    except subprocess.CalledProcessError:
        LOGGER.exception("Exception adding ssh key, shutting down")
        raise Exception
    else:
        LOGGER.info("SSH key loaded")

def syntax_check_play_inv(my_playbook, my_inventory):
    """Check a single playbook against a single inventory."""
    my_playbook = os.path.abspath(my_playbook)
    my_inventory = os.path.abspath(my_inventory)
    LOGGER.info("Syntax Checking ansible playbook %s against "
                "inventory %s", my_playbook, my_inventory)

    ret = subprocess.call(
        [
            ANSIBLE_PLAYBOOK_CMD,
            '--inventory', my_inventory,
            '--vault-password-file', ARGS.vault_password_file,
            my_playbook,
            '--syntax-check'
        ], cwd=ARGS.venv
    )

    if ret == 0:
        LOGGER.info(
            "ansible-playbook syntax check return code: "
            "%s", ret)
        bad_syntax = ''
    else:
        LOGGER.info(
            "Playbook %s failed syntax check!!!", my_playbook)
        LOGGER.debug(
            "ansible-playbook syntax check return code: "
            "%s", ret)
        bad_syntax = ('playbook: \n' + my_playbook +
                      '\n with inventory: \n' + my_inventory)
    return bad_syntax


def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    for my_inventory in ARGS.inventories:

        my_inventory = os.path.abspath(my_inventory)
        failed = syntax_check_play_inv(my_playbook, my_inventory)
        bad_inventories.append(failed)

    return bad_inventories


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
            LOGGER.error("Unable to find path %s , aborting", filename)
            return [filename]

    bad_playbooks = []
    for my_playbook in listofplaybooks:
        for my_inventory in listofinventories:

            failed = syntax_check_play_inv(my_playbook, my_inventory)
            bad_playbooks.append(failed)

    return bad_playbooks


def checkeverything():
    """Check all YAML in a directory for ansible syntax."""
    syntax_check_dir_path = Path(ARGS.syntax_check_dir)
    if not syntax_check_dir_path.exists():
        LOGGER.error(
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

        my_playbook = os.path.abspath(my_playbook)

        LOGGER.info("Attempting to run ansible-playbook --inventory %s %s",
                    MAININVENTORY, my_playbook)
        ret = subprocess.call(
            [
                ANSIBLE_PLAYBOOK_CMD,
                '--inventory', MAININVENTORY,
                '--vault-password-file', ARGS.vault_password_file,
                my_playbook
            ], cwd=ARGS.venv
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
            LOGGER.debug("Received directory event for %s, ignoring",
                         event.src_path)

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

            if ARGS.pre_run_playbooks is not None:
                LOGGER.info("Pre-Running playbooks %s",
                            ARGS.pre_run_playbooks)
                runplaybooks(ARGS.pre_run_playbooks)

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
                LOGGER.info("Playbooks/inventories that had failures: %s",
                            " \n".join(problemlisteverything))

                LOGGER.info("Refusing to run requested playbooks until "
                            "syntax checks pass")
            else:
                LOGGER.info("Playbooks/inventories that failed syntax check: "
                            "%s", " \n".join(problemlist))



if __name__ == '__main__':

    ARGS = parse_args()
    ANSIBLE_PLAYBOOK_CMD = ARGS.venv + '/bin/ansible-playbook'

    # Setup Logging globally
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]  %(message)s",
        handlers=[logging.StreamHandler()]
        )

    LOGGER = logging.getLogger('ansible_logpoll')

    # create sysloghandler if needed
    if ARGS.syslog:
        SYSLOGHANDLER = logging.handlers.SysLogHandler(
            address=ARGS.syslogdevice,
            facility='local3')
        SYSLOGFORMATTER = logging.Formatter(
            '%(name)s - [%(levelname)s] - %(message)s')
        SYSLOGHANDLER.setFormatter(SYSLOGFORMATTER)
        LOGGER.addHandler(SYSLOGHANDLER)

    # debug logging
    if ARGS.debug:
        LOGGER.level = logging.DEBUG

    # First inventory is the one that plays run against
    MAININVENTORY = os.path.abspath(ARGS.inventories[0])

    # log main arguments used
    LOGGER.info("ssh id: %s", ARGS.ssh_id)
    LOGGER.info("venv: %s", ARGS.venv)
    LOGGER.info("ansible_playbook_cmd: %s", ANSIBLE_PLAYBOOK_CMD)
    LOGGER.info("logdir: %s", ARGS.logdir)
    LOGGER.info("inventorylist: %s", " ".join(ARGS.inventories))
    LOGGER.info("maininventory: %s", MAININVENTORY)
    LOGGER.info("playbooks: %s", " ".join(ARGS.playbooks))
    LOGGER.info("interval: %s", str(ARGS.interval))

    add_ssh_key_to_agent(ARGS.ssh_id)
    LOGGER.info("Polling %s directory for updated files every %s seconds...",
                ARGS.logdir, ARGS.interval)
    W = Watcher()
    W.run()
