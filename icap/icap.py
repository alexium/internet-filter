#!/usr/bin/python3
"""ICAP server."""

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
    self.set_icap_header('Methods', 'REQMOD')
    self.set_icap_header('Service', 'Internet Filter ICAP service')
    self.send_headers(False)

  def filter_REQMOD(self): # pylint: disable=invalid-name
    """Handle ICAP REQMOD requests."""
    self.set_icap_response(200)

    LOG.info("======== filter request =======")
    LOG.info(self.enc_req)
    LOG.info(self.headers)

    if self.server.content_filter.allowed(self.enc_req[1]):
      LOG.info('%s allowed', self.enc_req[1])
      self.no_adaptation_required()
      return

    LOG.info('%s denied', self.enc_req[1])
    self.set_enc_status('HTTP/1.1 403 Forbidden')
    self.send_headers(False)
    return


def main(): # pylint: disable=missing-docstring
  server = ThreadingSimpleServer(('', PORT), ICAPHandler, Filter())
  try:
    while 1:
      server.handle_request()
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  main()
