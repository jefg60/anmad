"""Functions to run ansible playbooks."""
import os
import subprocess
from multiprocessing import Pool, Lock

import anmad_args
import anmad_logging

PLAYBOOK_LOCK = Lock()

def run_one_playbook(my_playbook):
    """Run exactly one ansible playbook. Due to locking, don't call this
    directly. Instead, call one of the multi-playbook funcs with a list of
    one playbook eg [playbook]."""

    my_playbook = os.path.abspath(my_playbook)
    anmad_logging.LOGGER.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        anmad_args.MAININVENTORY, my_playbook)
    ret = subprocess.call(
        [anmad_args.ANSIBLE_PLAYBOOK_CMD,
         '--inventory', anmad_args.MAININVENTORY,
         '--vault-password-file', anmad_args.ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        anmad_logging.LOGGER.info(
            "ansible-playbook %s return code: %s",
            my_playbook, ret)
        return ret

    anmad_logging.LOGGER.error(
        "ansible-playbook %s return code: %s",
        my_playbook, ret)

    return ret


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks and wait for them to finish."""

    anmad_logging.LOGGER.debug("%s Waiting for playbook lock", __name__)
    PLAYBOOK_LOCK.acquire()
    anmad_logging.LOGGER.debug("Lock acquired")

    pool = Pool(anmad_args.ARGS.concurrency)
    ret = pool.map(run_one_playbook, listofplaybooks)
    pool.close()
    pool.join()

    PLAYBOOK_LOCK.release()
    anmad_logging.LOGGER.debug("Lock released")
    return ret

def runplaybooks_async(listofplaybooks):
    """Run a list of ansible playbooks asyncronously."""

    anmad_logging.LOGGER.debug("%s Waiting for playbook lock", __name__)
    PLAYBOOK_LOCK.acquire()
    anmad_logging.LOGGER.debug("Lock acquired")

    pool = Pool(anmad_args.ARGS.concurrency)
    ret = pool.map_async(run_one_playbook, listofplaybooks)
    pool.close()
    pool.join()

    PLAYBOOK_LOCK.release()
    anmad_logging.LOGGER.debug("Lock released")
    return ret
