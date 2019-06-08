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
        """Init ansibleRun."""
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

    def syncheck_playbook(self, playbook):
        """Check a single playbook against a single inventory.
        Returns ansible-playbook command return code
        (should be 0 if syntax checks pass)."""
        self.logger.info("Syntax Checking ansible playbook %s against "
            "inevntory %s", str(playbook), str(self.inventory))
        ret = self.run_playbook(playbook, syncheck=True)
        if ret.returncode == 0:
            self.logger.info(
                "OK. ansible-playbook syntax check return code: "
                "%s", str(ret.returncode))
            return ret.returncode
        # if syntax checks pass, the code below should NOT run
        self.logger.warning(
            "Playbook %s failed syntax check against inventory %s!!!",
            str(playbook), str(self.inventory))
        self.logger.warning(
            "ansible-playbook syntax check return code: "
            "%s", str(ret.returncode))
        return ret.returncode

