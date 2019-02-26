"""anmad syntax check module."""

import os
import glob
from multiprocessing import Pool
from pathlib import Path
import subprocess

import anmad_args
import anmad_logging

def syntax_check_play_inv(my_playbook, my_inventory):
    """Check a single playbook against a single inventory."""
    my_playbook = os.path.abspath(my_playbook)
    my_inventory = os.path.abspath(my_inventory)
    anmad_logging.LOGGER.info(
        "Syntax Checking ansible playbook %s against "
        "inventory %s", my_playbook, my_inventory)
    ret = subprocess.call(
        [anmad_args.ANSIBLE_PLAYBOOK_CMD,
         '--inventory', my_inventory,
         '--vault-password-file', anmad_args.ARGS.vault_password_file,
         my_playbook, '--syntax-check'])

    if ret == 0:
        anmad_logging.LOGGER.info(
            "ansible-playbook syntax check return code: "
            "%s", ret)
        return str()

    anmad_logging.LOGGER.info(
        "Playbook %s failed syntax check!!!", my_playbook)
    anmad_logging.LOGGER.debug(
        "ansible-playbook syntax check return code: "
        "%s", ret)
    return ('   playbook: ' + my_playbook +
            '\n   inventory: ' + my_inventory)

def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    for my_inventory in anmad_args.ARGS.inventories:
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
        anmad_logging.LOGGER.error("%s cannot be found", check_dir)
        return check_dir

    yamlfiles = glob.glob(check_dir + '/*.yaml')
    ymlfiles = glob.glob(check_dir + '/*.yml')
    yamlfiles = yamlfiles + ymlfiles
    problemlist = checkplaybooks(yamlfiles)
    return problemlist

def verify_files_exist():
    """ Check that files exist before continuing."""
    fileargs = anmad_args.ARGS.inventories + anmad_args.ARGS.playbooks

    fileargs.append(anmad_args.ARGS.ssh_id)
    fileargs.append(anmad_args.ARGS.dir_to_watch)
    try:
        fileargs.append(anmad_args.ARGS.vault_password_file)
    except NameError:
        pass
    for filename in fileargs:
        filenamepath = Path(filename)
        if not filenamepath.exists():
            anmad_logging.LOGGER.error("Unable to find path %s , aborting", filename)
            raise FileNotFoundError
