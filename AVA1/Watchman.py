import cPickle
import socket
import time

from Message import Message
from LocalKnot import LocalKnot


__author__ = 'me'


def send_init_to_zero():
    sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    sender.connect((host, 50000))
    init_message = Message('init', 'War... War never changes', True)
    sender.sendall(cPickle.dumps(init_message))


if __name__ == '__main__':
    for num in range(4):
        print 'Watchman starts', num
        l = LocalKnot(num+1)
        l.start()
        #l.join()
    time.sleep(1)
    #send_init_to_zero()
