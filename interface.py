"""Control interface for ansible-logpoll."""
import os
import datetime
import argparse
from flask import Flask, render_template

app = Flask(__name__)
baseurl = "/control/"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--logdir",
    help="directory to write interface.log in",
    required=True
    )
parser.add_argument(
    "--playbooks",
    "-p",
    nargs='*',
    required=True,
    help="space separated list of ansible playbooks to run. "
    )
ARGS = parser.parse_args()

@app.route(baseurl)
def mainpage():
    """Render main page."""
    time_string = datetime.datetime.now()
    template_data = {
        'title' : 'ansible-logpoll controls',
        'time': time_string
        }
    return render_template('main.html', playbooks=ARGS.playbooks, **template_data)

@app.route(baseurl + "runall/")
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

#@app.route(baseurl + "stop/")
#def omxstop():
#   subprocess.call(['./stop.sh'], shell=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999, debug=True)
