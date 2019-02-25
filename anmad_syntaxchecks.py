"""Ansible_logpoll syntax check module."""

import os
import glob
from multiprocessing import Pool
from pathlib import Path
import subprocess

import constants

def syntax_check_play_inv(my_playbook, my_inventory):
    """Check a single playbook against a single inventory."""
    my_playbook = os.path.abspath(my_playbook)
    my_inventory = os.path.abspath(my_inventory)
    constants.LOGGER.info(
        "Syntax Checking ansible playbook %s against "
        "inventory %s", my_playbook, my_inventory)
    ret = subprocess.call(
        [constants.ANSIBLE_PLAYBOOK_CMD,
         '--inventory', my_inventory,
         '--vault-password-file', constants.ARGS.vault_password_file,
         my_playbook, '--syntax-check'])

    if ret == 0:
        constants.LOGGER.info(
            "ansible-playbook syntax check return code: "
            "%s", ret)
        return str()

    constants.LOGGER.info(
        "Playbook %s failed syntax check!!!", my_playbook)
    constants.LOGGER.debug(
        "ansible-playbook syntax check return code: "
        "%s", ret)
    return ('   playbook: ' + my_playbook +
            '\n   inventory: ' + my_inventory)

def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    for my_inventory in constants.ARGS.inventories:
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
        constants.LOGGER.error("%s cannot be found", check_dir)
        return check_dir

    yamlfiles = glob.glob(check_dir + '/*.yaml')
    ymlfiles = glob.glob(check_dir + '/*.yml')
    yamlfiles = yamlfiles + ymlfiles
    problemlist = checkplaybooks(yamlfiles)
    return problemlist

def verify_files_exist():
    """ Check that files exist before continuing."""
    fileargs = constants.ARGS.inventories + constants.ARGS.playbooks

    fileargs.append(constants.ARGS.ssh_id)
    fileargs.append(constants.ARGS.dir_to_watch)
    try:
        fileargs.append(constants.ARGS.vault_password_file)
    except NameError:
        pass
    for filename in fileargs:
        filenamepath = Path(filename)
        if not filenamepath.exists():
            constants.LOGGER.error("Unable to find path %s , aborting", filename)
            raise FileNotFoundError
