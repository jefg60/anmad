#!/usr/bin/env python3
"""Configuration and routes for anmad flask app."""
import datetime
import socket
import glob
from flask import Flask, render_template, redirect, request

import anmad.interface_backend
import anmad.api_backend
import anmad.queues
import anmad.version
import anmad.args
import anmad.logging
import anmad.yaml
import anmad.process

config = {
    "args": anmad.args.parse_args(),
    "version": anmad.version.VERSION + " on " + socket.getfqdn(),
    "baseurl": "/",
    "queues": anmad.queues.AnmadQueues('prerun', 'playbooks', 'info'),
}

config["logger"] = anmad.logging.logsetup(config["args"], 'Interface')

flaskapp = Flask(__name__)
flaskapp.add_template_filter(anmad.interface_backend.basename)

@flaskapp.route(config["baseurl"])
def mainpage():
    """Render main page."""
    config["queues"].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': config["version"],
        'daemon_status': anmad.interface_backend.service_status('anmad_run'),
        'preq_message': config["queues"].prequeue_list,
        'queue_message': config["queues"].queue_list,
        'messages': config["queues"].info_list[0:3],
        'playbooks': config["args"].playbooks,
        'prerun': config["args"].pre_run_playbooks,
        }
    config["logger"].debug("Rendering control page")
    return render_template('main.html',
                           **template_data)

@flaskapp.route(config["baseurl"] + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    config["logger"].debug("Redirecting to ARA reports page")
    return redirect(config["args"].ara_url)

@flaskapp.route(config["baseurl"] + "log")
def log_page():
    """Display info queues."""
    config["queues"].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad log',
        'time': time_string,
        'version': config["version"],
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
        'jobs': anmad.process.get_ansible_playbook_procs()
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
        'extras': anmad.interface_backend.extraplays(**config)
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
        loglist = glob.glob('/var/log/ansible/playbook/' + '*.log')
        loglist.sort()
        template_data = {
            'title' : 'ansible playbook logs',
            'time': time_string,
            'version': config["version"],
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
        'log': requestedlog,
        'text': content
        }
    return render_template('ansiblelog.html', **template_data)

@flaskapp.route(config["baseurl"] + "kill")
def kill_route():
    """Route to kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    requestedpid = request.args.get('pid', type=int)
    return anmad.api_backend.kill(requestedpid, **config)

@flaskapp.route(config["baseurl"] + "killall")
def killall_route():
    """equivalent to killall ansible-playbook."""
    killedprocs = anmad.process.killall()
    for proc in killedprocs:
        config["logger"].warning(
            "KILLED process '%s' via killall", ' '.join(proc['cmdline']))
    return redirect(config["baseurl"] + "jobs")

@flaskapp.route(config["baseurl"] + "clearqueues")
def clearqueues_route():
    """Clear redis queues."""
    config["logger"].info("Clear redis queues requested.")
    config["queues"].clear()
    config["queues"].update_job_lists()
    return redirect(config["baseurl"])

@flaskapp.route(config["baseurl"] + "runall")
def runall_button():
    """Run all playbooks after verifying that files exist."""
    return anmad.api_backend.runall(**config)

@flaskapp.route(config["baseurl"] + 'playbooks/<path:playbook>')
def configuredplaybook_button(playbook):
    """Runs one playbook, if its one of the configured ones."""
    return anmad.api_backend.configuredplaybook(playbook, **config)

@flaskapp.route(config["baseurl"] + 'otherplaybooks/<path:playbook>')
def otherplaybook_button(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    return anmad.api_backend.otherplaybook(playbook, **config)
