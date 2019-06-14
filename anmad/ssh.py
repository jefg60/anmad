"""anmad ssh key functions."""
import os
import subprocess

import ssh_agent_setup

def add_ssh_key_to_agent(logger, key_file, ssh_askpass=None):
    """Adds ssh key, with ssh_askpass if possible"""
    logger.info("Loading ssh key...")
    ssh_agent_setup.setup()
    my_env = os.environ.copy()
    if ssh_askpass is not None:
        my_env["SSH_ASKPASS"] = ssh_askpass
        my_env["DISPLAY"] = ":0"

    logger.debug("environment: %s", str(my_env))
    try:
        subprocess.run(['ssh-add', key_file],
                       env=my_env,
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL
                       )
    except subprocess.CalledProcessError:
        logger.exception("Exception adding ssh key, shutting down")
        raise Exception
    else:
        logger.info("SSH key loaded")
