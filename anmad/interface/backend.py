#!/usr/bin/env python3
"""Functions for anmad_interface."""

import os
import subprocess

import anmad.yaml

def basename(path):
    """Simple func to be used as jinja2 filter."""
    return os.path.basename(path)

def buttonlist(playbooks, prerun=None):
    """Get a list of allowed playbook buttons."""
    try:
        my_buttonlist = (prerun + playbooks)
    except TypeError:
        my_buttonlist = (playbooks)
    return my_buttonlist

def extraplays(prerun=None, **config):
    """Get a list of yaml files in root dir that arent in buttonlist()."""
    yamlfiles = anmad.yaml.find_yaml_files(
        config["logger"], config["args"].playbook_root_dir)
    yamlbasenames = []
    for yml in yamlfiles:
        yamlbasenames.append(os.path.basename(yml))
    if prerun is None:
        my_buttonlist = buttonlist(config["args"].playbooks)
    else:
        my_buttonlist = buttonlist(config["args"].playbooks,
            config["args"].pre_run_playbooks)
    extraplaybooks = list(set(yamlbasenames) - set(my_buttonlist))
    extraplaybooks.sort()
    return extraplaybooks

def service_status(service):
    """Check a service status."""
    servicestatus = subprocess.run(
        ['systemctl',
         '--property',
         'StateChangeTimestamp,ActiveState,SubState',
         '--value',
         'show',
         service],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False)

    lines = servicestatus.stdout.splitlines()
    active_state = lines[0]
    sub_state = lines[1]
    state_change_timestamp = lines[2]

    if state_change_timestamp != '':
        state_change_timestamp = str(' since ' + lines[2])
    active_state = lines[0]
    return {"service": service,
            "active_state": active_state,
            "sub_state": sub_state,
            "state_change_timestamp": state_change_timestamp}
