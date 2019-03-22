#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
import os
import glob
from flask import Flask, render_template, redirect, abort

import anmad_args
import anmad_logging
import anmad_syntaxchecks
import anmad_queues

APP = Flask(__name__)
BASEURL = "/"
QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')

def buttonlist():
    """Get a list of allowed playbook buttons."""
    try:
        my_buttonlist = (anmad_args.ARGS.pre_run_playbooks +
                         anmad_args.ARGS.playbooks)
    except TypeError:
        my_buttonlist = (anmad_args.ARGS.playbooks)
    return my_buttonlist

def extraplays():
    """Get a list of yaml files in root dir that arent in buttonlist()."""
    yamlfiles = glob.glob(anmad_args.ARGS.playbook_root_dir + '/*.yaml')
    ymlfiles = glob.glob(anmad_args.ARGS.playbook_root_dir + '/*.yml')
    yamlfiles = yamlfiles + ymlfiles
    yamlbasenames = []
    for yml in yamlfiles:
        yamlbasenames.append(os.path.basename(yml))
    extraplaybooks = list(set(yamlbasenames) - set(buttonlist()))
    return extraplaybooks

def oneplaybook(playbook, playbooklist):
    """Queues one playbook, if its one of the configured ones."""
    if playbook not in playbooklist:
        anmad_logging.LOGGER.warning("API request for %s DENIED", playbook)
        abort(404)
    my_runlist = [anmad_args.ARGS.playbook_root_dir + '/' + playbook]
    QUEUES.queue_job(my_runlist)

@APP.route(BASEURL + 'playbooks/<path:playbook>')
def configuredplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    oneplaybook(playbook, buttonlist())
    anmad_logging.LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)

@APP.route(BASEURL + 'otherplaybooks/<path:playbook>')
def otherplaybook(playbook):
    """Runs one playbook, if its one of the other ones found by extraplays."""
    oneplaybook(playbook, extraplays())
    anmad_logging.LOGGER.debug("Redirecting to others page")
    return redirect(BASEURL + 'otherplays')

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    QUEUES.update_job_lists()
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'anmad',
        'time': time_string,
        'version': anmad_args.VERSION,
        'preq_message': QUEUES.prequeue_list,
        'queue_message': QUEUES.queue_list,
        'messages': QUEUES.info_list,
        'playbooks': anmad_args.ARGS.playbooks,
        'prerun': anmad_args.ARGS.pre_run_playbooks,
        }
    anmad_logging.LOGGER.debug("Rendering control page")
    return render_template('main.html',
                           **template_data)


@APP.route(BASEURL + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    anmad_logging.LOGGER.debug("Redirecting to ARA reports page")
    return redirect(anmad_args.ARGS.ara_url)


@APP.route(BASEURL + "log")
def log():
    """Display info queues."""
    QUEUES.update_job_lists()
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'anmad log',
        'time': time_string,
        'version': anmad_args.VERSION,
        'messages': QUEUES.info_list,
        }
    anmad_logging.LOGGER.info("Rendering log page")
    return render_template('log.html',
                           **template_data)

@APP.route(BASEURL + "otherplays")
def otherplaybooks():
    """Display other playbooks."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'anmad others',
        'time': time_string,
        'version': anmad_args.VERSION,
        'extras': extraplays()
        }
    anmad_logging.LOGGER.info("Rendering other playbooks page")
    return render_template('other.html',
                           **template_data)


@APP.route(BASEURL + "clearqueues")
def clearqueues():
    """Clear redis queues."""
    anmad_logging.LOGGER.info("Clear redis queues requested.")
    QUEUES.clear()
    return redirect(BASEURL)


@APP.route(BASEURL + "runall")
def runall():
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad_syntaxchecks.verify_files_exist()
    if problemfile:
        QUEUES.info.put([str(datetime.datetime.now()),
                         " Invalid files: " + str(problemfile)])
        return redirect(BASEURL)

    if anmad_args.ARGS.pre_run_playbooks is not None:
        for play in anmad_args.PRERUN_LIST:
            if [play] not in QUEUES.prequeue_list:
                QUEUES.prequeue_job(play)
    QUEUES.queue_job(anmad_args.RUN_LIST)
    anmad_logging.LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


if __name__ == "__main__" and not anmad_args.ARGS.dryrun:
    APP.run(host='0.0.0.0', port=9999, debug=True)
