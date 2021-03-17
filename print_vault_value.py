#!/usr/bin/env python3
"""Fetches a single YAML value from an ansible vault file, and prints it."""

import argparse
from os.path import expanduser
from ansible_vault import Vault

import anmad.common.version as anmadver

def parse_args():
    """Read arguments from command line."""
    home = expanduser("~")
    __version__ = anmadver.VERSION

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

def get_yaml_vault_data(args):
    """Gets data from vault and prints it."""
    vault_pass_file = open(args.vault_password_file, "r")
    vault_password = vault_pass_file.read()
    vault = Vault(vault_password.rstrip())
    vault_data = vault.load(open(args.vaultfile).read())
    myoutput = vault_data.get(args.yaml_key)
    return myoutput

def main():
    """ Main func. """
    args = parse_args()
    output = get_yaml_vault_data(args)
    if output is not None:
        print(output)
        raise SystemExit(0)

    print("ERROR: no data found in yaml key", args.yaml_key)
    raise SystemExit(1)

if __name__ == '__main__':
    main()
