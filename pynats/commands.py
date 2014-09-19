import re

MSG = re.compile(b'^MSG\s+(?P<subject>[^\s\r\n]+)\s+(?P<sid>[^\s\r\n]+)\s+(?P<reply>([^\s\r\n]+)[^\S\r\n]+)?(?P<size>\d+)\r\n')
OK = re.compile(b'^\+OK\s*\r\n')
ERR = re.compile(b'^-ERR\s+(\'.+\')?\r\n')
PING = re.compile(b'^PING\r\n')
PONG = re.compile(b'^PONG\r\n')
INFO = re.compile(b'^INFO\s+([^\r\n]+)\r\n')

commands = {
    'MSG': MSG, '+OK': OK, '-ERR': ERR,
    'PING': PING, 'PONG': PONG, 'INFO': INFO
}
