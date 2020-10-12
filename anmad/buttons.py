#!/usr/bin/env python3
"""Configuration and routes for anmad flask app."""
import datetime
import socket
import glob
from flask import Flask, render_template, redirect, request

import anmad.button_funcs
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
flaskapp.add_template_filter(anmad.button_funcs.basename)

@flaskapp.route(config["baseurl"])
def mainpage():
    """Render main page."""
    config["queues"].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': config["version"],
        'daemon_status': anmad.button_funcs.service_status('anmad_run'),
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
def log():
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
def jobs():
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
def otherplaybooks():
    """Display other playbooks."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': config["version"],
        'extras': anmad.button_funcs.extraplays(
            config["logger"],
            config["args"].playbook_root_dir,
            config["args"].playbooks)
        }
    config["logger"].debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)

@flaskapp.route(config["baseurl"] + "ansiblelog")
def ansiblelog():
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
def kill():
    """Here be dragons. route to kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    proclist = anmad.process.get_ansible_playbook_procs()
    pids = [li['pid'] for li in proclist]
    requestedpid = request.args.get('pid', type=int)
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

@flaskapp.route(config["baseurl"] + "killall")
def killall():
    """equivalent to killall ansible-playbook."""
    killedprocs = anmad.process.killall()
    for proc in killedprocs:
        config["logger"].warning(
            "KILLED process '%s' via killall", ' '.join(proc['cmdline']))
    return redirect(config["baseurl"] + "jobs")

@flaskapp.route(config["baseurl"] + "clearqueues")
def clearqueues():
    """Clear redis queues."""
    config["logger"].info("Clear redis queues requested.")
    config["queues"].clear()
    config["queues"].update_job_lists()
    return redirect(config["baseurl"])

@flaskapp.route(config["baseurl"] + "runall")
def runall():
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

@flaskapp.route(config["baseurl"] + 'playbooks/<path:playbook>')
def configuredplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    anmad.button_funcs.oneplaybook(
        config["logger"],
        config["queues"],
        playbook,
        anmad.button_funcs.buttonlist(
            config["args"].pre_run_playbooks,
            config["args"].playbooks),
        config["args"].playbook_root_dir)
    config["queues"].update_job_lists()
    config["logger"].debug("Redirecting to control page")
    return redirect(config["baseurl"])

@flaskapp.route(config["baseurl"] + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad.button_funcs.oneplaybook(
        config["logger"],
        config["queues"],
        playbook,
        anmad.button_funcs.extraplays(
            config["logger"], config["args"].playbook_root_dir,
            config["args"].playbooks, config["args"].pre_run_playbooks),
        config["args"].playbook_root_dir)
    config["logger"].debug("Redirecting to others page")
    config["queues"].update_job_lists()
    return redirect(config["baseurl"] + 'otherplays')
