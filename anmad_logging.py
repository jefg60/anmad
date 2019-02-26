"""Initialize logging for anmad."""
import logging
import logging.handlers
import __main__ as main

import anmad_args

# Setup Logging globally with no handlers to begin with
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s]  %(message)s",
    handlers=[]
    )

LOGGER = logging.getLogger(os.path.basename(main.__file__))
FORMATTER = logging.Formatter(
    '%(name)s - [%(levelname)s] - %(message)s')

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

# log main arguments used
LOGGER.info("config file: %s",
            anmad_args.ARGS.configfile
            if anmad_args.ARGS.configfile is not None
            else anmad_args.DEFAULT_CONFIGFILE)
LOGGER.info("vault password file: %s", anmad_args.ARGS.vault_password_file)
LOGGER.info("ssh id: %s", anmad_args.ARGS.ssh_id)
LOGGER.info("venv: %s", anmad_args.ARGS.venv)
LOGGER.info("ansible_playbook_cmd: %s", anmad_args.ANSIBLE_PLAYBOOK_CMD)
LOGGER.info("dir_to_watch: %s", anmad_args.ARGS.dir_to_watch)
LOGGER.info("inventorylist: %s", " ".join(anmad_args.ARGS.inventories))
LOGGER.info("maininventory: %s", anmad_args.MAININVENTORY)
if anmad_args.ARGS.pre_run_playbooks:
    LOGGER.info("pre_run_playbooks: %s",
                " ".join(anmad_args.ARGS.pre_run_playbooks))
LOGGER.info("playbooks: %s", " ".join(anmad_args.ARGS.playbooks))
LOGGER.info("interval: %s", str(anmad_args.ARGS.interval))
