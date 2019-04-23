"""Functions to run ansible playbooks."""
import os
import subprocess
from multiprocessing import Pool

import anmad_logging

QUEUES = anmad_logging.QUEUES
ARGS = anmad_logging.ARGS
VERSION = anmad_logging.VERSION
DEFAULT_CONFIGFILE = anmad_logging.DEFAULT_CONFIGFILE
ANSIBLE_PLAYBOOK_CMD = anmad_logging.ANSIBLE_PLAYBOOK_CMD
MAININVENTORY = anmad_logging.MAININVENTORY
PRERUN_LIST = anmad_logging.PRERUN_LIST
RUN_LIST = anmad_logging.RUN_LIST

def run_one_playbook(my_playbook):
    """Run exactly one ansible playbook. Don't call this
    directly. Instead, call one of the multi-playbook funcs with a list of
    one playbook eg [playbook]."""

    my_playbook = os.path.abspath(my_playbook)
    anmad_logging.LOGGER.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        str(MAININVENTORY), str(my_playbook))
    ret = subprocess.call(
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', MAININVENTORY,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        anmad_logging.LOGGER.info(
            "ansible-playbook %s return code: %s",
            str(my_playbook), str(ret))
        return ret

    anmad_logging.LOGGER.error(
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
