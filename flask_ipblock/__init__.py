from flask import request, url_for
from flask_ipblock.documents import IPNetwork


class IPBlock(object):

    def __init__(self, app, read_preference=None, cache_size=None, cache_ttl=None,
                 blocking_enabled=True, logging_enabled=False):
        """
        Initialize IPBlock and set up a before_request handler in the
        app.

        You can override the default MongoDB read preference via the
        optional read_preference kwarg.

        You can limit the impact of the IP checks on your MongoDB by
        maintaining a local in-memory LRU cache. To do so, specify its
        cache_size (i.e. max number of IP addresses it can store) and
        cache_ttl (i.e. how many seconds each result should be cached
        for).

        To run in dry-run mode without blocking requests, set
        blocking_enabled to False. Set logging_enabled to True
        to log IPs that match blocking rules -- if enabled, will
        log even if blocking_enabled is False.
        """
        self.read_preference = read_preference
        self.blocking_enabled = blocking_enabled
        self.logger = None
        if logging_enabled:
            self.logger = app.logger
            self.block_msg = "blocking" if blocking_enabled else "blocking disabled"

        if cache_size and cache_ttl:
            # inline import because cachetools dependency is optional.
            from cachetools import TTLCache
            self.cache = TTLCache(cache_size, cache_ttl)
        else:
            self.cache = None

        app.before_request(self.block_before)

    def block_before(self):
        """
        Check the current request and block it if the IP address it's
        coming from is blacklisted.
        """
        # To avoid unnecessary database queries, ignore the IP check for
        # requests for static files
        if request.path.startswith(url_for('static', filename='')):
            return

        # Some static files might be served from the root path (e.g.
        # favicon.ico, robots.txt, etc.). Ignore the IP check for most
        # common extensions of those files.
        ignored_extensions = ('ico', 'png', 'txt', 'xml')
        if request.path.rsplit('.', 1)[-1] in ignored_extensions:
            return

        ips = request.headers.getlist('X-Forwarded-For')
        if not ips:
            return

        # If the X-Forwarded-For header contains multiple comma-separated
        # IP addresses, we're only interested in the last one.
        ip = ips[0].strip()
        if ip[-1] == ',':
            ip = ip[:-1]
        ip = ip.rsplit(',', 1)[-1].strip()

        if self.matches_ip(ip):
            if self.logger is not None:
                self.logger.info("IPBlock: matched {}, {}".format(ip, self.block_msg))
            if self.blocking_enabled:
                return 'IP Blocked', 200

    def matches_ip(self, ip):
        """Return True if the given IP is blacklisted, False otherwise."""

        # Check the cache if caching is enabled
        if self.cache is not None:
            matches_ip = self.cache.get(ip)
            if matches_ip is not None:
                return matches_ip

        # Query MongoDB to see if the IP is blacklisted
        matches_ip = IPNetwork.matches_ip(
            ip, read_preference=self.read_preference)

        # Cache the result if caching is enabled
        if self.cache is not None:
            self.cache[ip] = matches_ip

        return matches_ip
