"""anmad ssh key functions."""
import os
import subprocess

import ssh_agent_setup

import anmad_logging
import anmad_args

def add_ssh_key_to_agent(key_file):
    """Adds ssh key, with ssh_askpass if possible"""
    anmad_logging.LOGGER.info("Loading ssh key...")
    ssh_agent_setup.setup()
    my_env = os.environ.copy()
    if anmad_args.ARGS.ssh_askpass is not None:
        my_env["SSH_ASKPASS"] = anmad_args.ARGS.ssh_askpass
        my_env["DISPLAY"] = ":0"

    anmad_logging.LOGGER.debug("environment: %s", str(my_env))
    try:
        subprocess.run(['ssh-add', key_file],
                       env=my_env,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL
                       )
    except subprocess.CalledProcessError:
        anmad_logging.LOGGER.exception("Exception adding ssh key, shutting down")
        raise Exception
    else:
        anmad_logging.LOGGER.info("SSH key loaded")
