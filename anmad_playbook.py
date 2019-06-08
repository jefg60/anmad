"""Functions to run ansible playbooks."""                              
import os                                                                      
import subprocess

class ansibleRun:
    """Ansible-playbook operations class."""
    def __init__(self,                                                         
            logger,                                                            
            inventory,                                                         
            ansible_playbook_cmd,                                              
            vault_password_file=None):                                         
        """Init SyntaxCheckWorker."""                                          
        self.logger = logger                                                   
        self.inventory = inventory                                             
        self.ansible_playbook_cmd = [ansible_playbook_cmd]
        if vault_password_file is not None:
            self.ansible_playbook_cmd.extend(
            ['--vault-password-file', vault_password_file] )

    def run_playbook(self, playbook, syncheck=False, checkmode=False):
        """Run an ansible playbook, optionally in syntax check mode or
        with --check --diff"""
        playbook = os.path.abspath(playbook)
        inventory = os.path.abspath(self.inventory)
        ansible_playbook_cmd = self.ansible_playbook_cmd
        if syncheck:
            ansible_playbook_cmd.extend( ['--syntax-check'] )
        if checkmode:
            ansible_playbook_cmd.extend( ['--check', '--diff'] )
        ansible_playbook_cmd.extend(['--inventory', inventory, playbook])

        self.logger.info("Running %s", str(ansible_playbook_cmd))
        ret = subprocess.run(                                                  
            ansible_playbook_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        if 'WARNING' in (ret.stdout, ret.stderr):
            logger.warning("Warnings found in ansible output: %s %s",
                ret.stdout, ret.stderr)
        return ret
