import socket
import json
import urlparse
import re
from pynats.subscription import Subscription

DEFAULT_URI = 'nats://localhost:4222'

MSG = re.compile(r'^MSG\s+(?P<subject>[^\s\r\n]+)\s+(?P<sid>[^\s\r\n]+)\s+(?P<reply>([^\s\r\n]+)[^\S\r\n]+)?(?P<size>\d+)\r\n')
OK = re.compile(r'^\+OK\s*\r\n')
ERR = re.compile(r'^-ERR\s+(\'.+\')?\r\n')
PING = re.compile(r'^PING\r\n')
PONG = re.compile(r'^PONG\r\n')
INFO = re.compile(r'^INFO\s+([^\r\n]+)\r\n')


class Connection(object):
    _options = {}
    _connect_timeout = None
    _socket = None
    _socket_file = None
    _subscriptions = {}
    _next_sid = 0

    def __init__(
        self,
        url=DEFAULT_URI,
        name=None,
        ssl_required=False,
        verbose=False,
        pedantic=False
    ):
        self._options = locals()
        self._options['url'] = urlparse.urlsplit(self._options['url'])

    def connect(self):
        self._build_socket()
        self._connect_socket()
        self._build_file_socket()
        self._send_connect_msg()

    def _build_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._connect_timeout)

    def _connect_socket(self):
        SocketError.wrap(self._socket.connect, (
            self._options['url'].hostname,
            self._options['url'].port
        ))

    def _send_connect_msg(self):
        self._send('CONNECT %s' % self._build_connect_config())
        self._recv_match(INFO)

    def _build_connect_config(self):
        config = {
            'verbose': self._options['verbose'],
            'pedantic': self._options['pedantic'],
            'ssl_required': self._options['ssl_required'],
            'name': self._options['name'],
        }

        if self._options['url'].username is not None:
            config['user'] = self._options['url'].username
            config['pass'] = self._options['url'].password

        return json.dumps(config)

    def _build_file_socket(self):
        self._socket_file = self._socket.makefile('rb')

    def ping(self):
        self._send('PING')
        self._recv_match(PONG)

    def subscribe(self, subject, callback):
        s = Subscription(
            sid=len(self._subscriptions) + 1,
            subject=subject,
            queue='',
            callback=callback,
            connetion=self
        )

        self._next_sid += 1
        self._subscriptions[self._next_sid] = s
        self._send('SUB %s %s %d' % (s.subject, s.queue, s.sid))

    def wait(self):
        while True:
            self._handle_msg(self._recv_msg())

    def _handle_msg(self, msg):
        s = self._subscriptions.get(msg['sid'])
        s.handle_msg(msg)

    def reconnect(self):
        self.close()
        self.connect()

    def _send(self, command):
        print 'Send: %s' % command
        SocketError.wrap(self._socket.sendall, command + '\r\n')

    def _recv_match(self, regexp):
        line = SocketError.wrap(self._socket_file.readline)
        print 'Recv: %s' % line

        result = regexp.match(line)
        if result is None:
            raise UnexpectedResponse(regexp.pattern, line)

        return result

    def _recv_msg(self):
        result = self._recv_match(MSG)

        msg = dict(result.groupdict())
        msg['sid'] = int(msg['sid'])
        msg['size'] = int(msg['size'])
        msg['data'] = SocketError.wrap(self._socket_file.readline)

        return msg


class UnexpectedResponse(Exception):
    pass


class SocketError(Exception):
    @staticmethod
    def wrap(wrapped_function, *args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)
        except socket.error, err:
            raise SocketError(err)
