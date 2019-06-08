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
        self.ansible_playbook_cmd = ansible_playbook_cmd                       
        self.vault_password_file = vault_password_file

    def run_playbook(self, playbook, syncheck=False):
        """Run an ansible playbook, optionally in syntax check mode."""
        playbook = os.path.abspath(playbook)
        inventory = os.path.abspath(self.inventory)
        ansible_playbook_args = ('--inventory ' + self.inventory + ' ' +
            playbook )
        if self.vault_password_file is not None:
            ansible_playbook_args = ( ansible_playbook_args +
            ' --vault-password-file ' + self.vault_password_file )
        if syncheck:
            ansible_playbook_args = ( ansible_playbook_args +
            ' --syntax-check ' )

        print("Running ", str(self.ansible_playbook_cmd),
            str(ansible_playbook_args))
        self.logger.info("Running %s %s", str(self.ansible_playbook_cmd),
            str(ansible_playbook_args))
        ret = subprocess.run(                                                  
            [self.ansible_playbook_cmd, ansible_playbook_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        if 'WARNING' in (ret.stdout, ret.stderr):
            logger.warning("Warnings found in ansible output: %s %s",
                ret.stdout, ret.stderr)
        return ret.returncode
