"""Functions to run ansible playbooks."""
import os
import subprocess
from multiprocessing import Pool

import anmad_args
import anmad_logging
import anmad_queues

QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')

def run_one_playbook(my_playbook):
    """Run exactly one ansible playbook. Don't call this
    directly. Instead, call one of the multi-playbook funcs with a list of
    one playbook eg [playbook]."""

    my_playbook = os.path.abspath(my_playbook)
    anmad_logging.LOGGER.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        anmad_args.MAININVENTORY, my_playbook)
    anmad_logging.LOGGER.info(my_playbook + " Starting ansible-playbook...")
    ret = subprocess.call(
        [anmad_args.ANSIBLE_PLAYBOOK_CMD,
         '--inventory', anmad_args.MAININVENTORY,
         '--vault-password-file', anmad_args.ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        anmad_logging.LOGGER.info(
            "ansible-playbook %s return code: %s",
            my_playbook, ret)
        anmad_logging.LOGGER.info(my_playbook + " Completed successfully")
        return ret

    anmad_logging.LOGGER.error(
        "ansible-playbook %s return code: %s",
        my_playbook, str(ret))
    anmad_logging.LOGGER.info(my_playbook + " Did not complete, error code: " + str(ret))
    return ret


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks and wait for them to finish."""

    pool = Pool(anmad_args.ARGS.concurrency)
    ret = pool.map(run_one_playbook, listofplaybooks)
    pool.close()
    pool.join()

    return ret
