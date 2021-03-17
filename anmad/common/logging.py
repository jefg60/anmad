"""Initialize anmad."""
import logging
import logging.handlers

import watchtower
import boto3

import anmad.common.queues as anmadqueues

class AnmadInfoHandler(logging.handlers.QueueHandler):
    """Override QueueHandler enqueue method to work with hotqueue."""

    def enqueue(self, record):
        self.queue.put(record.message)

def logsetup(args, name):
    """Set up anmad logging."""
    logger = logging.getLogger(name)
    queues = anmadqueues.AnmadQueues(
        args.prerun_queue,
        args.playbook_queue,
        args.info_queue)

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

    if args.cloudwatch:
        prefix = "anmad"
        group_name = f"{prefix}-{args.cloudwatch_log_group}"
        stream_name = f"{prefix}-{args.cloudwatch_stream}"

        session = boto3.Session(
            profile_name = args.aws_profile,
            region_name = args.aws_region
            )

        logger.addHandler(
            watchtower.CloudWatchLogHandler(
                boto3_session = session,
                log_group = group_name,
                stream_name = stream_name,
                )
            )

    # create consolehandler if debug mode
    if args.debug:
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(timed_formatter)
        logger.addHandler(consolehandler)
        logger.level = logging.DEBUG

    return logger
