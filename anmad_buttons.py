#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
from flask import Flask, render_template, redirect, abort

import anmad_args
import anmad_logging
import anmad_syntaxchecks
import anmad_queues

APP = Flask(__name__)
BASEURL = "/"
QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks')

try:
    BUTTONLIST = (anmad_args.ARGS.pre_run_playbooks +
                  anmad_args.ARGS.playbooks)
except TypeError:
    BUTTONLIST = (anmad_args.ARGS.playbooks)


@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'anmad controls',
        'time': time_string,
        'version': anmad_args.VERSION,
        'preq_message': QUEUES.prequeue_message,
        'queue_message': QUEUES.queue_message
        }
    anmad_logging.LOGGER.debug("Rendering control page")
    return render_template('main.html',
                           playbooks=BUTTONLIST,
                           **template_data)
    return mainpage()


@APP.route(BASEURL + "ara")
def ara_redirect():
    """Redirect to ARA reports page."""
    anmad_logging.LOGGER.debug("Redirecting to ARA reports page")
    return redirect(anmad_args.ARGS.ara_url)


@APP.route(BASEURL + "runall")
def runall():
    """Run all playbooks after verifying that files exist."""
    problemfile = anmad_syntaxchecks.verify_files_exist()
    verify_msg = ("YAML error with: " + str(problemfile))
    if problemfile:
        return mainpage(verify_msg)

    if anmad_args.ARGS.pre_run_playbooks is not None:
        for play in anmad_args.PRERUN_LIST:
            QUEUES.prequeue_job(play)
    QUEUES.queue_job(anmad_args.RUN_LIST)
    anmad_logging.LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


#@APP.route(BASEURL + "stop/")
#def stopall():
#   subprocess.call(['./stop.sh'], shell=True)


@APP.route(BASEURL + 'playbooks/<path:playbook>')
def oneplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    if playbook not in BUTTONLIST:
        anmad_logging.LOGGER.warning("API request for %s DENIED", playbook)
        abort(404)
    my_runlist = [anmad_args.ARGS.playbook_root_dir + '/' + playbook]
    anmad_logging.LOGGER.info("Queuing %s", my_runlist)
    QUEUES.queue_job(my_runlist)
    anmad_logging.LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)


if __name__ == "__main__" and not anmad_args.ARGS.dryrun:
    APP.run(host='0.0.0.0', port=9999, debug=True)
