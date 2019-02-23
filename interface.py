"""Control interface for ansible-logpoll."""
import os
import datetime
import argparse
from flask import Flask, render_template, request, redirect, abort
import threading

import constants
import ansible_run

APP = Flask(__name__)
BASEURL = "/control/"

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'ansible-logpoll controls',
        'time': time_string
        }
    return render_template('main.html', playbooks=constants.ARGS.playbooks, **template_data)

@APP.route(BASEURL + "runall/")
def runall():
    """Run all playbooks."""
    ansible_run.runplaybooks(constants.ARGS.playbooks)
    return redirect(constants.ARGS.ara_url)

#@APP.route(BASEURL + "stop/")
#def stopall():
#   subprocess.call(['./stop.sh'], shell=True)

@APP.route(BASEURL + 'playbooks/<playbook>')
def oneplaybook(playbook):
    """Runs one playbook, if its one of the configured ones."""
    if playbook not in constants.ARGS.playbooks:
        abort(403)
    ansible_run.run_one_playbook(playbook)
    return redirect(constants.ARGS.ara_url)

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=9999, debug=True)
