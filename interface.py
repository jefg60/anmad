"""Control interface for ansible-logpoll."""
import os
import datetime
import argparse
from flask import Flask, render_template, request, redirect
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
    thread = threading.Thread(target=ansible_run.runplaybooks, args=([constants.ARGS.playbooks]))
    thread.start()
    return render_template('waiting.html')

#@APP.route(BASEURL + "stop/")
#def omxstop():
#   subprocess.call(['./stop.sh'], shell=True)

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=9999, debug=True)
