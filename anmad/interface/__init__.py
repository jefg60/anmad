#!/usr/bin/env python3
"""flaskapp as application object."""
import sys
import anmad.interface.routes as anmadroutes

def main():
    """Normal entry point."""
    application = anmadroutes.flaskapp
    return application

# Gunicorn entry point generator
def app(**kwargs):
    """Gunicorn entry point."""
    # Gunicorn CLI args are useless.
    # https://stackoverflow.com/questions/8495367/
    #
    # Start the application in modified environment.
    # https://stackoverflow.com/questions/18668947/
    #
    sys.argv = ['--gunicorn']
    for k in kwargs:
        sys.argv.append("--" + k)
        sys.argv.append(kwargs[k])
    return main()
