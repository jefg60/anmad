#!/usr/bin/env python3
"""Test http return codes."""

import unittest
import re
import datetime

import requests

class TestReturnCodes(unittest.TestCase):
    """Test http return codes."""

    def setUp(self):
        self.baseurl = "http://localhost:9999/"
        self.dateformat = "%Y-%m-%d %H:%M:%S"

    def check_for_valid_date(self, text):
        """checks date string was passed to template."""
        dateline = re.search(r"document.write\(moment\(*.*\)", text)
        datestring = re.search(r'(\d+\-\d+\-\d+\ \d+\:\d+\:\d+)', dateline.group(0))
        self.assertIsNotNone(datestring)
        self.assertTrue(datetime.datetime.strptime(datestring.group(0), self.dateformat))

    def test_ara_button(self):
        """Test the ara button."""
        output = requests.get(self.baseurl)
        self.assertIn('/ara', output.text)

    def test_clearall_button(self):
        """Test the clearall button."""
        output = requests.get(self.baseurl + 'clearqueues')
        self.assertEqual(200, output.status_code)
        self.assertIn('Clear redis queues requested.', output.text)
        self.check_for_valid_date(output.text)

    def test_runall_button(self):
        """Test the runall button."""
        # pylint: disable=C0301
        requests.get(self.baseurl + 'clearqueues')
        output = requests.get(self.baseurl + 'runall')
        self.assertEqual(200, output.status_code)
        self.assertIn("<h2>Queued Jobs:</h2>\n\t<h3>(multiples between [] will be concurrently run)</h3>\n\t\n\t\n\t<h3>[&#39;/vagrant/samples/deploy.yaml&#39;, &#39;/vagrant/samples/deploy2.yaml&#39;]</h3>", output.text)
        self.assertIn(
            "<h3>[&#39;/vagrant/samples/deploy4.yaml&#39;]</h3>", output.text)
        self.check_for_valid_date(output.text)

    def test_otherplays(self):
        """Test the otherplays page."""
        output = requests.get(self.baseurl + 'otherplays')
        self.assertEqual(200, output.status_code)
        self.assertIn("run deploy6.yaml", output.text)
        self.assertIn("run deploy9.yml", output.text)
        self.assertIn("Back to main interface", output.text)
        self.check_for_valid_date(output.text)

    def test_jobs(self):
        """Test the jobs / processes page."""
        output = requests.get(self.baseurl + 'jobs')
        self.assertEqual(200, output.status_code)
        self.assertIn("playbook /srv/config/deploy.yaml", output.text)
        self.assertIn("playbook /srv/config/deploy2.yaml", output.text)
        self.assertIn("ansible log for deploy.yaml", output.text)
        self.assertIn("ansible log for deploy2.yaml", output.text)
        self.assertIn("Back to main interface", output.text)
        self.assertIn("KILL PID", output.text)
        self.assertIn("KILL ALL", output.text)
        self.check_for_valid_date(output.text)

    def test_log(self):
        """Test the log page."""
        output = requests.get(self.baseurl + 'log')
        self.assertEqual(200, output.status_code)
        self.assertIn("for full logs, check syslog", output.text)
        self.assertIn("messages (newest first):", output.text)
        self.check_for_valid_date(output.text)

if __name__ == '__main__':
    unittest.main()
