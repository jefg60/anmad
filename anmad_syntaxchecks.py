"""anmad syntax check module."""

import os
import glob
from multiprocessing import Pool
from configparser import ConfigParser
import subprocess
import yaml

import anmad_args
import anmad_logging


def verify_yaml_file(filename):
    """Try to read yaml safely, return False if not valid"""
    try:
        with open(filename, 'r') as my_filename:
            yamldata = yaml.safe_load(my_filename)
    except FileNotFoundError:
        anmad_logging.LOGGER.error(
            "YAML File %s cannot be found", filename)
        yamldata = False
    except IsADirectoryError:
        anmad_logging.LOGGER.error(
            "Expected YAML File at %s but got a directory", filename)
        yamldata = False
    except yaml.scanner.ScannerError:
        anmad_logging.LOGGER.error(
            "Bad YAML syntax in %s", filename)
        yamldata = False
    except yaml.parser.ParserError:
        try:
            config = ConfigParser()
            yamldata = config.read(filename)
        except config.Error:
            yamldata = False
    return yamldata


def verify_files_exist():
    """ Check that files exist before continuing.
    Returns names of files that are missing or fail yaml syntax checks"""
    try:
        fileargs1 = (anmad_args.ARGS.inventories +
                     anmad_args.RUN_LIST +
                     anmad_args.PRERUN_LIST)
    except (AttributeError, TypeError):
        fileargs1 = (anmad_args.ARGS.inventories +
                     anmad_args.RUN_LIST)
    badfiles = []
    for filename in fileargs1:
        yamldata = verify_yaml_file(filename)
        if not yamldata:
            badfiles.append(filename)
    if badfiles is not None:
        return badfiles

    fileargs2 = anmad_args.ARGS.ssh_id + anmad_args.ARGS.dir_to_watch
    try:
        fileargs2.append(anmad_args.ARGS.vault_password_file)
    except NameError:
        pass
    for filename in fileargs2:
        if not os.path.exists(filename):
            anmad_logging.LOGGER.error("Unable to find path %s , aborting",
                                       filename)
            return filename
    return str()


def syntax_check_play_inv(my_playbook, my_inventory):
    """Check a single playbook against a single inventory.
    Plays should be absolute paths here.
    Returns a list of failed playbooks or inventories or
    an empty string if all were ok"""

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
    try:
        anmad_logging.LOGGER.debug(
            "ansible-playbook syntax check return code: "
            "%s", ret)
    except NameError:
        anmad_logging.LOGGER.error(
            "playbooks / inventories must be valid YAML, %s or %s is not",
            my_playbook, my_inventory)
    return ('   playbook: ' + my_playbook +
            '\n   inventory: ' + my_inventory)

def syntax_check_play(my_playbook):
    """Check a single playbook against all inventories."""
    my_playbook = os.path.abspath(my_playbook)
    for my_inventory in anmad_args.ARGS.inventories:
        my_inventory = os.path.abspath(my_inventory)
        if not verify_yaml_file(my_playbook):
            failed = ('failed playbook: ' + my_playbook)
            return failed
        if not verify_yaml_file(my_inventory):
            failed = ('failed inventory: ' + my_inventory)
            return failed

        failed = syntax_check_play_inv(my_playbook, my_inventory)
    return failed


def checkplaybooks(listofplaybooks):
    """Syntax check a list of playbooks."""

    bad_playbooks = []

    pool = Pool(anmad_args.ARGS.concurrency)
    bad_playbooks = pool.map(syntax_check_play, listofplaybooks)
    pool.close()
    pool.join()

    return bad_playbooks


def syntax_check_dir(check_dir):
    """Check all YAML in a directory for ansible syntax."""
    if not os.path.exists(check_dir):
        anmad_logging.LOGGER.error("%s cannot be found", check_dir)
        return check_dir

    yamlfiles = glob.glob(check_dir + '/*.yaml')
    ymlfiles = glob.glob(check_dir + '/*.yml')
    yamlfiles = yamlfiles + ymlfiles
    problemlist = checkplaybooks(yamlfiles)
    return problemlist
