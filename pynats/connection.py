import socket
import json
import urlparse
from commands import commands, MSG, INFO, PING, PONG
from pynats.subscription import Subscription

DEFAULT_URI = 'nats://localhost:4222'


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

        self._next_sid += 1
        self._subscriptions[self._next_sid] = s
        self._send('SUB %s %s %d' % (s.subject, s.queue, s.sid))

    def wait(self):
        while True:
            type, result = self._recv(MSG, PING)
            if type is MSG:
                self._handle_msg(result)
            else:
                self._handle_ping()

    def _handle_msg(self, result):
        msg = dict(result.groupdict())
        msg['sid'] = int(msg['sid'])
        msg['size'] = int(msg['size'])
        msg['data'] = SocketError.wrap(self._socket_file.readline)

        s = self._subscriptions.get(msg['sid'])
        s.handle_msg(msg)

    def _handle_ping(self):
        self._send('PONG')

    def reconnect(self):
        self.close()
        self.connect()

    def _send(self, command):
        print 'Send: %s' % command
        SocketError.wrap(self._socket.sendall, command + '\r\n')

    def _recv(self, *expected_commands):
        line = SocketError.wrap(self._socket_file.readline)
        print 'Recv: %s' % line

        command = self._get_command(line)
        if command not in expected_commands:
            raise UnexpectedResponse(line)

        result = command.match(line)
        if result is None:
            raise UnknownResponse(command.pattern, line)

        return command, result

    def _get_command(self, line):
        values = line.strip().split(' ', 1)

        return commands.get(values[0])


class UnknownResponse(Exception):
    pass


class UnexpectedResponse(Exception):
    pass


class SocketError(Exception):
    @staticmethod
    def wrap(wrapped_function, *args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)
        except socket.error, err:
            raise SocketError(err)
