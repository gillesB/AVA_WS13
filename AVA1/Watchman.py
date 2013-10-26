import cPickle
import socket
import time
import json

from Message import Message
from LocalKnot import LocalKnot


__author__ = 'me'

class Watchman:


    def __init__(self):
        self.__ips_and_ports = ""


    def read_input_file(self):
        json_data = open('AVA1/json_data')
        self.__ips_and_ports = json.load(json_data)
        json_data.close()

    def send_init_to_zero(self, ID):
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        initiator = self.__ips_and_ports[str(ID)]
        sender.connect((initiator["ip"], initiator["port"]))
        init_message = Message('init', 'War... War never changes', True)
        sender.sendall(cPickle.dumps(init_message))


if __name__ == '__main__':
    for num in range(7):
        l = LocalKnot(num+1)
        l.start()
        #l.join()

    time.sleep(1)
    watchman = Watchman()
    watchman.read_input_file()
    watchman.send_init_to_zero(1)
