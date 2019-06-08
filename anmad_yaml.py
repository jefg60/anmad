"""Functions to verify yaml files."""
import os
import glob
import configparser
import yaml

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
    filename = os.path.abspath(filename)
    try:
        with open(filename, 'r') as my_filename:
            yaml.safe_load(my_filename)
    except FileNotFoundError:
        logger.error("%s not found", filename)
        return False
    except IsADirectoryError:
        if not find_yaml_files(logger, filename):
            logger.error("No yaml files found in %s", str(filename))
            return False
        for yml in find_yaml_files(logger, filename):
            if not verify_yaml_file(logger, yml):
                return False
    except yaml.parser.ParserError:
        return False
    return True

def verify_config_file(filename):
    """Verify config file syntax. return True if passed."""
    try:
        config = configparser.ConfigParser()
        config.read(filename)
    except configparser.Error:
        return False
    return True

def list_bad_yamlfiles(logger, filelist):
    """ Check a list of yaml files for bad syntax.
    Return list of files that look wrong, or empty list if OK."""
    badfiles = []
    for filename in filelist:
        yamldata = verify_yaml_file(logger, filename)
        if not yamldata:
            badfiles.append(filename)
    return badfiles

def list_missing_files(logger, filelist):
    """Check a list of files to see if they exist. log if not.
    return empty list if OK or list of missing files."""
    badfiles = []
    for filename in filelist:
        if not os.path.exists(filename):
            logger.error("Unable to find path %s , aborting", str(filename))
            badfiles.append(filename)
    return badfiles
