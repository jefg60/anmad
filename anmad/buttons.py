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

class AnmadConfig:
    """Anmad configuration class."""
    def __init__(self, appname):
        """Fetch required args into config dict."""
        self.baseurl = "/"
        self.version = anmad.version.VERSION + " on " + socket.getfqdn()
        self.flaskapp = Flask(appname)
        self.config = {
            'ara_url': anmad.args.parse_args().ara_url,
            'playbook_root_dir': anmad.args.parse_args().playbook_root_dir,
            'playbooks': anmad.args.parse_args().playbooks,
            'pre_run_playbooks': anmad.args.parse_args().pre_run_playbooks,
            'prerun_list': anmad.args.parse_args().prerun_list,
            'run_list': anmad.args.parse_args().run_list,
            'logger': anmad.logging.logsetup(),
            'queues': anmad.queues.AnmadQueues(
                'prerun', 'playbooks', 'info')
        }
        self.flaskapp.add_template_filter(anmad.button_funcs.basename)

app = AnmadConfig(__name__)

@app.flaskapp.route(app.baseurl)
def mainpage():
    """Render main page."""
    app.config['queues'].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': app.version,
        'daemon_status': anmad.button_funcs.service_status('anmad_run'),
        'preq_message': app.config['queues'].prequeue_list,
        'queue_message': app.config['queues'].queue_list,
        'messages': app.config['queues'].info_list[0:3],
        'playbooks': app.config['playbooks'],
        'prerun': app.config['pre_run_playbooks'],
        }
    app.config['logger'].debug("Rendering control page")
    return render_template('main.html',
                           **template_data)
@app.flaskapp.route(app.baseurl + "log")
def log():
    """Display info queues."""
    app.config['queues'].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad log',
        'time': time_string,
        'version': app.version,
        'messages': app.config['queues'].info_list,
        }
    app.config['logger'].debug("Rendering log page")
    return render_template('log.html', **template_data)

@app.flaskapp.route(app.baseurl + "jobs")
def jobs():
    """Display running jobs (like ps -ef | grep ansible-playbook)."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'ansible-playbook processes',
        'time': time_string,
        'version': app.version,
        'jobs': anmad.process.get_ansible_playbook_procs()
        }
    app.config['logger'].debug("Rendering job page")
    return render_template('job.html', **template_data)

@app.flaskapp.route(app.baseurl + "kill")
def kill():
    """Here be dragons. route to kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    proclist = anmad.process.get_ansible_playbook_procs()
    pids = [li['pid'] for li in proclist]
    requestedpid = request.args.get('pid', type=int)
    if requestedpid in pids:
        anmad.process.kill(requestedpid)
        app.config['logger'].warning("KILLED pid %s on request", requestedpid)
        for proc in proclist:
            if proc['pid'] == requestedpid:
                cmdline = ' '.join(proc['cmdline'])
                app.config['logger'].warning(
                    "pid %s had cmdline '%s'", requestedpid, cmdline)
    else:
        app.config['logger'].critical(
            "got request to kill PID %s which doesnt look like ansible-playbook!!!",
            requestedpid)
    return redirect(app.baseurl + "jobs")

@app.flaskapp.route(app.baseurl + "killall")
def killall():
    """equivalent to killall ansible-playbook."""
    killedprocs = anmad.process.killall()
    for proc in killedprocs:
        app.config['logger'].warning(
            "KILLED process '%s' via killall", ' '.join(proc['cmdline']))
    return redirect(app.baseurl + "jobs")

@app.flaskapp.route(app.baseurl + "otherplays")
def otherplaybooks():
    """Display other playbooks."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': app.version,
        'extras': anmad.button_funcs.extraplays(
            app.config['logger'],
            app.config['playbook_root_dir'],
            app.config['playbooks'])
        }
    app.config['logger'].debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)

@app.flaskapp.route(app.baseurl + "clearqueues")
def clearqueues():
    """Clear redis queues."""
    app.config['logger'].info("Clear redis queues requested.")
    app.config['queues'].clear()
    app.config['queues'].update_job_lists()
    return redirect(app.baseurl)

@app.flaskapp.route(app.baseurl + "runall")
def runall():
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad.yaml.list_missing_files(
        app.config['logger'],
        app.config['prerun_list'])
    if problemfile:
        app.config['logger'].info("Invalid files: %s", str(problemfile))
        return redirect(app.baseurl)

    if app.config['pre_run_playbooks'] is not None:
        for play in app.config['prerun_list']:
            if [play] not in app.config['queues'].prequeue_list:
                app.config['logger'].info("Pre-Queueing %s", str(play))
                app.config['queues'].prequeue_job(play)

    app.config['logger'].info("Queueing %s", str(app.config['run_list']))
    app.config['queues'].queue_job(app.config['run_list'])
    app.config['queues'].update_job_lists()

    app.config['logger'].debug("Redirecting to control page")
    return redirect(app.baseurl)

@app.flaskapp.route(app.baseurl + 'playbooks/<path:playbook>')
def configuredplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    anmad.button_funcs.oneplaybook(
        app.config['logger'],
        app.config['queues'],
        playbook,
        anmad.button_funcs.buttonlist(
            app.config['pre_run_playbooks'],
            app.config['playbooks']),
        app.config['playbook_root_dir'])
    app.config['queues'].update_job_lists()
    app.config['logger'].debug("Redirecting to control page")
    return redirect(app.baseurl)

@app.flaskapp.route(app.baseurl + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad.button_funcs.oneplaybook(
        app.config['logger'],
        app.config['queues'],
        playbook,
        anmad.button_funcs.extraplays(
            app.config['logger'], app.config['playbook_root_dir'],
            app.config['playbooks'], app.config['pre_run_playbooks']),
        app.config['playbook_root_dir'])
    app.config['logger'].debug("Redirecting to others page")
    app.config['queues'].update_job_lists()
    return redirect(app.baseurl + 'otherplays')

@app.flaskapp.route(app.baseurl + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    app.config['logger'].debug("Redirecting to ARA reports page")
    return redirect(app.config['ara_url'])

@app.flaskapp.route(app.baseurl + "ansiblelog")
def ansiblelog():
    """Display ansible.log."""
    app.config['logger'].debug("Displaying ansible.log")
    time_string = datetime.datetime.utcnow()
    requestedlog = request.args.get('play')
    if requestedlog == 'list':
        loglist = glob.glob('/var/log/ansible/playbook/' + '*.log')
        loglist.sort()
        template_data = {
            'title' : 'ansible playbook logs',
            'time': time_string,
            'version': app.version,
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
        'version': app.version,
        'log': requestedlog,
        'text': content
        }
    return render_template('ansiblelog.html', **template_data)
