#!/usr/bin/python
"""Unit tests for edgerouter.py."""

import unittest

from edgerouter import Config
from edgerouter import Portal


class TestEdgeRouter(unittest.TestCase):
  """Unit tests for EdgeRouter Config and Portal classes."""

  def setUp(self):
    with open('testdata/config.txt') as config_file:
      self.config = config_file.read()

  def test_same_config(self):
    """Test a no op run of the script."""
    sessions_str = ('john 192.168.2.42\npaul 192.168.2.45\n'
                    'george 192.168.2.52\nringo 192.168.2.68\n')
    portal = Portal(sessions_str)
    edgerouter = Config(config=self.config, portal=portal)
    self.assertEqual("", edgerouter.updates())

  def test_different_config(self):
    """Test a run of the script that changes rules."""
    sessions_str = ('john 192.168.2.43\npaul 192.168.2.45\n'
                    'george 192.168.2.52\ntest 192.168.2.68\n')
    portal = Portal(sessions_str)
    edgerouter = Config(config=self.config, portal=portal)
    expected_results = (
      'delete firewall modify SQUID rule 48\n'
      'delete firewall modify SQUID rule 11\n'
      'set firewall modify SQUID rule 13 action accept\n'
      'set firewall modify SQUID rule 13 description john\n'
      'set firewall modify SQUID rule 13 source address 192.168.2.43\n'
      'set firewall modify SQUID rule 14 action accept\n'
      'set firewall modify SQUID rule 14 description test\n'
      'set firewall modify SQUID rule 14 source address 192.168.2.68\n')
    self.assertItemsEqual(expected_results.split('\n'),
                          edgerouter.updates().split('\n'))


if __name__ == '__main__':
  unittest.main()
