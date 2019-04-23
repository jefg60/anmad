"""Functions to run ansible playbooks."""
import os
import glob
from multiprocessing import Pool
from configparser import ConfigParser
import subprocess
import yaml

import anmad_logging

QUEUES = anmad_logging.QUEUES
VERSION = anmad_logging.VERSION

ARGS = anmad_logging.ARGS
ANSIBLE_PLAYBOOK_CMD = anmad_logging.ANSIBLE_PLAYBOOK_CMD
MAININVENTORY = anmad_logging.MAININVENTORY
PRERUN_LIST = anmad_logging.PRERUN_LIST
RUN_LIST = anmad_logging.RUN_LIST
LOGGER = anmad_logging.LOGGER

def find_yaml_files(directory):
    """Returns a list of files with yaml or yml extensions in a directory.
    Does not recurse into subdirectories."""
    LOGGER.info("Searching in %s for yaml files", str(directory))
    yamlfiles = glob.glob(directory + '/*.yaml')
    ymlfiles = glob.glob(directory + '/*.yml')
    return yamlfiles + ymlfiles


def verify_yaml_file(filename):
    """Try to read yaml safely, return False if not valid"""
    try:
        with open(filename, 'r') as my_filename:
            yaml.safe_load(my_filename)
    except FileNotFoundError:
        LOGGER.error(
            "YAML File %s cannot be found", str(filename))
        return False
    except IsADirectoryError:
        if not find_yaml_files(filename):
            LOGGER.error("No yaml files found in %s", str(filename))
            return False
        for yml in find_yaml_files(filename):
            verify_yaml_file(yml)
    except yaml.scanner.ScannerError:
        LOGGER.error(
            "Bad YAML syntax in %s", str(filename))
        return False
    except yaml.parser.ParserError:
        try:
            config = ConfigParser()
            config.read(filename)
        except config.Error:
            return False
    return True


def verify_files_exist():
    """ Check that files exist before continuing.
    Returns names of files that are missing or fail yaml syntax checks"""
    try:
        fileargs1 = (ARGS.inventories +
                     RUN_LIST +
                     PRERUN_LIST)
    except TypeError:
        fileargs1 = (ARGS.inventories +
                     RUN_LIST)
    badfiles = []
    for filename in fileargs1:
        yamldata = verify_yaml_file(filename)
        if not yamldata:
            badfiles.append(filename)
    if badfiles is not None:
        return badfiles

    fileargs2 = [ARGS.ssh_id]
    try:
        fileargs2.append(ARGS.vault_password_file)
    except NameError:
        pass
    for filename in fileargs2:
        if not os.path.exists(filename):
            LOGGER.error("Unable to find path %s , aborting",
                         str(filename))
            return filename
    return str()


def syntax_check_play_inv(my_playbook, my_inventory):
    """Check a single playbook against a single inventory.
    Plays should be absolute paths here.
    Returns a list of failed playbooks or inventories or
    an empty string if all were ok"""

    my_playbook = os.path.abspath(my_playbook)
    my_inventory = os.path.abspath(my_inventory)
    LOGGER.info(
        "Syntax Checking ansible playbook %s against "
        "inventory %s", str(my_playbook), str(my_inventory))
    ret = subprocess.call(
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', my_inventory,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook, '--syntax-check'])
    if ret == 0:
        LOGGER.info(
            "ansible-playbook syntax check return code: "
            "%s", str(ret))
        return str()

    LOGGER.info(
        "Playbook %s failed syntax check!!!", str(my_playbook))
    try:
        LOGGER.debug(
            "ansible-playbook syntax check return code: "
            "%s", str(ret))
    except NameError:
        LOGGER.error(
            "playbooks / inventories must be valid YAML, %s or %s is not",
            str(my_playbook), str(my_inventory))
    return ('   playbook: ' + my_playbook +
            '\n   inventory: ' + my_inventory)

def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    if not verify_yaml_file(my_playbook):
        failed = ('failed playbook: ' + my_playbook)
        return failed
    for my_inventory in ARGS.inventories:
        my_inventory = os.path.abspath(my_inventory)
        if not verify_yaml_file(my_inventory):
            failed = ('failed inventory: ' + my_inventory)
            return failed
        failed = syntax_check_play_inv(my_playbook, my_inventory)
    return failed


def checkplaybooks(listofplaybooks):
    """Syntax check a list of playbooks."""

    bad_playbooks = []

    pool = Pool(ARGS.concurrency)
    bad_playbooks = pool.map(syntax_check_play, listofplaybooks)
    pool.close()
    pool.join()

    return bad_playbooks


def syntax_check_dir(check_dir):
    """Check all YAML in a directory for ansible syntax."""
    if not os.path.exists(check_dir):
        LOGGER.error("%s cannot be found", str(check_dir))
        return check_dir

    problemlist = checkplaybooks(find_yaml_files(check_dir))
    return problemlist


def run_one_playbook(my_playbook):
    """Run exactly one ansible playbook. Don't call this
    directly. Instead, call one of the multi-playbook funcs with a list of
    one playbook eg [playbook]."""

    my_playbook = os.path.abspath(my_playbook)
    LOGGER.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        str(MAININVENTORY), str(my_playbook))
    ret = subprocess.call(
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', MAININVENTORY,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        LOGGER.info(
            "ansible-playbook %s return code: %s",
            str(my_playbook), str(ret))
        return ret

    LOGGER.error(
        "ansible-playbook %s did not complete, return code: %s",
        str(my_playbook), str(ret))
    return ret


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks and wait for them to finish."""

    pool = Pool(ARGS.concurrency)
    ret = pool.map(run_one_playbook, listofplaybooks)
    pool.close()
    pool.join()

    return ret
