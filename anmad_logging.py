"""Initialize logging for anmad."""
import logging
import logging.handlers
import os
import mod_wsgi
import __main__ as main

import anmad_args
import anmad_queues

try:
    PROCESS_NAME = mod_wsgi.process_group
except AttributeError:
    PROCESS_NAME = os.path.basename(main.__file__)

class AnmadInfoHandler(logging.handlers.QueueHandler):
    """Override QueueHandler enqueue method to work with hotqueue."""

    def enqueue(self, record):
        self.queue.put(record.message)

# Setup Logging globally with no handlers to begin with
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s]  %(message)s",
    handlers=[]
    )

LOGGER = logging.getLogger(PROCESS_NAME)
FORMATTER = logging.Formatter(
    '%(name)s - [%(levelname)s] - %(message)s')
BUI_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')
QUEUE_HANDLER = AnmadInfoHandler(QUEUES.info)
QUEUE_HANDLER.setFormatter(BUI_FORMATTER)
LOGGER.addHandler(QUEUE_HANDLER)

# create sysloghandler if needed (default true)
if anmad_args.ARGS.syslog:
    SYSLOGHANDLER = logging.handlers.SysLogHandler(
        address=anmad_args.ARGS.syslogdevice,
        facility='local3')
    SYSLOGHANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(SYSLOGHANDLER)
    LOGGER.level = logging.INFO

# create consolehandler if debug mode
if anmad_args.ARGS.debug:
    CONSOLEHANDLER = logging.StreamHandler()
    CONSOLEHANDLER.setFormatter(FORMATTER)
    logging.getLogger().addHandler(CONSOLEHANDLER)
    LOGGER.level = logging.DEBUG

# create queuehandler

# log main arguments used
LOGGER.info("Version: %s", anmad_args.VERSION)
LOGGER.debug("config file: %s",
             anmad_args.ARGS.configfile
             if anmad_args.ARGS.configfile is not None
             else anmad_args.DEFAULT_CONFIGFILE)
LOGGER.debug("vault password file: %s", anmad_args.ARGS.vault_password_file)
LOGGER.debug("ssh id: %s", anmad_args.ARGS.ssh_id)
LOGGER.debug("venv: %s", anmad_args.ARGS.venv)
LOGGER.debug("ansible_playbook_cmd: %s", anmad_args.ANSIBLE_PLAYBOOK_CMD)
LOGGER.debug("inventorylist: %s", " ".join(anmad_args.ARGS.inventories))
LOGGER.debug("maininventory: %s", anmad_args.MAININVENTORY)
if anmad_args.ARGS.pre_run_playbooks:
    LOGGER.debug("pre_run_playbooks: %s",
                 " ".join(anmad_args.ARGS.pre_run_playbooks))
    LOGGER.debug("PRERUN_LIST: %s",
                 " ".join(anmad_args.PRERUN_LIST))
LOGGER.debug("playbooks: %s", " ".join(anmad_args.ARGS.playbooks))
LOGGER.debug("RUN_LIST: %s", " ".join(anmad_args.RUN_LIST))
LOGGER.debug("playbook_root_dir: %s", anmad_args.ARGS.playbook_root_dir)
