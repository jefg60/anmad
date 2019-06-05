"""Functions to check / run ansible playbooks."""
import os
from multiprocessing import Pool
import subprocess

import anmad_yaml
import anmad_args

def syntax_check_play_inv(logger, my_playbook, my_inventory):
    """Check a single playbook against a single inventory.
    Plays should be absolute paths here.
    Returns a list of failed playbooks or inventories or
    an empty string if all were ok"""

    args = anmad_args.parse_args()

    my_playbook = os.path.abspath(my_playbook)
    my_inventory = os.path.abspath(my_inventory)
    logger.info(
        "Syntax Checking ansible playbook %s against "
        "inventory %s", str(my_playbook), str(my_inventory))
    ret = subprocess.call(
        [args.ansible_playbook_cmd,
         '--inventory', my_inventory,
         '--vault-password-file', args.vault_password_file,
         my_playbook, '--syntax-check'])
    if ret == 0:
        logger.info(
            "ansible-playbook syntax check return code: "
            "%s", str(ret))
        return str()

    logger.info(
        "Playbook %s failed syntax check!!!", str(my_playbook))
    try:
        logger.debug(
            "ansible-playbook syntax check return code: "
            "%s", str(ret))
    except NameError:
        logger.error(
            "playbooks / inventories must be valid YAML, %s or %s is not",
            str(my_playbook), str(my_inventory))
    return ('   playbook: ' + my_playbook +
            '\n   inventory: ' + my_inventory)

def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    if not anmad_yaml.verify_yaml_file(my_playbook):
        failed = ('failed playbook: ' + my_playbook)
        return failed
    for my_inventory in ARGS.inventories:
        my_inventory = os.path.abspath(my_inventory)
        if not anmad_yaml.verify_yaml_file(my_inventory):
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


def syntax_check_dir(logger, check_dir):
    """Check all YAML in a directory for ansible syntax."""
    if not os.path.exists(check_dir):
        logger.error("%s cannot be found", str(check_dir))
        return check_dir

    problemlist = checkplaybooks(anmad_yaml.find_yaml_files(check_dir))
    return problemlist


def run_one_playbook(logger, my_playbook):
    """Run exactly one ansible playbook. Don't call this
    directly. Instead, call one of the multi-playbook funcs with a list of
    one playbook eg [playbook]."""

    my_playbook = os.path.abspath(my_playbook)
    logger.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        str(MAININVENTORY), str(my_playbook))
    ret = subprocess.call(
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', MAININVENTORY,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        logger.info(
            "ansible-playbook %s return code: %s",
            str(my_playbook), str(ret))
        return ret

    logger.error(
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

if __name__ == '__main__':
    QUEUES = anmad_yaml.QUEUES
    VERSION = anmad_yaml.VERSION

    ARGS = anmad_yaml.ARGS
    ANSIBLE_PLAYBOOK_CMD = anmad_yaml.ANSIBLE_PLAYBOOK_CMD
    MAININVENTORY = anmad_yaml.MAININVENTORY
    PRERUN_LIST = anmad_yaml.PRERUN_LIST
    RUN_LIST = anmad_yaml.RUN_LIST
