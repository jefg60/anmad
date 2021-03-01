#!/usr/bin/env python3
"""Functions for anmad_interface."""

from time import localtime,gmtime,strftime,strptime
from os.path import basename
import subprocess

from anmad.common.yaml import find_yaml_files

TIME_FORMAT = '%a %d %b %H:%M:%S %Z'

def buttonlist(playbooks, prerun=None):
    """Get a list of allowed playbook buttons."""
    try:
        my_buttonlist = (prerun + playbooks)
    except TypeError:
        my_buttonlist = (playbooks)
    return my_buttonlist

def extraplays(prerun=None, **config):
    """Get a list of yaml files in root dir that arent in buttonlist()."""
    yamlfiles = find_yaml_files(
        config["logger"], config["args"].playbook_root_dir)
    yamlbasenames = []
    for yml in yamlfiles:
        yamlbasenames.append(basename(yml))
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
         'show',
         service],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False)

    lines = servicestatus.stdout.splitlines()
    active_state = lines[0].split("=", 1)[1]
    sub_state = lines[1].split("=", 1)[1]
    if len(lines) > 2:
        state_change_time = strftime(TIME_FORMAT,
            strptime(lines[2],'%a %Y-%m-%d %H:%M:%S %Z'))
    else:
        state_change_time = 'system boot'
    return {"service": service,
            "active_state": active_state,
            "sub_state": sub_state,
            "state_change_time": state_change_time}

def timestring():
    """Return a tuple with formatted strings for localtime, and GMT time as a
    second value if localtime is not GMT."""
    gmt_time = gmtime()
    local_time = localtime()
    gmt_time_string = strftime(TIME_FORMAT, gmt_time)
    local_time_string = strftime(TIME_FORMAT, local_time)
    if local_time.tm_gmtoff == 0:
        return (local_time_string,)
    return (local_time_string, gmt_time_string)
