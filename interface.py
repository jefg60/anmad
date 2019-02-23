"""Control interface for ansible-logpoll."""
import os
import datetime
import argparse
from flask import Flask, render_template

APP = Flask(__name__)
BASEURL = "/control/"

PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    "--logdir",
    help="directory to write interface.log in",
    required=True
    )
PARSER.add_argument(
    "--playbooks",
    "-p",
    nargs='*',
    required=True,
    help="space separated list of ansible playbooks to run. "
    )
ARGS = PARSER.parse_args()

@APP.route(BASEURL)
def mainpage():
    """Render main page."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'ansible-logpoll controls',
        'time': time_string
        }
    return render_template('main.html', playbooks=ARGS.playbooks, **template_data)

@APP.route(BASEURL + "runall/")
def runall():
    """Run all playbooks."""
    my_logfile = ARGS.logdir + '/interface.log'
    log_line = 'run button pushed at '+ str(datetime.datetime.now()) + '\n'
    if os.path.exists(my_logfile):
        append_write = 'a'
    else:
        append_write = 'w'

    filehandle = open(my_logfile, append_write)
    filehandle.write(log_line)
    filehandle.close()
    return log_line

#@APP.route(BASEURL + "stop/")
#def omxstop():
#   subprocess.call(['./stop.sh'], shell=True)

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=9999, debug=True)
