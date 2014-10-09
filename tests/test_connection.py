import unittest
import pynats
import mocket.mocket as mocket


class TestConnection(unittest.TestCase):
    def setUp(self):
        mocket.Mocket.enable()
        assertSocket(
            expected='CONNECT {"pedantic": false, "verbose": false, "ssl_required": false, "name": "foo"}\r\n',
            response='INFO {"foo": "bar"}\r\n'
        )

    def test_connect(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

    def test_ping(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        assertSocket(expected='PING\r\n', response='PONG\r\n')
        c.ping()

    def test_subscribe_and_unsubscribe(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        def handler(msg):
            pass

        assertSocket(expected='SUB foo  1\r\n', response='')
        subscription = c.subscribe('foo', handler)

        self.assertEquals(c._next_sid, 2)
        self.assertIsInstance(subscription, pynats.Subscription)
        self.assertEquals(subscription.sid, 1)
        self.assertEquals(subscription.subject, 'foo')
        self.assertEquals(subscription.callback, handler)

        assertSocket(expected='UNSUB 1\r\n', response='')
        c.unsubscribe(subscription)
        self.assertEquals(c._subscriptions, {})

    def test_publish(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        assertSocket(expected='PUB foo 3\r\n', response='')
        assertSocket(expected='msg\r\n', response='')
        c.publish('foo', 'msg')

    def test__build_inbox(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        inbox = c._build_inbox()
        self.assertEquals(20, len(inbox))

    def test_request(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        inbox = '_INBOX.kykblzisxpeou'

        def mocked_inbox():
            return inbox

        c._build_inbox = mocked_inbox

        assertSocket(expected='SUB %s  1\r\n' % inbox, response='')
        assertSocket(expected='UNSUB 1 1\r\n', response='')
        assertSocket(expected='PUB request %s 3\r\n' % inbox, response='')
        assertSocket(expected='msg\r\n', response='')

        s = c.request('request', 'callback', 'msg')
        self.assertEquals(s.subject, inbox)

    def test_request_without_msg(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        inbox = '_INBOX.kykblzisxpeou'

        def mocked_inbox():
            return inbox

        c._build_inbox = mocked_inbox

        assertSocket(expected='SUB %s  1\r\n' % inbox, response='')
        assertSocket(expected='UNSUB 1 1\r\n', response='')
        assertSocket(expected='PUB request %s 0\r\n' % inbox, response='')
        assertSocket(expected='\r\n', response='')

        s = c.request('request', 'callback')
        self.assertEquals(s.subject, inbox)

    def test_publish_with_reply(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        assertSocket(expected='PUB foo reply 3\r\n', response='')
        assertSocket(expected='msg\r\n', response='')
        c.publish('foo', 'msg', 'reply')

    def test_wait_receive_ping(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        def monkey(self, *expected_commands):
            return pynats.commands.PING, None

        c._recv = monkey
        assertSocket(expected='PONG\r\n', response='')
        c.wait(duration=0.1)

    def test_wait_receive_msg(self):
        c = pynats.Connection('nats://localhost:4444', 'foo')
        c.connect()

        def handler(msg):
            return False

        assertSocket(expected='SUB foo  1\r\n', response='')
        c.subscribe('foo', handler)

        def monkey(self, *expected_commands):
            line = 'MSG foo 1 reply 10\r\n'
            return pynats.commands.MSG, pynats.commands.MSG.match(line)

        c._recv = monkey
        assertSocket(expected='PONG\r\n', response='')
        c.wait(count=1)


class assertSocket(object):
    def __init__(self, expected, response):
        self.location = ('localhost', 4444)
        mocket.Mocket.register(self)
        self.expected = expected
        self.response = response
        self.calls = 0

    def can_handle(self, data):
        return self.expected == data

    def collect(self, data):
        self.calls += 1

    def get_response(self):
        return self.response

if __name__ == '__main__':
    unittest.main()
