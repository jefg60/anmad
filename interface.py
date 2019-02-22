from flask import Flask, render_template
import os
import datetime
import time
import argparse

app = Flask(__name__)
baseurl = "/control/"
now = datetime.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--logdir",
    help="directory to write interface.log in",
    required=True
    )
args = parser.parse_args()

@app.route(baseurl)
def hello():
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
       'title' : 'ansible-logpoll controls',
       'time': timeString
       }
    return render_template('main.html', **templateData)

@app.route(baseurl + "run/")
def omx():
    my_logfile = args.logdir + '/interface.log'
    log_line = 'run button pushed at '+ str(now) + '\n'
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
