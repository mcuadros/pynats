pynats [![Build Status](https://travis-ci.org/mcuadros/pynats.png?branch=master)](https://travis-ci.org/mcuadros/pynats)
======

A Python client for the [NATS messaging system](https://nats.io).

> Note: pynats is under heavy development

Requirements
------------

* python ~2.7
* [gnatsd server](https://github.com/nats-io/gnatsd)


Usage
-----
### Basic Usage

```python
c = pynats.Connection(verbose=True)
c.connect()

# Simple Publisher
c.publish('foo', 'Hello World!')

# Simple Subscriber
def callback(msg):
    print 'Received a message: %s' % msg.data

c.subscribe('foo', callback)

# Waiting for one msg
c.wait(count=1)

# Requests
def request_callback(msg):
    print 'Got a response for help: %s' % msg.data

c.request('help', request_callback)
c.wait(count=1)

# Unsubscribing
subscription = c.subscribe('foo', callback)
c.unsubscribe(subscription)

# Close connection
c.close()
```

Documentation
-------------

```sh
cd docs
sudo pip install -r requirements.txt
sphinx-build -b html . build
```

After run this commands, the documention can be find at docs/build/index.html


Tests
-----

Tests are in the `tests` folder.
To run them, you need `nosetests` or `py.test`.


License
-------

MIT, see [LICENSE](LICENSE)

