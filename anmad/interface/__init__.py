#!/usr/bin/env python3
"""flaskapp as application object."""

def main():
    import anmad.interface.routes as anmadroutes
    application = anmadroutes.flaskapp
    return application

# Gunicorn entry point generator
def app(*args, **kwargs):
    # Gunicorn CLI args are useless.
    # https://stackoverflow.com/questions/8495367/
    #
    # Start the application in modified environment.
    # https://stackoverflow.com/questions/18668947/
    #
    import sys
    sys.argv = ['--gunicorn']
    for k in kwargs:
        sys.argv.append("--" + k)
        sys.argv.append(kwargs[k])
    return main()
