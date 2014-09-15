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
    _subscriptions = []

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
        self._recv(INFO)

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
        self._recv(PONG)

    def subscribe(self, subject, callback):
        s = Subscription(
            sid=len(self._subscriptions) + 1,
            subject=subject,
            queue='',
            callback=callback,
            connetion=self
        )

        self._subscriptions.append(s)
        self._send('SUB %s %s %d' % (s.subject, s.queue, s.sid))

    def wait(self):
        result = self._recv(MSG)

        print 'subject: %s, sid: %s, reply: %s, size: %s' % (
            result.group('subject'),
            result.group('sid'),
            result.group('reply'),
            result.group('size')
        )

    def reconnect(self):
        self.close()
        self.connect()

    def _send(self, command):
        print 'Send: %s' % command
        SocketError.wrap(self._socket.sendall, command + '\r\n')

    def _recv(self, regexp):
        line = SocketError.wrap(self._socket_file.readline)
        print 'Recv: %s' % line

        result = regexp.match(line)
        if result is None:
            raise UnexpectedResponse(regexp.pattern, line)

        return result


class UnexpectedResponse(Exception):
    pass


class SocketError(Exception):
    @staticmethod
    def wrap(wrapped_function, *args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)
        except socket.error, err:
            raise SocketError(err)
