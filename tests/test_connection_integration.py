import unittest
import pynats
import mocket.mocket as mocket
import threading
import time


class TestConnectionIntegration(unittest.TestCase):
    def setUp(self):
        mocket.Mocket.disable()

    def test_wait_with_timeout(self):
        c = pynats.Connection('nats://localhost:4222', 'foo')
        c.connect()

        def callback(msg):
            return True

        c.subscribe('foo', callback)
        self._send_message(0.1)
        c.wait(duration=0.1)

    def test_wait_with_limit(self):
        c = pynats.Connection('nats://localhost:4222', 'foo')
        c.connect()

        def callback(msg):
            return True

        c.subscribe('foo', callback)
        self._send_message(0.1)
        self._send_message(0.1)
        self._send_message(0.1)
        c.wait(iterations=3)

    def test_wait_with_handler_return_false(self):
        c = pynats.Connection('nats://localhost:4222', 'foo')
        c.connect()

        def callback(msg):
            return False

        c.subscribe('foo', callback)
        self._send_message(0.1)
        c.wait()

    def _send_message(self, sleep=0):
        def send():
            c = pynats.Connection('nats://localhost:4222', 'foo')
            c.connect()
            c.publish('foo', 'test')
        self._create_thread(send, sleep)

    def _create_thread(self, callback, sleep=0):
        time.sleep(sleep)
        th = threading.Thread(target=callback)
        th.start()
        th.join()
