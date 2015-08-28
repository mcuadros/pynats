import unittest
import pynats
import mocket.mocket as mocket
import threading
import time


class TestConnectionIntegration(unittest.TestCase):
    def setUp(self):
        mocket.Mocket.disable()

    def test_wait_with_timeout(self):
        c = pynats.Connection(verbose=True)
        c.connect()

        def callback(msg):
            return True

        c.subscribe('foo', callback)
        self._send_message(0.1)
        c.wait(duration=0.1)

    def test_wait_with_limit(self):
        c = pynats.Connection(verbose=True)
        c.connect()

        def callback(msg):
            return True

        c.subscribe('foo', callback)
        self._send_message(0.1)
        self._send_message(0.1)
        self._send_message(0.1)
        c.wait(count=3)

    def test_wait_with_limit_foo(self):
        c = pynats.Connection(verbose=True)
        c.connect()

        def callback(msg):
            return True


        s = c.subscribe('foo', callback)
        c.unsubscribe(s, 3)
        self.assertEquals(1, len(c._subscriptions))

        self._send_message(0.1)
        self._send_message(0.1)
        self._send_message(0.1)
        c.wait(count=3)

        self.assertEquals(0, len(c._subscriptions))

    def test_wait_with_handler_return_false(self):
        c = pynats.Connection(verbose=True)
        c.connect()

        def callback(msg):
            return False

        c.subscribe('foo', callback)
        self._send_message(0.1)
        c.wait()

    def test_multiline_send(self):
        c = pynats.Connection(verbose=True)
        c.connect()

        payload = "123\n456"

        def callback(msg):
            self.assertEquals(msg.data, payload)
            return False

        c.subscribe('foo', callback)

        self._send_message(msg=payload)
        c.wait()


    def _send_message(self, sleep=0, msg="foo"):
        def send():
            c = pynats.Connection(verbose=True)
            c.connect()
            c.publish('foo', msg)
        self._create_thread(send, sleep)

    def _create_thread(self, callback, sleep=0):
        time.sleep(sleep)
        th = threading.Thread(target=callback)
        th.start()
        th.join()

if __name__ == '__main__':
    unittest.main()
