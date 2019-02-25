#!/usr/bin/env python3
"""Control interface for ansible-logpoll."""
import datetime
from flask import Flask, render_template, redirect, abort

import anmad_args
import anmad_logging
import ansible_run

APP = Flask(__name__)
BASEURL = "/control/"

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'ansible-logpoll controls',
        'time': time_string
        }
    return render_template('main.html', playbooks=anmad_args.ARGS.playbooks, **template_data)

@APP.route(BASEURL + "runall/")
def runall():
    """Run all playbooks."""
    ansible_run.runplaybooks_async(anmad_args.ARGS.playbooks)
    return redirect(anmad_args.ARGS.ara_url)

#@APP.route(BASEURL + "stop/")
#def stopall():
#   subprocess.call(['./stop.sh'], shell=True)

@APP.route(BASEURL + 'playbooks/<path:playbook>')
def oneplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    if playbook not in anmad_args.ARGS.playbooks:
        abort(404)
    ansible_run.runplaybooks_async([playbook])
    return redirect(anmad_args.ARGS.ara_url)

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=9999, debug=True)
