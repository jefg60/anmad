#!/usr/bin/env python3
"""Fetches a single YAML value from an ansible vault file, and prints it.
"""

import argparse
from os.path import expanduser
from ansible_vault import Vault

# Functions
def parse_args():
    """Read arguments from command line."""
    home = expanduser("~")
    __version__ = "0.13.6"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "-V",
        "--version",
        action="version",
        version=__version__
        )
    parser.add_argument(
        "--vault_password_file",
        help="vault password file. default ~/.vaultpw",
        default=home + "/.vaultpw"
        )
    parser.add_argument(
        "--vaultfile",
        help="vault file to open",
        required=True
        )
    parser.add_argument(
        "--yaml_key",
        help="name of YAML key to get data from",
        required=True
        )

    myargs = parser.parse_args()

    return myargs

def get_yaml_vault_data():
    """Gets data from vault and prints it."""
    vault_pass_file = open(ARGS.vault_password_file, "r")
    vault_password = vault_pass_file.read()
    vault = Vault(vault_password.rstrip())
    vault_data = vault.load(open(ARGS.vaultfile).read())
    myoutput = vault_data.get(ARGS.yaml_key)
    return myoutput

if __name__ == '__main__':

    ARGS = parse_args()
    OUTPUT = get_yaml_vault_data()
    if OUTPUT is not None:
        print(OUTPUT)
        exit(0)
    else:
        print("ERROR: no data found in yaml key", ARGS.yaml_key)
        exit(1)
