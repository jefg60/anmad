#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
import socket
import mod_wsgi
from flask import Flask, render_template, redirect, request

import anmad.button_funcs
import anmad.queues
import anmad.version
import anmad.args
import anmad.logging
import anmad.yaml
import anmad.process

APP = Flask(__name__)
BASEURL = "/"
VERSION = anmad.version.VERSION + " on " + socket.getfqdn()

def configure_app():
    """Fetch required args into config dict."""
    APP.config['ara_url'] = anmad.args.parse_args().ara_url
    APP.config['playbook_root_dir'] = anmad.args.parse_args().playbook_root_dir
    APP.config['playbooks'] = anmad.args.parse_args().playbooks
    APP.config['pre_run_playbooks'] = anmad.args.parse_args().pre_run_playbooks
    APP.config['prerun_list'] = anmad.args.parse_args().prerun_list
    APP.config['run_list'] = anmad.args.parse_args().run_list
    APP.config['logger'] = anmad.logging.logsetup()
    APP.config['queues'] = anmad.queues.AnmadQueues(
        'prerun', 'playbooks', 'info')
    APP.add_template_filter(anmad.button_funcs.basename)

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    APP.config['queues'].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': VERSION,
        'daemon_status': anmad.button_funcs.service_status('anmad_run'),
        'preq_message': APP.config['queues'].prequeue_list,
        'queue_message': APP.config['queues'].queue_list,
        'messages': APP.config['queues'].info_list[0:3],
        'playbooks': APP.config['playbooks'],
        'prerun': APP.config['pre_run_playbooks'],
        }
    APP.config['logger'].debug("Rendering control page")
    return render_template('main.html',
                           **template_data)

@APP.route(BASEURL + "log")
def log():
    """Display info queues."""
    APP.config['queues'].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad log',
        'time': time_string,
        'version': VERSION,
        'messages': APP.config['queues'].info_list,
        }
    APP.config['logger'].debug("Rendering log page")
    return render_template('log.html', **template_data)

@APP.route(BASEURL + "jobs")
def jobs():
    """Display running jobs (like ps -ef | grep ansible-playbook)."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'ansible-playbook processes',
        'time': time_string,
        'version': VERSION,
        'jobs': anmad.process.get_ansible_playbook_procs()
        }
    APP.config['logger'].debug("Rendering job page")
    return render_template('job.html', **template_data)

@APP.route(BASEURL + "kill")
def kill():
    """Here be dragons. route to kill a proc by PID.
    Hopefully a PID thats verified by psutil to be an ansible-playbook!"""
    proclist = anmad.process.get_ansible_playbook_procs()
    pids = [li['pid'] for li in proclist]
    requestedpid = request.args.get('pid', type=int)
    if requestedpid in pids:
        anmad.process.kill(requestedpid)
        APP.config['logger'].warning("KILLED pid %s on request", requestedpid)
        for proc in proclist:
            if proc['pid'] == requestedpid:
                cmdline = ' '.join(proc['cmdline'])
                APP.config['logger'].warning(
                    "pid %s had cmdline '%s'", requestedpid, cmdline)
    else:
        APP.config['logger'].critical(
            "got request to kill PID %s which doesnt look like ansible-playbook!!!",
            requestedpid)
    return redirect(BASEURL + "jobs")

@APP.route(BASEURL + "killall")
def killall():
    """equivalent to killall ansible-playbook."""
    killedprocs = anmad.process.killall()
    for proc in killedprocs:
        APP.config['logger'].warning(
            "KILLED process '%s' via killall", ' '.join(proc['cmdline']))
    return redirect(BASEURL + "jobs")

@APP.route(BASEURL + "otherplays")
def otherplaybooks():
    """Display other playbooks."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': VERSION,
        'extras': anmad.button_funcs.extraplays(
            APP.config['logger'],
            APP.config['playbook_root_dir'],
            APP.config['playbooks'])
        }
    APP.config['logger'].debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)

@APP.route(BASEURL + "clearqueues")
def clearqueues():
    """Clear redis queues."""
    APP.config['logger'].info("Clear redis queues requested.")
    APP.config['queues'].clear()
    APP.config['queues'].update_job_lists()
    return redirect(BASEURL)

@APP.route(BASEURL + "runall")
def runall():
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad.yaml.list_missing_files(
        APP.config['logger'],
        APP.config['prerun_list'])
    if problemfile:
        APP.config['logger'].info("Invalid files: %s", str(problemfile))
        return redirect(BASEURL)

    if APP.config['pre_run_playbooks'] is not None:
        for play in APP.config['prerun_list']:
            if [play] not in APP.config['queues'].prequeue_list:
                APP.config['logger'].info("Pre-Queueing %s", str(play))
                APP.config['queues'].prequeue_job(play)

    APP.config['logger'].info("Queueing %s", str(APP.config['run_list']))
    APP.config['queues'].queue_job(APP.config['run_list'])
    APP.config['queues'].update_job_lists()

    APP.config['logger'].debug("Redirecting to control page")
    return redirect(BASEURL)

@APP.route(BASEURL + 'playbooks/<path:playbook>')
def configuredplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    anmad.button_funcs.oneplaybook(
        APP.config['logger'],
        APP.config['queues'],
        playbook,
        anmad.button_funcs.buttonlist(
            APP.config['pre_run_playbooks'],
            APP.config['playbooks']),
        APP.config['playbook_root_dir'])
    APP.config['queues'].update_job_lists()
    APP.config['logger'].debug("Redirecting to control page")
    return redirect(BASEURL)

@APP.route(BASEURL + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad.button_funcs.oneplaybook(
        APP.config['logger'],
        APP.config['queues'],
        playbook,
        anmad.button_funcs.extraplays(
            APP.config['logger'], APP.config['playbook_root_dir'],
            APP.config['playbooks'], APP.config['pre_run_playbooks']),
        APP.config['playbook_root_dir'])
    APP.config['logger'].debug("Redirecting to others page")
    APP.config['queues'].update_job_lists()
    return redirect(BASEURL + 'otherplays')

@APP.route(BASEURL + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    APP.config['logger'].debug("Redirecting to ARA reports page")
    return redirect(APP.config['ara_url'])

@APP.route(BASEURL + "ansiblelog")
def ansiblelog():
    """Display ansible.log."""
    APP.config['logger'].debug("Displaying ansible.log")
    time_string = datetime.datetime.utcnow()
    if request.args.get('play') = 'list':
        return render_template('playbooklogs.html', **template_data)
    else:
        requestedlog = request.args.get('play')
        logfile = '/var/log/ansible/playbook/' + requestedlog
        text = open(logfile, 'r+')
        content = text.read()
        text.close()
        template_data = {
            'title' : 'ansible log for ' + requestedlog,
            'time': time_string,
            'version': VERSION,
            'log': requestedlog,
            'text': content
            }
        return render_template('ansiblelog.html', **template_data)

# Try accessing mod_wsgi process group, to see if we are running in wsgi.
try:
    PROCESS_NAME = mod_wsgi.process_group
    configure_app()
except AttributeError:
    pass

if __name__ == "__main__":
    configure_app()
    if not anmad.args.parse_args().dryrun:
        APP.run(host='0.0.0.0', port=9999, debug=True)
