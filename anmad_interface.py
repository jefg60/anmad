#!/usr/bin/env python3
"""Run dev test server."""
import anmad.routes
application = anmad.routes.flaskapp

if __name__ == "__main__":
    if not anmad.routes.config["args"].dryrun:
        application.run(host='0.0.0.0', port=9999, debug=True)
