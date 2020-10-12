#!/usr/bin/env python3
"""Functions for anmad_buttons."""

import os
import subprocess
from flask import abort, redirect

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

#def oneplaybook(logger, queues, playbook, playbooklist, playbook_root_dir):
def oneplaybook(playbook, playbooklist, **config):
    """Queues one playbook, only if its in the playbooklist."""
    if playbook not in playbooklist:
        config["logger"].warning("API request for %s DENIED", str(playbook))
        abort(404)
    my_runlist = [config["args"].playbook_root_dir + '/' + playbook]
    config["logger"].info("Queueing %s", str(my_runlist))
    config["queues"].queue_job(my_runlist)

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

def runall(**config):
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad.yaml.list_missing_files(
        config["logger"],
        config["args"].prerun_list)
    if problemfile:
        config["logger"].info("Invalid files: %s", str(problemfile))
        return redirect(config["baseurl"])

    if config["args"].pre_run_playbooks is not None:
        for play in config["args"].prerun_list:
            if [play] not in config["queues"].prequeue_list:
                config["logger"].info("Pre-Queueing %s", str(play))
                config["queues"].prequeue_job(play)

    config["logger"].info("Queueing %s", str(config["args"].run_list))
    config["queues"].queue_job(config["args"].run_list)
    config["queues"].update_job_lists()

    config["logger"].debug("Redirecting to control page")
    return redirect(config["baseurl"])

def configuredplaybook(playbook, **config):
    """Runs one playbook, if its one of the configured ones."""
    anmad.button_funcs.oneplaybook(
        playbook,
        anmad.button_funcs.buttonlist(
            config["args"].pre_run_playbooks,
            config["args"].playbooks),
        **config)
    config["queues"].update_job_lists()
    config["logger"].debug("Redirecting to control page")
    return redirect(config["baseurl"])

def otherplaybook(playbook, **config):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad.button_funcs.oneplaybook(
        playbook,
        anmad.button_funcs.extraplays(**config),
        **config)
    config["logger"].debug("Redirecting to others page")
    config["queues"].update_job_lists()
    return redirect(config["baseurl"] + 'otherplays')

def kill(requestedpid, **config):
    """Kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    proclist = anmad.process.get_ansible_playbook_procs()
    pids = [li['pid'] for li in proclist]
    if requestedpid in pids:
        anmad.process.kill(requestedpid)
        config["logger"].warning("KILLED pid %s on request", requestedpid)
        for proc in proclist:
            if proc['pid'] == requestedpid:
                cmdline = ' '.join(proc['cmdline'])
                config["logger"].warning(
                    "pid %s had cmdline '%s'", requestedpid, cmdline)
    else:
        config["logger"].critical(
            "got request to kill PID %s which doesnt look like ansible-playbook!!!",
            requestedpid)
    return redirect(config["baseurl"] + "jobs")
