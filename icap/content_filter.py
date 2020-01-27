"""Module for content filtering logic in the ICAP server."""
import io
import os
from os import path


class Filter(): # pylint: disable=too-few-public-methods
  """Implements the host filtering logic in the ICAP server."""

  def __init__(self, whitelist=None):
    self.allow_hosts = {}
    self._init_allow_hosts(whitelist)

  def _init_allow_hosts(self, whitelist):
    """Initialize the list of hosts that are whitelisted.

    The whitelist can be either a string or filename.
    """
    if not whitelist:
      whitelist = os.getenv('WHITELIST', '/var/lib/squidguard/db/whitelist')
    if path.exists(whitelist):
      with open(whitelist) as handle:
        self._read_whitelist(handle)
    else:
      with io.StringIO(whitelist) as handle:
        self._read_whitelist(handle)

  def _read_whitelist(self, handle):
    content = handle.readlines()
    for line in content:
      allow_host = line.split('#')[0].rstrip().lstrip()
      if allow_host:
        self.allow_hosts[allow_host] = 1
    # LOG.info('Initialized allow_list: %s', str(self.allow_hosts))

  def allowed(self, hostname):
    """Returns boolean, if the hostname is allowed."""
    domain_list = hostname.split('.')
    while len(domain_list) > 1:
      domain = '.'.join(domain_list)
      if domain in self.allow_hosts:
        return True
      domain_list.pop()
    return False
