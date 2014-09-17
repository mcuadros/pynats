import unittest
import pynats


class TestConnection(unittest.TestCase):
    def test_connect(self):
        c = pynats.Connection('nats://localhost:4222', 'foo')
        c.connect()
        c.ping()

        def handler(msg):
            print 'foo', msg
            return 'foo'

        c.subscribe('foo', handler)

        def handler(msg):
            print 'bar', msg
            return 'bar'

        c.subscribe('bar', handler)

        c.wait()

        self.assertTrue(False)
