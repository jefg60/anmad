#!/usr/bin/env python3
"""Configuration and routes for anmad flask app."""
import datetime
from socket import getfqdn
from glob import glob
from os.path import basename
from flask import Flask, render_template, request

from anmad.interface.backend import service_status, extraplays
from anmad.common.queues import AnmadQueues
from anmad.common.args import parse_anmad_args
from anmad.common.logging import logsetup
from anmad.daemon.process import get_ansible_playbook_procs

import anmad.api.backend as apibackend
import anmad.common.version as anmadver

config = {
    "args": parse_anmad_args(),
    "version": anmadver.VERSION + " on " + getfqdn(),
    "baseurl": "/",
    "queues": AnmadQueues('prerun', 'playbooks', 'info'),
}

config["logger"] = logsetup(config["args"], 'ANMAD Interface')

flaskapp = Flask(__name__)
flaskapp.add_template_filter(basename)

@flaskapp.route(config["baseurl"])
def mainpage():
    """Render main page."""
    config["queues"].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': config["version"],
        'daemon_status': service_status('anmad'),
        'preq_message': config["queues"].prequeue_list,
        'queue_message': config["queues"].queue_list,
        'messages': config["queues"].info_list[0:config["args"].messagelist_size],
        'playbooks': config["args"].playbooks,
        'prerun': config["args"].pre_run_playbooks,
        }
    config["logger"].debug("Rendering control page")
    return render_template('main.html',
                           **template_data)

@flaskapp.route(config["baseurl"] + "log")
def log_page():
    """Display info queues."""
    config["queues"].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad log',
        'time': time_string,
        'version': config["version"],
        'daemon_status': service_status('anmad'),
        'messages': config["queues"].info_list,
        }
    config["logger"].debug("Rendering log page")
    return render_template('log.html', **template_data)

@flaskapp.route(config["baseurl"] + "jobs")
def jobs_page():
    """Display running jobs (like ps -ef | grep ansible-playbook)."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'ansible-playbook processes',
        'time': time_string,
        'version': config["version"],
        'daemon_status': service_status('anmad'),
        'jobs': get_ansible_playbook_procs()
        }
    config["logger"].debug("Rendering job page")
    return render_template('job.html', **template_data)

@flaskapp.route(config["baseurl"] + "otherplays")
def otherplaybooks_page():
    """Display other playbooks."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': config["version"],
        'daemon_status': service_status('anmad'),
        'extras': extraplays(**config)
        }
    config["logger"].debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)

@flaskapp.route(config["baseurl"] + "ansiblelog")
def ansiblelog_page():
    """Display ansible.log."""
    config["logger"].debug("Displaying ansible.log")
    time_string = datetime.datetime.utcnow()
    requestedlog = request.args.get('play')
    if requestedlog == 'list':
        loglist = glob('/var/log/ansible/playbook/' + '*.log')
        loglist.sort()
        template_data = {
            'title' : 'ansible playbook logs',
            'time': time_string,
            'version': config["version"],
            'daemon_status': service_status('anmad'),
            'logs': loglist,
            }
        return render_template('playbooklogs.html', **template_data)
    logfile = '/var/log/ansible/playbook/' + requestedlog
    text = open(logfile, 'r+')
    content = text.readlines()
    text.close()
    template_data = {
        'title' : 'ansible log for ' + requestedlog,
        'time': time_string,
        'version': config["version"],
        'daemon_status': service_status('anmad'),
        'log': requestedlog,
        'text': content
        }
    return render_template('ansiblelog.html', **template_data)

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

@flaskapp.route(config["baseurl"] + 'playbooks/<path:playbook>')
def configuredplaybook_button(playbook):
    """Runs one playbook, if its one of the configured ones."""
    return apibackend.configuredplaybook(playbook, **config)

@flaskapp.route(config["baseurl"] + 'otherplaybooks/<path:playbook>')
def otherplaybook_button(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    return apibackend.otherplaybook(playbook, **config)
