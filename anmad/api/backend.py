#!/usr/bin/env python3
"""API functions."""

from flask import abort, redirect
import git

import anmad.interface.backend as intbackend
from anmad.common.yaml import list_missing_files
from anmad.daemon.process import get_ansible_playbook_procs, kill, killall

def git_pull(**config):
    """Execute git pull on playbook_root_dir.
    Returns output of git pull op"""
    try:
        local_repo = git.cmd.Git(config["args"].playbook_root_dir)
        if config["args"].repo_deploykey:
            gitssh_cmd = 'ssh -i' + config["args"].repo_deploykey
            config["logger"].info("GIT_SSH_COMMAND=" + gitssh_cmd)
            local_repo.update_environment(
                GIT_SSH_COMMAND=gitssh_cmd )
        return local_repo.pull()
    except git.GitCommandError as error:
        return error

def runall(**config):
    """Run all playbooks after verifying that files exist."""
    problemfile = list_missing_files(
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
        intbackend.buttonlist(
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
        intbackend.extraplays(**config),
        **config)
    config["logger"].debug("Redirecting to others page")
    config["queues"].update_job_lists()
    return redirect(config["baseurl"] + 'otherplays')

def kill_proc_by_pid(requestedpid, **config):
    """Kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    proclist = get_ansible_playbook_procs()
    pids = [li['pid'] for li in proclist]
    if requestedpid in pids:
        kill(requestedpid)
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

def killall_ansible(**config):
    """equivalent to sh: killall ansible-playbook."""
    killedprocs = killall()
    for proc in killedprocs:
        config["logger"].warning(
            "KILLED process '%s' via killall", ' '.join(proc['cmdline']))
    return redirect(config["baseurl"] + "jobs")

def clearqueues(**config):
    """Clear redis queues."""
    config["logger"].info("Clear redis queues requested.")
    config["queues"].clear()
    config["queues"].update_job_lists()
    return redirect(config["baseurl"])
