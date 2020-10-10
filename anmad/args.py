"""Initialize arguments for anmad."""
import shutil
import os
from os.path import expanduser
import configargparse

import anmad.version

def prepend_rootdir(myrootdir, mylist):
    """Prepends a path to each item in a list."""
    ret = [myrootdir + '/' + str(x) for x in mylist]
    return ret

def parse_args():
    """Read arguments from command line or config file."""

    home = expanduser("~")
    default_configfile = '/etc/anmad.conf'
    alternate_configfile = home + '/.anmad.conf'
    __version__ = anmad.version.VERSION

    try:
        ansible_home = os.path.dirname(
            os.path.dirname(shutil.which("ansible-playbook"))
        )
    except TypeError:
        ansible_home = os.getcwd()

    parser = configargparse.ArgParser(
        default_config_files=[
            default_configfile,
            alternate_configfile
            ]
        )

    parser.add_argument(
        "-v",
        "-V",
        "--version",
        action="version",
        version=__version__
        )
    parser.add_argument(
        "-c",
        "--configfile",
        is_config_file=True,
        help="override default config file " + default_configfile
        )
    parser.add_argument(
        "--venv",
        help="python virtualenv to run ansible from",
        default=ansible_home
        )
    parser.add_argument(
        "--ssh_id",
        help="ssh id file to use, default ~/.ssh/id_rsa",
        default=home + "/.ssh/id_rsa"
        )
    parser.add_argument(
        "--vault_password_file",
        help="vault password file, default ~/.vaultpw",
        default=home + "/.vaultpw"
        )
    parser.add_argument(
        "--syntax_check_dir",
        help="Optional directory to search for *.yml and *.yaml files to "
             "syntax check when changes are detected"
        )
    parser.add_argument(
        "--playbooks",
        "-p",
        nargs='*',
        required=True,
        help="space separated list of ansible playbooks to run. "
        )
    parser.add_argument(
        "--playbook_root_dir",
        help="base directory to run playbooks from",
        required=True,
        )
    parser.add_argument(
        "--pre_run_playbooks",
        nargs='*',
        help="space separated list of ansible playbooks to run "
             "before doing any syntax checking. Useful "
             "for playbooks that fetch roles required by other playbooks"
        )
    parser.add_argument(
        "--inventories",
        "-i",
        nargs='*',
        required=True,
        help="space separated list of ansible inventories to syntax check "
             "against. The first inventory file "
             "will be the one that playbooks are run against if syntax "
             "checks pass"
        )
    parser.add_argument(
        "--ssh_askpass",
        help="location of a script to pass as SSH_ASKPASS env var,"
             "which will enable this program to load an ssh key if "
             "it has a passphrase. Only works if not running in a terminal"
        )
    parser.add_argument(
        "--no-syslog",
        dest="syslog",
        action="store_false",
        help="disable logging to syslog"
        )
    parser.add_argument(
        "--syslogdevice",
        help="syslog device to use",
        default="/dev/log"
        )
    parser.add_argument(
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="only wait for one --interval, for testing"
        )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="print debugging info to logs"
        )
    parser.add_argument(
        "--concurrency",
        type=int,
        help="number of simultaneous processes to run,"
             "defaults to number of cpu reported by OS",
        default=os.cpu_count()
        )
    parser.add_argument(
        "--ara_url",
        help="ARA URL to display after starting jobs",
        default='http://ara/'
        )
    parser.add_argument(
        "--timeout",
        help="timeout in seconds before aborting playbooks",
        default=1800
        )

    parser.set_defaults(debug=False, syslog=True, dryrun=False)
    myargs, unknown = parser.parse_known_args()
    if len(unknown) > 0:
        print('Ignoring unknown args: ' + str(unknown))
    # filter list args to remove empty strings that may have been passed from
    # the config file
    myargs.inventories = list(filter(None, myargs.inventories))
    myargs.playbooks = list(filter(None, myargs.playbooks))
    myargs.prerun_list = None

    if myargs.pre_run_playbooks:
        myargs.pre_run_playbooks = list(filter(None, myargs.pre_run_playbooks))
        myargs.prerun_list = prepend_rootdir(
            myargs.playbook_root_dir, myargs.pre_run_playbooks)

    myargs.run_list = prepend_rootdir(
        myargs.playbook_root_dir, myargs.playbooks)

    # First inventory is the one that plays run against
    myargs.maininventory = os.path.abspath(myargs.inventories[0])
    myargs.process_name = 'anmad'
    myargs.ansible_playbook_cmd = myargs.venv + '/bin/ansible-playbook'
    myargs.default_configfile = default_configfile
    myargs.version = __version__

    return myargs
