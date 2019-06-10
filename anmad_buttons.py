#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
import mod_wsgi
from flask import Flask, render_template, redirect

import anmad_buttonfuncs
import anmad_queues
import anmad_version
import anmad_args
import anmad_logging
import anmad_yaml

APP = Flask(__name__)
BASEURL = "/"
VERSION = anmad_version.VERSION

def configure_app():
    """Fetch required args into config dict."""
    APP.config['ara_url'] = anmad_args.parse_args().ara_url
    APP.config['playbook_root_dir'] = anmad_args.parse_args().playbook_root_dir
    APP.config['playbooks'] = anmad_args.parse_args().playbooks
    APP.config['pre_run_playbooks'] = anmad_args.parse_args().pre_run_playbooks
    APP.config['prerun_list'] = anmad_args.parse_args().prerun_list
    APP.config['run_list'] = anmad_args.parse_args().run_list
    APP.config['logger'] = anmad_logging.logsetup()
    APP.config['queues'] = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    APP.config['queues'].update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': VERSION,
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


@APP.route(BASEURL + "otherplays")
def otherplaybooks():
    """Display other playbooks."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': VERSION,
        'extras': anmad_buttonfuncs.extraplays(
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
    problemfile = anmad_yaml.list_missing_files(APP.config['logger'], APP.config['prerun_list'])
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
    anmad_buttonfuncs.oneplaybook(
        APP.config['logger'],
        APP.config['queues'],
        playbook,
        anmad_buttonfuncs.buttonlist(APP.config['pre_run_playbooks'], APP.config['playbooks']),
        APP.config['playbook_root_dir'])
    APP.config['queues'].update_job_lists()
    APP.config['logger'].debug("Redirecting to control page")
    return redirect(BASEURL)


@APP.route(BASEURL + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad_buttonfuncs.oneplaybook(
        APP.config['logger'],
        APP.config['queues'],
        playbook,
        anmad_buttonfuncs.extraplays(
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

# Try accessing mod_wsgi process group, to see if we are running in wsgi.
try:
    PROCESS_NAME = mod_wsgi.process_group
    configure_app()
except AttributeError:
    pass

if __name__ == "__main__":
    configure_app()
    if not anmad_args.parse_args().dryrun:
        APP.run(host='0.0.0.0', port=9999, debug=True)
