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
        self.vault_password_file = vault_password_file

    def run_playbook(self, playbook, syncheck=False):
        """Run an ansible playbook, optionally in syntax check mode."""
        playbook = os.path.abspath(playbook)
        inventory = os.path.abspath(self.inventory)
        ansible_playbook_cmd = self.ansible_playbook_cmd
        ansible_playbook_cmd.extend(['--inventory', inventory, playbook])
        if self.vault_password_file is not None:
            ansible_playbook_cmd.extend(
            ['--vault-password-file', self.vault_password_file] )
        if syncheck:
            ansible_playbook_cmd.extend( ['--syntax-check'] )

        self.logger.info("Running %s", str(self.ansible_playbook_cmd))
        ret = subprocess.run(                                                  
            self.ansible_playbook_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        if 'WARNING' in (ret.stdout, ret.stderr):
            logger.warning("Warnings found in ansible output: %s %s",
                ret.stdout, ret.stderr)
        return ret
