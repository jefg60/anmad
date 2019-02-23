"""Functions to run ansible playbooks."""
import os
import subprocess
from multiprocessing import Pool

import constants

def run_one_playbook(my_playbook):
    """Run exactly one ansible playbook."""
    my_playbook = os.path.abspath(my_playbook)
    constants.LOGGER.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        constants.MAININVENTORY, my_playbook)
    ret = subprocess.call(
        [constants.ANSIBLE_PLAYBOOK_CMD,
         '--inventory', constants.MAININVENTORY,
         '--vault-password-file', constants.ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        constants.LOGGER.info(
            "ansible-playbook %s return code: %s",
            my_playbook, ret)
        return ret

    constants.LOGGER.error(
        "ansible-playbook %s return code: %s",
        my_playbook, ret)
    return ret


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks."""
    pool = Pool(constants.ARGS.concurrency)
    pool.map_async(run_one_playbook, listofplaybooks)
