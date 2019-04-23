"""Initialize anmad."""
import logging
import logging.handlers
import os
import mod_wsgi
import __main__ as main

import anmad_args
import anmad_queues

class AnmadInfoHandler(logging.handlers.QueueHandler):
    """Override QueueHandler enqueue method to work with hotqueue."""

    def enqueue(self, record):
        self.queue.put(record.message)


try:
    PROCESS_NAME = mod_wsgi.process_group
except AttributeError:
    PROCESS_NAME = os.path.basename(main.__file__)


LOGGER = logging.getLogger(PROCESS_NAME)
QUEUES = anmad_queues.AnmadQueues('prerun', 'playbooks', 'info')
ARGS = anmad_args.ARGS
VERSION = anmad_args.VERSION
DEFAULT_CONFIGFILE = anmad_args.DEFAULT_CONFIGFILE
ANSIBLE_PLAYBOOK_CMD = anmad_args.ANSIBLE_PLAYBOOK_CMD
MAININVENTORY = anmad_args.MAININVENTORY
PRERUN_LIST = anmad_args.PRERUN_LIST
RUN_LIST = anmad_args.RUN_LIST

SYSLOG_FORMATTER = logging.Formatter(
    '%(name)s - [%(levelname)s] - %(message)s')
TIMED_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

QUEUE_HANDLER = AnmadInfoHandler(QUEUES.info)
QUEUE_HANDLER.setFormatter(TIMED_FORMATTER)

LOGGER.addHandler(QUEUE_HANDLER)
LOGGER.level = logging.INFO

# create sysloghandler if needed (default true)
if ARGS.syslog:
    SYSLOGHANDLER = logging.handlers.SysLogHandler(
        address=ARGS.syslogdevice,
        facility='local3')
    SYSLOGHANDLER.setFormatter(SYSLOG_FORMATTER)
    LOGGER.addHandler(SYSLOGHANDLER)

# create consolehandler if debug mode
if ARGS.debug:
    CONSOLEHANDLER = logging.StreamHandler()
    CONSOLEHANDLER.setFormatter(TIMED_FORMATTER)
    logging.getLogger().addHandler(CONSOLEHANDLER)
    LOGGER.level = logging.DEBUG

def startup():
    LOGGER.info("Version: %s startup", str(VERSION))
    LOGGER.debug("config file: %s",
                 str(ARGS.configfile)
                 if ARGS.configfile is not None
                 else str(DEFAULT_CONFIGFILE))
    LOGGER.debug("vault password file: %s", str(ARGS.vault_password_file))
    LOGGER.debug("ssh id: %s", str(ARGS.ssh_id))
    LOGGER.debug("venv: %s", str(ARGS.venv))
    LOGGER.debug("ansible_playbook_cmd: %s", str(ANSIBLE_PLAYBOOK_CMD))
    LOGGER.debug("inventorylist: %s", " ".join(ARGS.inventories))
    LOGGER.debug("maininventory: %s", str(MAININVENTORY))
    if ARGS.pre_run_playbooks:
        LOGGER.debug("pre_run_playbooks: %s",
                     " ".join(ARGS.pre_run_playbooks))
        LOGGER.debug("PRERUN_LIST: %s",
                     " ".join(PRERUN_LIST))
    LOGGER.debug("playbooks: %s", " ".join(ARGS.playbooks))
    LOGGER.debug("RUN_LIST: %s", " ".join(RUN_LIST))
    LOGGER.debug("playbook_root_dir: %s", str(ARGS.playbook_root_dir))

if __name__ == "__main__":
    startup()
