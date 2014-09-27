class Subscription(object):
    def __init__(self, sid, subject, queue, callback, connetion):
        self.sid = sid
        self.subject = subject
        self.queue = queue
        self.connetion = connetion
        self.callback = callback
        self.received = 0
        self.delivered = 0
        self.bytes = 0
        self.max = 0

    def handle_msg(self, msg):
        return self.callback(msg)
