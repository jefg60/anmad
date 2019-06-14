"""Initialize anmad."""
import logging
import logging.handlers

import anmad.args
import anmad.queues

class AnmadInfoHandler(logging.handlers.QueueHandler):
    """Override QueueHandler enqueue method to work with hotqueue."""

    def enqueue(self, record):
        self.queue.put(record.message)

def logsetup():
    """Set up anmad logging."""
    args = anmad.args.parse_args()
    logger = logging.getLogger(args.process_name)
    queues = anmad.queues.AnmadQueues('prerun', 'playbooks', 'info')

    syslog_formatter = logging.Formatter(
        '%(name)s - [%(levelname)s] - %(message)s')
    timed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

    queue_handler = AnmadInfoHandler(queues.info)
    queue_handler.setFormatter(timed_formatter)
    queue_handler.setLevel(logging.INFO)

    logger.addHandler(queue_handler)
    logger.level = logging.INFO

    # create sysloghandler if needed (default true)
    if args.syslog:
        sysloghandler = logging.handlers.SysLogHandler(
            address=args.syslogdevice,
            facility='local3')
        sysloghandler.setFormatter(syslog_formatter)
        logger.addHandler(sysloghandler)

    # create consolehandler if debug mode
    if args.debug:
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(timed_formatter)
        logger.addHandler(consolehandler)
        logger.level = logging.DEBUG

    return logger
