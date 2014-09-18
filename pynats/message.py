class Message(object):
    def __init__(self, sid, size, data, reply=None):
        self.sid = sid
        self.size = size
        self.data = data
        self.reply = reply
