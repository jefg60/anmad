"""Initialize arguments for anmad."""
from shutil import which
from os import getcwd, cpu_count
from os.path import expanduser, dirname, abspath
import configargparse

import anmad.common.version as anmadver

def prepend_rootdir(myrootdir, mylist):
    """Prepends a path to each item in a list."""
    ret = [myrootdir + '/' + str(x) for x in mylist]
    return ret

def init_argparser():
    """Create an argument parser"""
    home = expanduser("~")
    default_configfile = '/etc/anmad.conf'
    alternate_configfile = home + '/.anmad.conf'
    __version__ = anmadver.VERSION

    parser = configargparse.ArgParser(
        default_config_files=[
            default_configfile,
            alternate_configfile
            ],
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter
        )
    output_dict = {
            "parser": parser,
            "home": home,
            "default_configfile": default_configfile,
            "alternate_configfile": alternate_configfile,
            "version": __version__,
            }
    return output_dict

def add_other_args(**config):
    """Args used by daemon AND interface."""
    group = config['parser'].add_argument_group(
            'Other')
    group.add_argument(
        "-v",
        "-V",
        "--version",
        action="version",
        version=config["version"]
        )
    group.add_argument(
        "-c",
        "--configfile",
        is_config_file=True,
        help="override default config files ("
            + config['default_configfile'] + ","
            + config['alternate_configfile'] + ")"
        )
    group.add_argument(
        "--aws-profile",
        default="default",
        help="AWS profile to use"
        )
    group.add_argument(
        "--playbooks",
        "-p",
        nargs='*',
        required=True,
        help="space separated list of ansible playbooks to run. "
        )
    group.add_argument(
        "--playbook-root-dir",
        help="base directory to run playbooks from",
        required=True,
        )
    group.add_argument(
        "--pre-run-playbooks",
        nargs='*',
        help="space separated list of ansible playbooks to run "
             "before doing any syntax checking. Useful "
             "for playbooks that fetch roles required by other playbooks"
        )

def add_logging_args(**config):
    """Add Logging args."""
    group = config['parser'].add_argument_group(
            'Logging')
    group.add_argument(
        "--no-syslog",
        dest="syslog",
        action="store_false",
        help="disable logging to syslog"
        )
    group.add_argument(
        "--syslogdevice",
        help="syslog device to use",
        default="/dev/log"
        )
    group.add_argument(
        "--cloudwatch",
        dest="cloudwatch",
        action="store_true",
        help="log to aws cloudwatch"
        )
    group.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="print debugging info to logs"
        )
    group.add_argument(
        "--ansible-log-path",
        help="path for ansible playbook logs",
        default="/var/log/ansible/playbook"
        )

def add_queue_args(**config):
    """Queue args."""
    group = config['parser'].add_argument_group(
            'Queues')
    group.add_argument(
        "--prerun-queue",
        help="Name for prerun queue",
        default="prerun-dev"
        )
    group.add_argument(
        "--playbook-queue",
        help="Name for playbook queue",
        default="playbooks-dev"
        )
    group.add_argument(
        "--info-queue",
        help="Name for info queue",
        default="info-dev"
        )

def add_daemon_args(**config):
    """Anmad daemon args."""
    try:
        ansible_home = dirname(
            dirname(which("ansible-playbook"))
        )
    except TypeError:
        ansible_home = getcwd()

    group = config['parser'].add_argument_group(
            'Daemon')
    group.add_argument(
        "--venv",
        help="python virtualenv to run ansible from",
        default=ansible_home
        )
    group.add_argument(
        "--ssh-id",
        help="ssh id file to use",
        default=config["home"] + "/.ssh/id_rsa"
        )
    group.add_argument(
        "--vault-password-file",
        help="vault password file",
        default=config["home"] + "/.vaultpw"
        )
    group.add_argument(
        "--syntax-check-dir",
        help="Optional directory to search for *.yml and *.yaml files to "
             "syntax check when changes are detected"
        )
    group.add_argument(
        "--inventories",
        "-i",
        nargs='*',
        required=True,
        help="space separated list of ansible inventories to syntax check "
             "against. The first inventory file "
             "will be the one that playbooks are run against if syntax "
             "checks pass"
        )
    group.add_argument(
        "--ssh-askpass",
        help="location of a script to pass as SSH_ASKPASS env var,"
             "which will enable this program to load an ssh key if "
             "it has a passphrase. Only works if not running in a terminal"
        )
    group.add_argument(
        "--concurrency",
        type=int,
        help="number of simultaneous processes to run,"
             "defaults to number of cpu reported by OS",
        default=cpu_count()
        )
    group.add_argument(
        "--timeout",
        help="timeout in seconds before aborting playbooks",
        default=1800
        )

def add_interface_args(**config):
    """Interface args."""
    group = config['parser'].add_argument_group(
            'Interface')
    group.add_argument(
        "--messagelist-size",
        help="number of messages to display on homepage",
        type=int,
        default=4
        )
    group.add_argument(
        "--git-pull",
        dest="gitpull",
        action="store_false",
        help="enable git pull functionality on playbook_root_dir"
        )
    group.add_argument(
        "--repo-deploykey",
        help="ssh private key file for git pull operations"
        )

def parse_anmad_args(daemon=False, interface=False):
    """Read arguments from command line or config file."""
    config = init_argparser()

    # groups that are used by both interface and daemon for now
    add_logging_args(**config)
    add_queue_args(**config)

    if daemon and interface:
        raise ValueError(
            "call parse_anmad_args with either daemon=True or interface=True, never both")
    if daemon:
        add_daemon_args(**config)
        debug_str = 'Daemon'
    elif interface:
        add_interface_args(**config)
        debug_str = 'Interface'
    else:
        debug_str = 'TEST'

    #another one used by daemon and interface, but put it after the specific ones
    add_other_args(**config)

    config['parser'].set_defaults(debug=False, syslog=True)

    myargs, unknown = config['parser'].parse_known_args()

    if len(unknown) > 0:
        print(f"ANMAD {debug_str}: Ignoring unknown args: {str(unknown)}")

    # filter list args to remove empty strings that may have been passed from
    # the config file (if we have parsed --inventories - not done for interface)
    if daemon:
        myargs.inventories = list(filter(None, myargs.inventories))
        # First inventory is the one that plays run against
        myargs.maininventory = abspath(myargs.inventories[0])
        myargs.ansible_playbook_cmd = myargs.venv + '/bin/ansible-playbook'

    myargs.playbooks = list(filter(None, myargs.playbooks))
    myargs.prerun_list = None

    if myargs.pre_run_playbooks:
        myargs.pre_run_playbooks = list(filter(None, myargs.pre_run_playbooks))
        myargs.prerun_list = prepend_rootdir(
            myargs.playbook_root_dir, myargs.pre_run_playbooks)

    myargs.run_list = prepend_rootdir(
        myargs.playbook_root_dir, myargs.playbooks)

    myargs.default_configfile = config["default_configfile"]
    myargs.alternate_configfile = config["alternate_configfile"]
    myargs.version = config["version"]

    return myargs
