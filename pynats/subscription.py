class Subscription(object):
    sid = None
    subject = None
    queue = None
    connetion = None
    callback = None
    msgs = 0
    delivered = 0
    bytes = 0
    max = 0

    def __init__(self, sid, subject, queue, callback, connetion):
        self.sid = sid
        self.subject = subject
        self.queue = queue
        self.connetion = connetion
        self.callback = callback
