"""Functions to check / run ansible playbooks."""
import os
from multiprocessing import Pool
import subprocess

import anmad_yaml
import anmad_playbook

class ansibleSyntaxCheck:
    """Anmad syntax checking class. Accepts a list of inventories."""


    def __init__(self,
            logger,
            inventories,
            ansible_playbook_cmd,
            vault_password_file=None):
        """Init ansibleSyntaxCheck."""
        self.logger = logger
        if isinstance(inventories, str):
            self.inventories = [inventories]
        else:
            self.inventories = inventories
        self.maininventory = inventories[0]
        self.ansible_playbook_cmd = ansible_playbook_cmd
        self.vault_password_file = vault_password_file

    def syntax_check_one_play_many_inv(self, playbook):
        """Check a single playbook against all inventories.
        Returns 0 if all OK, 1 or 2 if there was a parsing issue
        with the playbook or the inventories respectively.
        Returns 3 if ansible-playbook syntax check failed.
        If any errors are found, the function will stop and return one
        of the above without continuing."""
        # check if we've been passed a single string, make it a one item list
        # if so.
        if not anmad_yaml.verify_yaml_file(self.logger, playbook):
            self.logger.error(
                "Unable to verify yaml file %s", str(playbook))
            return 1
        for my_inventory in self.inventories:
            if not anmad_yaml.verify_yaml_file(self.logger, my_inventory):
                # check the 'bad yaml' isnt actually a valid ini style inventory,
                # before reporting it bad.
                if not anmad_yaml.verify_config_file(my_inventory):
                    self.logger.error(
                        "Unable to verify file %s", str(my_inventory))
                    return 2

            playbookobject = anmad_playbook.ansibleRun(
                self.logger,
                my_inventory,
                self.ansible_playbook_cmd,
                self.vault_password_file)
            if playbookobject.syncheck_playbook(playbook) is not 0:
                return 3
        # if none of the above return statements happen, then syntax checks 
        # passed and we can return 0 to the caller.
        return 0

    def checkplaybooks(self, listofplaybooks, concurrency=os.cpu_count()):
        """Syntax check a list of playbooks concurrently against one inv.
        Return number of failed syntax checks (so 0 = success)."""
        if isinstance(listofplaybooks, str):
            listofplaybooks = [listofplaybooks]
        syntax_check_pool = anmad_playbook.ansibleRun(
            self.logger,
            self.maininventory,
            self.ansible_playbook_cmd,
            self.vault_password_file)
        
        output = []

        pool = Pool(concurrency)
        output = pool.map(syntax_check_pool.syncheck_playbook, listofplaybooks)
        pool.close()
        pool.join()

        # if the returned list of outputs only contains 0, success.
        if output.count(0) == len(output):
            return 0
        # otherwise, subtract number of passed (0) values from the list length,
        # to get the number of failed checks.
        return len(output) - output.count(0)

    def syncheck_dir(self, check_dir):
        """Check all YAML in a directory for ansible syntax.
        Return number of files failing syntax check (0 = success)
        and/or 255 if dir not found"""
        if not os.path.exists(check_dir):
            self.logger.error("%s cannot be found", str(check_dir))
            return 255

        problemcount = self.checkplaybooks(
            anmad_yaml.find_yaml_files(self.logger, check_dir))
        return problemcount

##############################################################################

def run_one_playbook(logger, my_playbook):
    """Run exactly one ansible playbook. Don't call this
    directly. Instead, call one of the multi-playbook funcs with a list of
    one playbook eg [playbook]."""

    my_playbook = os.path.abspath(my_playbook)
    logger.info(
        "Attempting to run ansible-playbook --inventory %s %s",
        str(MAININVENTORY), str(my_playbook))
    ret = subprocess.call(
        [ANSIBLE_PLAYBOOK_CMD,
         '--inventory', MAININVENTORY,
         '--vault-password-file', ARGS.vault_password_file,
         my_playbook])

    if ret == 0:
        logger.info(
            "ansible-playbook %s return code: %s",
            str(my_playbook), str(ret))
        return ret

    logger.error(
        "ansible-playbook %s did not complete, return code: %s",
        str(my_playbook), str(ret))
    return ret


def runplaybooks(listofplaybooks):
    """Run a list of ansible playbooks and wait for them to finish."""

    pool = Pool(ARGS.concurrency)
    ret = pool.map(run_one_playbook, listofplaybooks)
    pool.close()
    pool.join()

    return ret
