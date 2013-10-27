import json
import logging
import random
import socket
import cPickle
import sys

import prctl
from AVA1.AVA1_a.Message import Message


__author__ = 'me'

from multiprocessing import Process
import os


class LocalKnot(Process):
    def __init__(self, ID, connections_filename):
        super(LocalKnot, self).__init__()
        prctl.set_proctitle(self._name + '-' + str(ID))
        self.__ID = str(ID)
        self.__connections_filename = connections_filename
        self.__ips_and_ports = None
        self.__ip = None
        self.__port = None
        self.__listeningSocket = None
        self.__neighbours = {}
        self.logger = logging.getLogger(__name__ + '-' + str(ID))
        logging.basicConfig(level=logging.INFO, format='%(name)s %(levelname)s %(asctime)s: %(message)s')

    def run(self):
        self.info()
        self.read_input_file()
        self.open_port()
        self.choose_neighbours()
        init = True
        while True:
            self.receive_message()
            if init:
                self.send_id_to_neighbours()
                init = False

    def getID(self):
        return self.__ID

    def info(self):
        info_message = 'module name:' + __name__ + '\n'
        if hasattr(os, 'getppid'):
            info_message += 'parent process:' + str(os.getppid()) + '\n'
        info_message += 'process id:' + str(os.getpid()) + '\n'
        info_message += 'LocalKnot id:' + str(self.__ID) + '\n\n'
        self.logger.info(info_message)

    def read_input_file(self):
        json_data = open(self.__connections_filename)
        self.__ips_and_ports = json.load(json_data)
        json_data.close()

    def open_port(self):
        self.__ip = self.__ips_and_ports[self.__ID]["ip"]
        self.__port = self.__ips_and_ports[self.__ID]["port"]
        del self.__ips_and_ports[self.__ID]

        self.__listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listeningSocket.bind((self.__ip, self.__port))
        self.__listeningSocket.listen(5)

    def choose_neighbours(self):
        for i in range(3):
            random_index = random.randint(0, len(self.__ips_and_ports) - 1)
            ID = self.__ips_and_ports.keys()[random_index]
            self.add_neighbour(ID)

    def add_neighbour(self, ID):
        self.__neighbours[ID] = self.__ips_and_ports[ID]
        del self.__ips_and_ports[ID]

    def receive_message(self):
        connection, addr = self.__listeningSocket.accept()
        data = connection.recv(1024)
        if data:
            message = cPickle.loads(data)
            self.logger.info("empfangen: " + message.printToString())
            if message.getAction() == 'suicide':
                sys.exit(0)

    def send_id_to_neighbours(self):
        for neighbour in self.__neighbours.values():
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sender.connect((neighbour["ip"], neighbour["port"]))
            except:
                self.logger.error('Error while sending to ' + str(neighbour["ip"]) + ":" + str(neighbour["port"]),
                                  exc_info=1)
            own_id_message = Message("ID", self.__ID)
            sender.sendall(cPickle.dumps(own_id_message))
            self.logger.info("gesendet: " + own_id_message.printToString())

if __name__ == '__main__':
    id = sys.argv[1]
    filename = sys.argv[2]
    localKnot = LocalKnot(id, filename)
    localKnot.run()



