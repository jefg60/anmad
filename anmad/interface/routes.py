#!/usr/bin/env python3
"""Configuration and routes for anmad flask app."""

from socket import getfqdn
from glob import glob
from os.path import basename, isfile, isdir, abspath, dirname, normpath, getctime, relpath
from flask import Flask, render_template, request, abort, redirect

from anmad.interface.backend import service_status, extraplays, timestring
from anmad.common.queues import AnmadQueues
from anmad.common.args import parse_anmad_args
from anmad.common.logging import logsetup
from anmad.daemon.process import get_ansible_playbook_procs

import anmad.api.backend as apibackend
import anmad.common.version as anmadver

config = {
    "args": parse_anmad_args(interface=True),
    "version": anmadver.VERSION,
    "hostname": getfqdn(),
    "baseurl": "/",
}

config["logger"] = logsetup(config["args"], 'ANMAD Interface')
config["queues"] = AnmadQueues(
        config["args"].prerun_queue,
        config["args"].playbook_queue,
        config["args"].info_queue)

flaskapp = Flask(__name__)
flaskapp.add_template_filter(basename)

@flaskapp.route(config["baseurl"])
def mainpage():
    """Render main page."""
    config["queues"].update_job_lists()
    template_data = {
        'title' : 'anmad',
        'time': timestring(),
        'version': config["version"],
        'hostname': config["hostname"],
        'daemon_status': service_status('anmad'),
        'preq_message': config["queues"].prequeue_list,
        'queue_message': config["queues"].queue_list,
        'messages': config["queues"].info_list[0:config["args"].messagelist_size],
        'playbooks': config["args"].playbooks,
        'prerun': config["args"].pre_run_playbooks,
        'jobs': get_ansible_playbook_procs()
        }
    config["logger"].debug("Rendering control page")
    return render_template('main.html',
                           **template_data)

@flaskapp.route(config["baseurl"] + "log")
def log_page():
    """Display info queues."""
    config["queues"].update_job_lists()
    template_data = {
        'title' : 'anmad log',
        'time': timestring(),
        'version': config["version"],
        'hostname': config["hostname"],
        'daemon_status': service_status('anmad'),
        'messages_long': config["queues"].info_list,
        }
    config["logger"].debug("Rendering log page")
    return render_template('log.html', **template_data)

@flaskapp.route(config["baseurl"] + "jobs")
def jobs_page():
    """Display running jobs (like ps -ef | grep ansible-playbook)."""
    template_data = {
        'title' : 'ansible-playbook processes',
        'time': timestring(),
        'version': config["version"],
        'hostname': config["hostname"],
        'daemon_status': service_status('anmad'),
        'messages': config["queues"].info_list[0:config["args"].messagelist_size],
        'jobs': get_ansible_playbook_procs()
        }
    config["logger"].debug("Rendering job page")
    return render_template('job.html', **template_data)

@flaskapp.route(config["baseurl"] + "otherplays")
def otherplaybooks_page():
    """Display other playbooks."""
    template_data = {
        'title' : 'anmad others',
        'time': timestring(),
        'version': config["version"],
        'hostname': config["hostname"],
        'daemon_status': service_status('anmad'),
        'messages': config["queues"].info_list[0:config["args"].messagelist_size],
        'extras': extraplays(**config)
        }
    config["logger"].debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)

@flaskapp.route(config["baseurl"] + "ansiblelog")
def ansiblelog_page():
    """Display ansible.logs."""
    play = request.args.get('play')
    toplevel = False
    # prevent use of .. to browse dirs above log_base
    if '..' in play:
        return abort(403)
    if not play or normpath(play) == '/' or normpath(play) == '//':
        play = '/'
        toplevel = True
    log_base = config["args"].ansible_log_path
    try_path = (log_base + play)
    latest = request.args.get('latest')
    parent = dirname(play)
    if normpath(parent) == '/' or normpath(parent) == '//':
        playbook = basename(play)
    else:
        playbook = basename(normpath(parent))
    # Get log dir lists if the param turns out to be a dir
    if isdir(try_path):
        config["logger"].debug("Displaying ansible log CHILD DIR " + try_path)
        loglist = glob(abspath(try_path) + '/*')
        if not toplevel:
            loglist.sort(reverse=True)
        else:
            loglist.sort()
        config["logger"].debug(play)
        template_data = {
            'title' : 'ansible playbook logs',
            'time': timestring(),
            'version': config["version"],
            'hostname': config["hostname"],
            'daemon_status': service_status('anmad'),
            'messages': config["queues"].info_list[0:config["args"].messagelist_size],
            'logs': loglist,
            'parent': parent,
            'log_base': normpath(play),
            'toplevel': toplevel,
            'playbook': playbook,
            }
        return render_template('playbooklogs.html', **template_data)
    # Try to find the latest logfile for play in the directory hierarchy
    if latest == 'True':
        config["logger"].debug("Finding latest log for " + play)
        list_of_logs = glob(log_base + '/' + play + '/**/*.log', recursive=True)
        if list_of_logs:
            latest_log = max(list_of_logs, key=getctime)
            relative_path = relpath(latest_log, start=log_base)
            try_path = (log_base + '/' + relative_path)
            parent = dirname('/' + relative_path)
        else:
            return abort(404, 'No logs found yet for ' + play)
    # If we get here, we should be looking at a file, not a dir
    if isfile(try_path):
        config["logger"].debug("Displaying ansible log file " + try_path)
        text = open(try_path, 'r+')
        content = text.readlines()
        text.close()
        template_data = {
            'title' : 'ansible log for ' + play,
            'time': timestring(),
            'version': config["version"],
            'hostname': config["hostname"],
            'daemon_status': service_status('anmad'),
            'log': play,
            'messages': config["queues"].info_list[0:config["args"].messagelist_size],
            'text': content,
            'parent': parent,
            }
        return render_template('ansiblelog.html', **template_data)
    # Abort if it turns out to not be a file, or a dir.
    return abort(403, 'Not a logfile or directory containing logfiles')

@flaskapp.route(config["baseurl"] + "kill")
def kill_route():
    """Route to kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    requestedpid = request.args.get('pid', type=int)
    return apibackend.kill_proc_by_pid(requestedpid, **config)

@flaskapp.route(config["baseurl"] + "killall")
def killall_route():
    """equivalent to killall ansible-playbook."""
    return apibackend.killall_ansible(**config)

@flaskapp.route(config["baseurl"] + "clearqueues")
def clearqueues_route():
    """Clear redis queues."""
    return apibackend.clearqueues(**config)

@flaskapp.route(config["baseurl"] + "runall")
def runall_button():
    """Run all playbooks after verifying that files exist."""
    return apibackend.runall(**config)

@flaskapp.route(config["baseurl"] + "gitpull")
def gitpull_button():
    """Git pull the playbook root dir."""
    if config["args"].gitpull:
        gitpull_out = apibackend.git_pull(**config)
        gitstr = 'git pull: '
        if isinstance(gitpull_out, apibackend.git.GitCommandError):
            config["logger"].error(gitstr + str(gitpull_out))
        else:
            config["logger"].info(gitstr + str(gitpull_out))
    else:
        config["logger"].warning("Git pull requested but it is disabled")
    return redirect(config["baseurl"])

@flaskapp.route(config["baseurl"] + 'playbooks/<path:playbook>')
def configuredplaybook_button(playbook):
    """Runs one playbook, if its one of the configured ones."""
    return apibackend.configuredplaybook(playbook, **config)

@flaskapp.route(config["baseurl"] + 'otherplaybooks/<path:playbook>')
def otherplaybook_button(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    return apibackend.otherplaybook(playbook, **config)
