"""Functions to check / run ansible playbooks."""
import os
from multiprocessing import Pool

import anmad.common.yaml as anmadyaml
from anmad.daemon.run import AnmadRun

class AnmadMulti:
    """Anmad Multi inventory / playbook class. Accepts a list of inventories.
    Multi playbooks will run against the first inventory in the list."""


    def __init__(self, **kwargs):
        """Init ansibleSyntaxCheck."""
        self.logger = kwargs.get('logger')
        self.ansible_log_path = kwargs.get('ansible_log_path')
        self.ansible_playbook_cmd = kwargs.get('ansible_playbook_cmd')
        self.vault_password_file = kwargs.get('vault_password_file', None)
        self.timeout = kwargs.get('timeout', 1800)
        inventories = kwargs.get('inventories')
        if not isinstance(inventories, list):
            self.inventories = [inventories]
        else:
            self.inventories = inventories
        self.maininventory = self.inventories[0]

    def syntax_check_one_play_many_inv(self, playbook):
        """Check a single playbook against all inventories.
        Returns 0 if all OK, 1 or 2 if there was a parsing issue
        with the playbook or the inventories respectively.
        Returns 3 if ansible-playbook syntax check failed.
        If any errors are found, the function will stop and return one
        of the above without continuing."""
        # check if we've been passed a single string, make it a one item list
        # if so.
        if not anmadyaml.verify_yaml_file(self.logger, playbook):
            self.logger.error(
                "Unable to verify yaml file %s", str(playbook))
            return 1
        for my_inventory in self.inventories:
            if not anmadyaml.verify_yaml_file(self.logger, my_inventory):
                # check the 'bad yaml' isnt actually a valid ini style
                # inventory, before reporting it bad.
                if not anmadyaml.verify_config_file(my_inventory):
                    self.logger.error(
                        "Unable to verify file %s", str(my_inventory))
                    return 2

            playbookobject = AnmadRun(
                self.ansible_playbook_cmd,
                self.vault_password_file,
                self.timeout,
                logger=self.logger,
                inventory=my_inventory,
                ansible_log_path=self.ansible_log_path)
            if playbookobject.syncheck_playbook(playbook).returncode != 0:
                return 3
        # if none of the above return statements happen, then syntax checks
        # passed and we can return 0 to the caller.
        return 0

    def concurrentrun(self, listofplaybooks, syncheck=False):
        """Concurrently run a list of ansible playbooks
        against a single inventory.
        Return number of nonzero exit codes (so 0 = success)."""
        if isinstance(listofplaybooks, str):
            listofplaybooks = [listofplaybooks]
        playbookobj = AnmadRun(
            self.ansible_playbook_cmd,
            self.vault_password_file,
            self.timeout,
            logger=self.logger,
            inventory=self.maininventory,
            ansible_log_path=self.ansible_log_path)

        output = []
        concurrency = os.cpu_count()
        pool = Pool(concurrency)
        if syncheck:
            completed_processes = pool.map(
                playbookobj.syncheck_playbook, listofplaybooks)
        else:
            completed_processes = pool.map(
                playbookobj.run_playbook, listofplaybooks)
        pool.close()
        pool.join()

        output = []

        for completedprocess in completed_processes:
            output.append(completedprocess.returncode)

        # if the returned list of outputs only contains 0, success.
        if output.count(0) == len(output):
            return 0
        # otherwise, subtract number of passed (0) values from the list length,
        # to get the number of failed checks.
        return len(output) - output.count(0)

    def checkplaybooks(self, listofplaybooks):
        """Syntax check a list of playbooks concurrently against one inv.
        Return number of failed syntax checks (so 0 = success)."""
        problemcount = self.concurrentrun(listofplaybooks, syncheck=True)
        return problemcount

    def syncheck_dir(self, check_dir):
        """Check all YAML in a directory for ansible syntax.
        Return number of files failing syntax check (0 = success)
        and/or 255 if dir not found"""
        if not os.path.exists(check_dir):
            self.logger.error("%s cannot be found", str(check_dir))
            return 255

        problemcount = self.checkplaybooks(
            anmadyaml.find_yaml_files(self.logger, check_dir))
        return problemcount

    def runplaybooks(self, listofplaybooks):
        """Run a list of ansible playbooks and wait for them to finish.
        Return number of nonzero exit codes (so 0 = success)."""
        problemcount = self.concurrentrun(listofplaybooks)
        return problemcount
