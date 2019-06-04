#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
import os
from flask import Flask, render_template, redirect, abort

import anmad_button_funcs

APP = Flask(__name__)
BASEURL = "/"
QUEUES = anmad_yaml.QUEUES
ARGS = anmad_yaml.ARGS
VERSION = anmad_yaml.VERSION
PRERUN_LIST = anmad_yaml.PRERUN_LIST
RUN_LIST = anmad_yaml.RUN_LIST
LOGGER = anmad_yaml.LOGGER

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
        'playbooks': ARGS.playbooks,
        'prerun': ARGS.pre_run_playbooks,
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
        'extras': anmad_button_funcs.extraplays()
        }
    LOGGER.debug("Rendering other playbooks page")
    return render_template('other.html', **template_data)


@APP.route(BASEURL + "clearqueues")
def clearqueues():
    """Clear redis queues."""
    LOGGER.info("Clear redis queues requested.")
    QUEUES.clear()
    return redirect(BASEURL)


@APP.route(BASEURL + "runall")
def runall():
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad_yaml.verify_files_exist()
    if problemfile:
        LOGGER.info("Invalid files: %s", str(problemfile))
        return redirect(BASEURL)

    if ARGS.pre_run_playbooks is not None:
        for play in PRERUN_LIST:
            if [play] not in QUEUES.prequeue_list:
                LOGGER.info("Pre-Queueing %s", str(play))
                QUEUES.prequeue_job(play)

    LOGGER.info("Queueing %s", str(RUN_LIST))
    QUEUES.queue_job(RUN_LIST)

    LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


@APP.route(BASEURL + 'playbooks/<path:playbook>')
def configuredplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    anmad_button_funcs.oneplaybook(playbook, anmad_button_funcs.buttonlist(ARGS.pre_run_playbooks, ARGS.playbooks))
    LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


@APP.route(BASEURL + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    anmad_button_funcs.oneplaybook(playbook, anmad_button_funcs.extraplays())
    LOGGER.debug("Redirecting to others page")
    return redirect(BASEURL + 'otherplays')


@APP.route(BASEURL + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    LOGGER.debug("Redirecting to ARA reports page")
    return redirect(ARGS.ara_url)


if __name__ == "__main__" and not ARGS.dryrun:
    APP.run(host='0.0.0.0', port=9999, debug=True)
