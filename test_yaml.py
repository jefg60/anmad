#!/usr/bin/env python3
"""Tests for anmad_yaml module."""

import logging
import os
import unittest

import __main__ as main

import anmad_yaml

class TestVersion(unittest.TestCase):
    """Tests for anmad_buttons module."""

    def setUp(self):
        self.playbooks = ['deploy.yaml', 'deploy2.yaml']
        self.pre_run_playbooks = ['deploy4.yaml']
        self.playbookroot = 'samples'
        self.logger = logging.getLogger(os.path.basename(main.__file__))
        self.testyamlfiles = ['deploy.yaml']
        for x in range(2, 9):
            dx = [('deploy' + str(x) + '.yaml')]
            self.testyamlfiles.extend(dx)
        self.testyamlfiles.extend(['deploy9.yml'])
        self.testyamlfiles_parent = ['samples/' + x for x in self.testyamlfiles]
        self.testyamlfiles_parent.sort()

    def test_find_yaml_files(self):
        """Test find_yaml_files func."""
        yamlfiles = anmad_yaml.find_yaml_files(self.logger, self.playbookroot)
        self.assertIsNotNone(yamlfiles)
        self.assertEqual(len(yamlfiles), 9)
        self.assertEqual(yamlfiles, self.testyamlfiles_parent)

    def test_verify_yaml_file(self):
        """Test verify_yaml_file func with valid yaml."""
        verify = anmad_yaml.verify_yaml_file(self.logger, (self.playbookroot + '/' + self.playbooks[0]))
        self.assertTrue(verify)

if __name__ == '__main__':
    unittest.main()
