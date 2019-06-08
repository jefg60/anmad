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
        # Change logging.ERROR to INFO, to see log messages during testing.
        self.logger.setLevel(logging.CRITICAL)
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

    def test_verify_yaml_missingfile(self):
        verify = anmad_yaml.verify_yaml_file(self.logger, 'tests/missing.yml')
        self.assertFalse(verify)

    def test_verify_yaml_is_empty_directory(self):
        verify = anmad_yaml.verify_yaml_file(self.logger, 'empty_dir')
        self.assertFalse(verify)

    def test_verify_yaml_is_directory(self):
        verify = anmad_yaml.verify_yaml_file(self.logger, 'samples')
        self.assertTrue(verify)

    def test_verify_yaml_is_bad_directory(self):
        verify = anmad_yaml.verify_yaml_file(self.logger, 'tests')
        self.assertFalse(verify)

    def test_verify_yaml_goodfile(self):
        """Test verify_yaml_file func with valid yaml."""
        verify = anmad_yaml.verify_yaml_file(self.logger, (self.playbookroot + '/' + self.playbooks[0]))
        self.assertTrue(verify)

    def test_verify_yaml_badfile(self):
        """Test that verify_yaml_file correctly identifies bad yaml."""
        verify = anmad_yaml.verify_yaml_file(self.logger, 'tests/badyaml.yml')
        self.assertFalse(verify)

    def test_list_bad_yamlfiles(self):
        """Test that bad yamlfiles are listed."""
        verify = anmad_yaml.list_bad_yamlfiles(self.logger, ['tests'])
        self.assertEqual(verify, ['tests'])

    def test_list_bad_yamlfiles_allgood(self):
        """Test that list_bad_yamlfiles returns empty string when it should."""
        verify = anmad_yaml.list_bad_yamlfiles(self.logger, ['samples'])
        self.assertEqual(verify, [])

    def test_list_missing_files(self):
        """Test missing files func."""
        testfiles = ['samples/' + x for x in self.playbooks]
        verify = anmad_yaml.list_bad_yamlfiles(self.logger, testfiles)
        self.assertEqual(verify, [])
        verify = anmad_yaml.list_bad_yamlfiles(self.logger, ['tests/missing.yml'])
        self.assertEqual(verify, ['tests/missing.yml'])

    def test_verify_config_file(self):
        """Test the verify_config_file func."""
        verify = anmad_yaml.verify_config_file('tests/bad-inventory')
        self.assertFalse(verify)
        verify = anmad_yaml.verify_config_file('samples/inventory-internal')
        self.assertTrue(verify)


if __name__ == '__main__':
    unittest.main()
