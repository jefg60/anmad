"""anmad ssh key functions."""
import os
import subprocess

import ssh_agent_setup

import anmad_logging

ARGS = anmad_logging.ARGS
LOGGER = anmad_logging.LOGGER

def add_ssh_key_to_agent(key_file):
    """Adds ssh key, with ssh_askpass if possible"""
    LOGGER.info("Loading ssh key...")
    ssh_agent_setup.setup()
    my_env = os.environ.copy()
    if ARGS.ssh_askpass is not None:
        my_env["SSH_ASKPASS"] = ARGS.ssh_askpass
        my_env["DISPLAY"] = ":0"

    LOGGER.debug("environment: %s", str(my_env))
    try:
        subprocess.run(['ssh-add', key_file],
                       env=my_env,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL
                       )
    except subprocess.CalledProcessError:
        LOGGER.exception("Exception adding ssh key, shutting down")
        raise Exception
    else:
        LOGGER.info("SSH key loaded")
