import unittest
import pynats


class TestConnection(unittest.TestCase):
    def test_connect(self):
        c = pynats.Connection('nats://localhost:4222', 'foo')
        c.connect()
        c.ping()

        def handler():
            return 'foo'

        c.subscribe('hello', handler)
        c.wait()

        self.assertTrue(False)
