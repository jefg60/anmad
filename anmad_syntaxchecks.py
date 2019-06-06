"""Functions to check / run ansible playbooks."""
import os
from multiprocessing import Pool
import subprocess

import anmad_yaml
import anmad_args

def syntax_check_play_inv(
        logger,
        my_playbook,
        my_inventory,
        ansible_playbook_cmd,
        vault_password_file=None):
    """Check a single playbook against a single inventory.
    Plays should be absolute paths here.
    Returns ansible-playbook command return code
    (should be 0 if syntax checks pass)."""

    my_playbook = os.path.abspath(my_playbook)
    my_inventory = os.path.abspath(my_inventory)
    logger.info(
        "Syntax Checking ansible playbook %s against "
        "inventory %s", str(my_playbook), str(my_inventory))
    if vault_password_file is not None:
        ret = subprocess.call(
            [ansible_playbook_cmd,
             '--inventory', my_inventory,
             '--vault-password-file', vault_password_file,
             my_playbook, '--syntax-check'])
    else:
        ret = subprocess.call(
            [ansible_playbook_cmd,
             '--inventory', my_inventory,
             my_playbook, '--syntax-check'])
    if ret == 0:
        logger.info(
            "OK. ansible-playbook syntax check return code: "
            "%s", str(ret))
        return ret
    # if external syntax checks pass, the code below should NOT run
    logger.info(
        "Playbook %s failed syntax check against inventory %s!!!",
        str(my_playbook), str(my_inventory))
    logger.info(
        "ansible-playbook syntax check return code: "
        "%s", str(ret))
    try:
        logger.debug(
            "ansible-playbook syntax check return code: "
            "%s", str(ret))
    # catch any exceptions caused by the ret value being None etc.
    # generic log message if so, and return 255.
    except:
        logger.error(
            "verifying %s or %s failed for unknown reason",
            str(my_playbook), str(my_inventory))
        return 255
    # after logging any errors above, return the return code from ansible
    # to calling funcs
    return ret

def syntax_check_one_play_many_inv(
        logger,
        my_playbook,
        inventories,
        ansible_playbook_cmd,
        vault_password_file=None):
    """Check a single playbook against all inventories.
    Returns 0 if all OK, 1 or 2 if there was a parsing issue
    with the playbook or the inventories respectively.
    Returns 3 if ansible-playbook syntax check failed.
    If any errors are found, the function will stop and return one
    of the above without continuing."""
    # check if we've been passed a single string, make it a one item list
    # if so.
    if isinstance(inventories, str):
        inventories = [inventories]
    my_playbook = os.path.abspath(my_playbook)
    if not anmad_yaml.verify_yaml_file(logger, my_playbook):
        logger.error(
            "Unable to verify yaml file %s", str(my,playbook))
        return 1
    for my_inventory in inventories:
        my_inventory = os.path.abspath(my_inventory)
        if not anmad_yaml.verify_yaml_file(logger, my_inventory):
            logger.error(
                "Unable to verify yaml file %s", str(my_inventory))
            return 2
        if syntax_check_play_inv(logger, my_playbook, my_inventory, ansible_playbook_cmd, vault_password_file) is not 0:
            return 3
    # if none of the above return statements happen, then syntax checks 
    # passed and we can return 0 to the caller.
    return 0

def checkplaybooks(listofplaybooks):
    """Syntax check a list of playbooks."""

    bad_playbooks = []

    pool = Pool(ARGS.concurrency)
    bad_playbooks = pool.map(syntax_check_one_play_many_inv, listofplaybooks)
    pool.close()
    pool.join()

    if bad_playbooks is not []:
        return bad_playbooks
    
    return 0


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
