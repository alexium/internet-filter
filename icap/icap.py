#!/usr/bin/python3
"""ICAP server."""

from ipaddress import ip_address
import logging
import os
import socketserver
from pyicap import BaseICAPRequestHandler
from pyicap import ICAPServer

from content_filter import Filter


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG = logging.getLogger(__name__)
PORT = 1344


class ThreadingSimpleServer(socketserver.ThreadingMixIn, ICAPServer):
  """ICAP server class."""

  def __init__(self, server_address, request_handler, content_filter):
    self.content_filter = content_filter
    ICAPServer.__init__(self, server_address, request_handler)


class ICAPHandler(BaseICAPRequestHandler):
  """ICAP handler class."""

  def filter_OPTIONS(self): # pylint: disable=invalid-name
    """Handle ICAP OPTIONS requests."""
    self.set_icap_response(200)
    self.set_icap_header(b'Methods', b'REQMOD')
    self.set_icap_header(b'Service', b'Internet Filter ICAP service')
    self.send_headers(False)

  def filter_REQMOD(self): # pylint: disable=invalid-name
    """Handle ICAP REQMOD requests."""
    self.set_icap_response(200)

    # self.enc_req = [b'CONNECT', b'172.217.195.129:443', b'HTTP/1.1']
    host = self.enc_req[1].split(b':')[0]
    try:
      ip_address(host)
      self.send_response(False)
    except ValueError:
      pass
    
    if self.server.content_filter.allowed(host):
      self.send_response(True)
    else:
      self.send_response(False)

  def send_response(self, allowed):
    """Send response. The allowed parameter is a boolean: True if content is allowed."""
    if allowed:
      LOG.info('%s allowed', self.enc_req[1])
      self.no_adaptation_required()
    else:
      LOG.info('%s denied', self.enc_req[1])
      self.set_enc_status(b'HTTP/1.1 403 Forbidden')
      self.send_headers(False)


def main(): # pylint: disable=missing-docstring
  server = ThreadingSimpleServer(('', PORT), ICAPHandler, Filter())
  try:
    while 1:
      server.handle_request()
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  main()
