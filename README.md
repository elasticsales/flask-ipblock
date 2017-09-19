Flask-IPBlock [![Build Status](https://circleci.com/gh/closeio/flask-ipblock.png?branch=master&style=shield)](https://circleci.com/gh/closeio/flask-ipblock)
=============

Block certain IP addresses from accessing your Flask application.

Flask-IPBlock is backed by MongoDB and supports application-level caching to boost performance.

Options
=======
You can override the default MongoDB read preference via the optional read_preference kwarg.

You can limit the impact of the IP checks on your MongoDB by maintaining a local in-memory LRU cache. To do so, specify its cache_size (i.e. max number of IP addresses it can store) and cache_ttl (i.e. how many seconds each result should be cached for).

To run in dry-run mode without blocking requests, set `blocking_enabled` to `False`. Set `logging_enabled` to `True` to log IPs that match blocking rules -- if enabled, will log even if `blocking_enabled` is False.

Setup
=====

``` python
from flask import Flask
from flask_ipblock import IPBlock
from flask_ipblock.documents import IPNetwork

# Initialize the Flask app
app = Flask(__name__)

# Configuration (e.g. setting up MongoEngine)

# Set up IPBlock
ipblock = IPBlock(app)

# Create a MongoEngine document corresponding to a range of IP addresses
# owned by Facebook
IPNetwork.objects.create_from_string('204.15.20.0/22', label='Facebook')

# From now on, any request coming from the above range will be blocked.
```
