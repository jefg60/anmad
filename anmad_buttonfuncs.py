#!/usr/bin/env python3
"""Functions for anmad_buttons."""

import os
from flask import abort

import anmad_yaml

def buttonlist(playbooks, prerun=None):
    """Get a list of allowed playbook buttons."""
    try:
        my_buttonlist = (prerun + playbooks)
    except TypeError:
        my_buttonlist = (playbooks)
    return my_buttonlist

def extraplays(logger, playbook_root_dir, playbooks, prerun=None):
    """Get a list of yaml files in root dir that arent in buttonlist()."""
    yamlfiles = anmad_yaml.find_yaml_files(logger, playbook_root_dir)
    yamlbasenames = []
    for yml in yamlfiles:
        yamlbasenames.append(os.path.basename(yml))
    if prerun is not None:
        my_buttonlist = buttonlist(playbooks)
    else:
        my_buttonlist = buttonlist(playbooks, prerun)
    extraplaybooks = list(set(yamlbasenames) - set(my_buttonlist))
    extraplaybooks.sort()
    return extraplaybooks

def oneplaybook(playbook, playbooklist, playbook_root_dir, logger, queues):
    """Queues one playbook, only if its in the playbooklist."""
    if playbook not in playbooklist:
        logger.warning("API request for %s DENIED", str(playbook))
        abort(404)
    my_runlist = [playbook_root_dir + '/' + playbook]
    logger.info("Queueing %s", str(my_runlist))
    queues.queue_job(my_runlist)
