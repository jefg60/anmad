#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
import os
import mod_wsgi
from flask import Flask, render_template, redirect
import __main__ as main

import anmad_buttonfuncs
import anmad_queues
import anmad_version
import anmad_args
import anmad_logging
import anmad_yaml

APP = Flask(__name__)
BASEURL = "/"
VERSION = anmad_version.VERSION

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    QUEUES.update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': VERSION,
        'preq_message': QUEUES.prequeue_list,
        'queue_message': QUEUES.queue_list,
        'messages': QUEUES.info_list[0:3],
        'playbooks': ARGS['playbooks'],
        'prerun': ARGS['pre_run_playbooks'],
        }
    LOGGER.debug("Rendering control page")
    return render_template('main.html',
                           **template_data)


@APP.route(BASEURL + "log")
def log():
    """Display info queues."""
    QUEUES.update_job_lists()
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad log',
        'time': time_string,
        'version': VERSION,
        'messages': QUEUES.info_list,
        }
    LOGGER.debug("Rendering log page")
    return render_template('log.html', **template_data)


@APP.route(BASEURL + "otherplays")
def otherplaybooks():
    """Display other playbooks."""
    time_string = datetime.datetime.utcnow()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': VERSION,
        'extras': anmad_buttonfuncs.extraplays(LOGGER, ARGS['playbook_root_dir'], ARGS['playbooks'])
        }
    LOGGER.debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)


@APP.route(BASEURL + "clearqueues")
def clearqueues():
    """Clear redis queues."""
    LOGGER.info("Clear redis queues requested.")
    QUEUES.clear()
    QUEUES.update_job_lists()
    return redirect(BASEURL)


@APP.route(BASEURL + "runall")
def runall():
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad_yaml.list_missing_files(LOGGER, ARGS['prerun_list'])
    if problemfile:
        LOGGER.info("Invalid files: %s", str(problemfile))
        return redirect(BASEURL)

    if ARGS['pre_run_playbooks'] is not None:
        for play in ARGS['prerun_list']:
            if [play] not in QUEUES.prequeue_list:
                LOGGER.info("Pre-Queueing %s", str(play))
                QUEUES.prequeue_job(play)

    LOGGER.info("Queueing %s", str(ARGS['run_list']))
    QUEUES.queue_job(ARGS['run_list'])
    QUEUES.update_job_lists()

    LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


@APP.route(BASEURL + 'playbooks/<path:playbook>')
def configuredplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    anmad_buttonfuncs.oneplaybook(
        LOGGER,
        QUEUES,
        playbook,
        anmad_buttonfuncs.buttonlist(ARGS['pre_run_playbooks'], ARGS['playbooks']),
        ARGS['playbook_root_dir'])
    QUEUES.update_job_lists()
    LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


@APP.route(BASEURL + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad_buttonfuncs.oneplaybook(
        LOGGER,
        QUEUES,
        playbook,
        anmad_buttonfuncs.extraplays(
            LOGGER, ARGS['playbook_root_dir'],
            ARGS['playbooks'], ARGS['pre_run_playbooks']),
        ARGS['playbook_root_dir'])
    LOGGER.debug("Redirecting to others page")
    return redirect(BASEURL + 'otherplays')


@APP.route(BASEURL + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    LOGGER.debug("Redirecting to ARA reports page")
    return redirect(ARGS['ara_url'])

# Try accessing mod_wsgi process group, to see if we are running in wsgi.
try:
    PROCESS_NAME = mod_wsgi.process_group
except AttributeError:
    PROCESS_NAME = os.path.basename(main.__file__)

# if wsgi process or cmd line run, set constants
if PROCESS_NAME != os.path.basename(main.__file__) or __name__ == "__main__":
    ARGS = {
        'ara_url': anmad_args.parse_args().ara_url,
        'playbook_root_dir': anmad_args.parse_args().playbook_root_dir,
        'playbooks': anmad_args.parse_args().playbooks,
        'pre_run_playbooks': anmad_args.parse_args().pre_run_playbooks,
        'prerun_list': anmad_args.parse_args().prerun_list,
        'run_list': anmad_args.parse_args().run_list}
    LOGGER = anmad_logging.logsetup()
    QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')

if __name__ == "__main__":
    if not anmad_args.parse_args().dryrun:
        APP.run(host='0.0.0.0', port=9999, debug=True)
