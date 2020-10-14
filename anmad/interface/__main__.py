#!/usr/bin/env python3
"""Run dev test server."""
import anmad.interface.routes as anmadroutes
application = anmadroutes.flaskapp

if __name__ == "__main__":
    if not anmadroutes.config["args"].dryrun:
        application.run(host='0.0.0.0', port=9999, debug=True)
