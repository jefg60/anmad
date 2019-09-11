"""anmad process functions."""
import fnmatch
import psutil

def get_ansible_playbook_procs():
    """Get list of processes that match *ansible-playbook."""
    proclist = [p.info for p in
                psutil.process_iter(attrs=['pid', 'name', 'cmdline'])
                if fnmatch.filter(p.info['cmdline'], '*ansible-playbook*')]
    return proclist

def kill(pid):
    """Kill ONE ansible-playbook process by pid."""
    process = psutil.Process(pid)
    process.kill()

def killall():
    """Killall ansible-playbook."""
    proclist = get_ansible_playbook_procs()
    pids = [li['pid'] for li in proclist]
    for pid in pids:
        kill(pid)
    return pids
