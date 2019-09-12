"""anmad process functions."""
import fnmatch
import psutil

def get_ansible_playbook_procs(cmdline_search='ansible-playbook'):
    """Get list of processes that match *ansible-playbook."""
    proclist = [p.info for p in
                psutil.process_iter(attrs=['pid', 'name', 'cmdline'])
                if fnmatch.filter(p.info['cmdline'], '*' + cmdline_search + '*')]
    return proclist

def kill(pid):
    """Kill ONE ansible-playbook process by pid."""
    process = psutil.Process(pid)
    process.kill()

def killall(**kwargs):
    """Killall ansible-playbook."""
    playtokill = kwargs.get('playtokill', 'ansible-playbook')
    proclist = get_ansible_playbook_procs(cmdline_search=playtokill)
    pids = [li['pid'] for li in proclist]
    for pid in pids:
        kill(pid)
    return proclist
