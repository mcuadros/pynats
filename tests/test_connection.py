import unittest
import pynats


class TestConnection(unittest.TestCase):
    def test_connect(self):
        c = pynats.Connection('nats://localhost:4222', 'foo')
        c.connect()
        c.ping()

        def handler(msg):
            print 'sid %d, reply "%s", data "%s"' % (msg.sid, msg.reply, msg.data)

            return 'foo'

        c.subscribe('foo', handler)
        c.subscribe('bar', handler)

        c.wait()

        self.assertTrue(False)
