#!/usr/bin/env python3
import anmad.buttons
application = anmad.buttons.app.flaskapp

if __name__ == "__main__":
    if not anmad.args.parse_args().dryrun:
        application.run(host='0.0.0.0', port=9999, debug=True)
