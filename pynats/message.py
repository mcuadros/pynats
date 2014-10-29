class Message(object):
    def __init__(self, sid, subject, size, data, reply=None):
        self.sid = sid
        self.subject = subject
        self.size = size
        self.data = data
        self.reply = reply
