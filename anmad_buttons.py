#!/usr/bin/env python3
"""Control interface for anmad."""
import datetime
from flask import Flask, render_template, redirect, abort
from hotqueue import HotQueue

import anmad_args
import anmad_logging

APP = Flask(__name__)
BASEURL = "/control/"
Q = HotQueue('playbooks')

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'anmad controls',
        'time': time_string
        }
    anmad_logging.LOGGER.debug("Rendering control page")
    return render_template('main.html',
                           playbooks=anmad_args.ARGS.playbooks,
                           **template_data)

@APP.route(BASEURL + "ara/")
def ara_redirect():
    """Redirect to ARA reports page."""
    anmad_logging.LOGGER.debug("Redirecting to ARA reports page")
    return redirect(anmad_args.ARGS.ara_url)

@APP.route(BASEURL + "runall/")
def runall():
    """Run all playbooks."""
    anmad_logging.LOGGER.info("Queuing %s", anmad_args.ARGS.playbooks)
    Q.put(anmad_args.ARGS.playbooks)
    anmad_logging.LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)

#@APP.route(BASEURL + "stop/")
#def stopall():
#   subprocess.call(['./stop.sh'], shell=True)

@APP.route(BASEURL + 'playbooks/<path:playbook>')
def oneplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    if playbook not in anmad_args.ARGS.playbooks:
        anmad_logging.LOGGER.warning("API request for %s DENIED", playbook)
        abort(404)
    anmad_logging.LOGGER.info("Queuing %s", [playbook])
    Q.put([playbook])
    anmad_logging.LOGGER.debug("Redirecting to control page")
    return redirect(BASEURL)

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=9999, debug=True)
