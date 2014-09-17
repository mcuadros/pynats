import re

MSG = re.compile(r'^MSG\s+(?P<subject>[^\s\r\n]+)\s+(?P<sid>[^\s\r\n]+)\s+(?P<reply>([^\s\r\n]+)[^\S\r\n]+)?(?P<size>\d+)\r\n')
OK = re.compile(r'^\+OK\s*\r\n')
ERR = re.compile(r'^-ERR\s+(\'.+\')?\r\n')
PING = re.compile(r'^PING\r\n')
PONG = re.compile(r'^PONG\r\n')
INFO = re.compile(r'^INFO\s+([^\r\n]+)\r\n')

commands = {
    'MSG': MSG, '+OK': OK, '-ERR': ERR,
    'PING': PING, 'PONG': PONG, 'INFO': INFO
}
