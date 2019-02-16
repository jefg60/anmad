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
from multiprocessing import Pool

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ssh_agent_setup

# Functions
def parse_args():
    """Read arguments from command line."""

    __version__ = "0.9"

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
        "--dir_to_watch",
        help="dir to watch",
        default="/srv/git/log/configmanagement.log"
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
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', my_inventory,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook, '--syntax-check'])

    if ret == 0:
        LOGGER.info(
            "ansible-playbook syntax check return code: "
            "%s", ret)
        return str()

    LOGGER.info(
        "Playbook %s failed syntax check!!!", my_playbook)
    LOGGER.debug(
        "ansible-playbook syntax check return code: "
        "%s", ret)
    return ('   playbook: ' + my_playbook +
            '\n   inventory: ' + my_inventory)


def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    for my_inventory in ARGS.inventories:
        my_inventory = os.path.abspath(my_inventory)
        failed = syntax_check_play_inv(my_playbook, my_inventory)
    return failed


def checkplaybooks(listofplaybooks):
    """Syntax check a list of playbooks."""

    bad_playbooks = []

    pool = Pool()
    bad_playbooks = pool.map(syntax_check_play, listofplaybooks)

    return bad_playbooks


def syntax_check_dir(check_dir):
    """Check all YAML in a directory for ansible syntax."""
    if not Path(check_dir).exists:
        LOGGER.error("%s cannot be found", check_dir)
        return check_dir

    yamlfiles = glob.glob(ARGS.syntax_check_dir + '/*.yaml')
    ymlfiles = glob.glob(ARGS.syntax_check_dir + '/*.yml')
    yamlfiles = yamlfiles + ymlfiles
    problemlist = checkplaybooks(yamlfiles)
    return problemlist


def run_one_playbook(my_playbook):
    """Run exactly one ansible playbook."""
    my_playbook = os.path.abspath(my_playbook)
    LOGGER.info("Attempting to run ansible-playbook --inventory %s %s",
                MAININVENTORY, my_playbook)
    ret = subprocess.call(
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', MAININVENTORY,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        LOGGER.info("ansible-playbook %s return code: %s",
                    my_playbook, ret)
        return ret

    LOGGER.error("ansible-playbook %s return code: %s",
                 my_playbook, ret)
    return ret


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks."""
    pool = Pool()
    pool.map(run_one_playbook, listofplaybooks)


def verify_files_exist():
    """ Check that files exist before continuing."""
    fileargs = ARGS.inventories + ARGS.playbooks

    fileargs.append(ARGS.ssh_id)
    fileargs.append(ARGS.dir_to_watch)
    try:
        fileargs.append(ARGS.vault_password_file)
    except NameError:
        pass
    for filename in fileargs:
        filenamepath = Path(filename)
        if not filenamepath.exists():
            LOGGER.error("Unable to find path %s , aborting", filename)
            raise FileNotFoundError


def poll_for_updates(my_file):
    """Func to watch a file."""
    while True:
        event_handler = Handler()
        observer = Observer()
        observer.schedule(event_handler, my_file, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(ARGS.interval)
                if ARGS.dryrun:
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
            LOGGER.debug("Received directory event for %s, ignoring",
                         event.src_path)

        elif event.event_type == 'created':
            # actions when a file is first created.
            LOGGER.info("Received created event - %s.", event.src_path)

        elif event.event_type == 'modified':
            # actions when a file is modified.
            LOGGER.info("Received modified event - %s.", event.src_path)
            LOGGER.debug("ssh id: %s", ARGS.ssh_id)
            LOGGER.debug("dir_to_watch: %s", ARGS.dir_to_watch)
            LOGGER.debug("interval: %s", str(ARGS.interval))
            LOGGER.debug("maininventory: %s", MAININVENTORY)
            LOGGER.debug("inventorylist: %s", ARGS.inventories)

            try:
                verify_files_exist()
            except FileNotFoundError:
                return

            if ARGS.pre_run_playbooks is not None:
                LOGGER.info("Pre-Running playbooks %s",
                            ARGS.pre_run_playbooks)
                for my_playbook in ARGS.pre_run_playbooks:
                    run_one_playbook(my_playbook)

            #Syntax check playbooks, or all playbooks in syntax_check_dir
            if ARGS.syntax_check_dir is None:
                problemlist = checkplaybooks(ARGS.playbooks)
            else:
                problemlist = syntax_check_dir(ARGS.syntax_check_dir)

            if problemlist:
                LOGGER.info("Playbooks/inventories that failed syntax check: "
                            "%s", " \n".join(problemlist))
                LOGGER.info("Refusing to run requested playbooks until "
                            "syntax checks pass")
                return

            # if we get to here without returning, run the playbooks
            LOGGER.info("Running playbooks %s", ARGS.playbooks)
            runplaybooks(ARGS.playbooks)



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
    LOGGER.info("dir_to_watch: %s", ARGS.dir_to_watch)
    LOGGER.info("inventorylist: %s", " ".join(ARGS.inventories))
    LOGGER.info("maininventory: %s", MAININVENTORY)
    if ARGS.pre_run_playbooks:
        LOGGER.info("pre_run_playbooks: %s", " ".join(ARGS.pre_run_playbooks))
    LOGGER.info("playbooks: %s", " ".join(ARGS.playbooks))
    LOGGER.info("interval: %s", str(ARGS.interval))

    add_ssh_key_to_agent(ARGS.ssh_id)
    LOGGER.info("Polling %s directory for updated files every %s seconds...",
                ARGS.dir_to_watch, ARGS.interval)
    poll_for_updates(ARGS.dir_to_watch)
