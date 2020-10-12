#!/usr/bin/env python3
"""API functions."""

from flask import abort, redirect

import anmad.yaml
import anmad.interface_backend

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

def oneplaybook(playbook, playbooklist, **config):
    """Queues one playbook, only if its in the playbooklist."""
    if playbook not in playbooklist:
        config["logger"].warning("API request for %s DENIED", str(playbook))
        abort(404)
    my_runlist = [config["args"].playbook_root_dir + '/' + playbook]
    config["logger"].info("Queueing %s", str(my_runlist))
    config["queues"].queue_job(my_runlist)

def configuredplaybook(playbook, **config):
    """Runs one playbook, if its one of the configured ones."""
    oneplaybook(
        playbook,
        anmad.interface_backend.buttonlist(
            config["args"].pre_run_playbooks,
            config["args"].playbooks),
        **config)
    config["queues"].update_job_lists()
    config["logger"].debug("Redirecting to control page")
    return redirect(config["baseurl"])

def otherplaybook(playbook, **config):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    oneplaybook(
        playbook,
        anmad.interface_backend.extraplays(**config),
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
