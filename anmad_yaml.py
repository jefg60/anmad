"""Functions to verify yaml files."""
import os
import glob
from configparser import ConfigParser
import yaml

import anmad_logging

def find_yaml_files(logger, directory):
    """Returns a list of files with yaml or yml extensions in a directory.
    Does not recurse into subdirectories."""
    logger.debug("Searching in %s for yaml files", str(directory))
    yamlfiles = glob.glob(directory + '/*.yaml')
    ymlfiles = glob.glob(directory + '/*.yml')
    output = yamlfiles + ymlfiles
    output.sort()
    return output


def verify_yaml_file(logger, filename):
    """Try to read yaml safely, return False if not valid"""
    try:
        with open(filename, 'r') as my_filename:
            yaml.safe_load(my_filename)
    except FileNotFoundError:
        logger.error(
            "YAML File %s cannot be found", str(filename))
        return False
    except IsADirectoryError:
        if not find_yaml_files(filename):
            logger.error("No yaml files found in %s", str(filename))
            return False
        for yml in find_yaml_files(filename):
            verify_yaml_file(yml)
    except yaml.scanner.ScannerError:
        logger.error(
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
        fileargs1 = (ARGS.inventories + RUN_LIST + PRERUN_LIST)
    except TypeError:
        fileargs1 = (ARGS.inventories + RUN_LIST)
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
            LOGGER.error("Unable to find path %s , aborting", str(filename))
            return filename
    return str()

if __name__ == '__main__':
    QUEUES = anmad_logging.QUEUES
    VERSION = anmad_logging.VERSION

    ARGS = anmad_logging.ARGS
    ANSIBLE_PLAYBOOK_CMD = anmad_logging.ANSIBLE_PLAYBOOK_CMD
    MAININVENTORY = anmad_logging.MAININVENTORY
    PRERUN_LIST = anmad_logging.PRERUN_LIST
    RUN_LIST = anmad_logging.RUN_LIST
    LOGGER = anmad_logging.LOGGER
