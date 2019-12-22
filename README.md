# Alexium Internet Filter

Alexium Internet Filter is a parental control system for home
networks.

## How it works

You need to have a router that supports Policy Based Routing and a
server that can run the Squid Proxy and Captive Portal web service.

The router is configured by default to block all outbound internet
traffic. Instead, the traffic is transparently routed to a Squid
proxy. The proxy queries an ICAP server which checks the destination
hostname against the whitelist to determine whether the request is
permitted or not.

Parents can get direct internet access by authenticating to a Captive
Portal web service. The Captive Portal programs the router to allow
direct internet access for the IP address belonging to the parent's
computer. The parent's browser maintains a session with the Captive
Portal through a keepalive URL. A cron script removes the parent's IP
address from the router configuration when the session ends.

