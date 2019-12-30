#!/usr/bin/python
"""Configuration script for EdgeRouter for Alexium Internet Filter.

EdgeOS v2.0.6 includes python2.7 but not python3."""

import logging
import subprocess
import sys
import urllib2
import vyattaconfparser

MIN_RULE_NUM = 11
MAX_RULE_NUM = 48
SHOW_CONFIG = ['/bin/cli-shell-api', 'showConfig', '--show-active-only']
RULE_NAME = 'SQUID'
SESSIONS_URL = 'http://192.168.3.10/sessions'


class Rule(object):
  """Class representing a firewall modify rule in the EdgeRouter Config."""

  def __init__(self, address, description):
    self.address = address
    self.description = description

  @classmethod
  def fromdict(cls, rule_dict):
    """Parameters:
         rule_dict: Dictionary with the following format:
           {u'action': u'accept', u'source': {u'address': u'192.168.2.42'},
            u'description': u'john'}}
    """
    address = rule_dict['source']['address']
    description = rule_dict['description']
    return cls(address, description)

  def add(self, rule_num):
    """EdgeRouter commands to add a firewall modify rule."""
    return ('set firewall modify SQUID rule %s action accept\n'
            'set firewall modify SQUID rule %s description %s\n'
            'set firewall modify SQUID rule %s source address %s\n'
            % (rule_num, rule_num, self.description, rule_num, self.address))

  @staticmethod
  def delete(rule_num):
    """Edgerouter commands to delete a firewall modify rule."""
    return 'delete firewall modify SQUID rule %s\n' % (rule_num)


class Config(object): # pylint: disable=too-few-public-methods
  """Class representing an EdgeRouter configuration."""

  def __init__(self, config=None, portal=None):
    self.portal = portal
    if not self.portal:
      self.portal = Portal()
    if not config:
      try:
        config = subprocess.check_output(SHOW_CONFIG)
      except subprocess.CalledProcessError as error:
        logging.error(error.output)
        sys.exit(error.returncode)
    self.config = vyattaconfparser.parse_conf(config)
    self.rules_config = self.config['firewall']['modify'][RULE_NAME]['rule']
    self.rules = self._get_rules()
    self.available_rule_nums = self._get_available_rule_nums()

  def updates(self):
    """Get the updates for the EdgeRouter configuration."""
    updates = ""
    for rule_num in self.rules:
      rule = self.rules[rule_num]
      if rule.address in self.portal.sessions and \
         rule.description == self.portal.sessions[rule.address]:
        # rule exists in portal sessions, do nothing
        pass
      else:
        # rule does not exist in portal sessions, delete rule
        updates += Rule.delete(rule_num)
    for ip_addr in self.portal.sessions:
      portal_session_in_rules = False
      for rule_num in self.rules:
        rule = self.rules[rule_num]
        if ip_addr == rule.address and \
           self.portal.sessions[ip_addr] == rule.description:
          # portal session is in rules, do nothing
          portal_session_in_rules = True
          break
      if not portal_session_in_rules:
        # portal session is not in rules, add new rule
        new_rule = Rule(ip_addr, self.portal.sessions[ip_addr])
        next_rule_num = self.available_rule_nums.pop(0)
        updates += new_rule.add(next_rule_num)
    return updates

  def _get_rules(self):
    """Returns:
         Dictionary of rules keyed on an integer rule number with values
         that are Rule objects.
    """
    rules = {}
    for rule_num in self.rules_config:
      if int(rule_num) >= MIN_RULE_NUM and int(rule_num) <= MAX_RULE_NUM:
        rules[int(rule_num)] = Rule.fromdict(self.rules_config[rule_num])
    return rules

  def _get_available_rule_nums(self):
    """Returns a list of integers, representing available rule numbers."""
    available_rules = []
    for rule_num in range(MIN_RULE_NUM, MAX_RULE_NUM):
      if rule_num not in self.rules:
        available_rules.append(rule_num)
    if not available_rules:
      logging.error('No available rules')
      sys.exit(1)
    return available_rules


class Portal(object): # pylint: disable=too-few-public-methods
  """Class to represent sessions in the Captive Portal."""

  def __init__(self, sessions_str=None):
    self.sessions_str = sessions_str
    self.sessions = self._get_portal_sessions()

  def _get_portal_sessions(self):
    """Returns a dictionary of portal sessions.

    Key: string IP address
    Value: string username
    """
    sessions = {}
    if not self.sessions_str:
      try:
        response = urllib2.urlopen(SESSIONS_URL)
        self.sessions_str = response.read()
      except IOError as error:
        logging.error(error)
        sys.exit(1)
    for session in self.sessions_str.split('\n'):
      if session:
        (username, ip_addr) = session.split()
        sessions[ip_addr] = username
    return sessions


def main(): # pylint: disable=missing-docstring
  config = Config()
  sys.stdout.write(config.updates())

if __name__ == '__main__':
  main()
