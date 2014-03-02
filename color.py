import sys

header = '\033[95m'
blue = '\033[94m'
green = '\033[92m'
warning = '\033[93m'
fail = '\033[91m'
gray = '\033[1;30m'
endc = '\033[0m'
red = '\033[91m'
green = '\033[92m'
cyan = '\033[96m'
white = '\033[97m'
yellow = '\033[93m'
magenta = '\033[95m'
grey = '\033[90m'
black = '\033[90m'

def indent(num):
    [sys.stdout.write('\t') for i in range(num)]

def begin(style):
    sys.stdout.write(style)
    sys.stdout.flush()

def end() :
    sys.stdout.write(endc)
    sys.stdout.flush()

