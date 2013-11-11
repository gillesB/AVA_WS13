from abc import abstractmethod
import json
import logging
import random
import socket
import cPickle

import prctl


__author__ = 'me'

from multiprocessing import Process
import os


class AbstractKnot(Process):
    def __init__(self, ID, connections_filename):
        super(AbstractKnot, self).__init__()
        prctl.set_proctitle(self._name + '-' + str(ID))
        self._ID = str(ID)
        self.__connections_filename = connections_filename
        self._ips_and_ports = None
        self.__ip = None
        self.__port = None
        self.__listeningSocket = None

        self.logger = logging.getLogger(__name__ + '-' + str(ID))
        logging.basicConfig(level=logging.INFO, format='%(name)s %(levelname)s %(asctime)s: %(message)s')

    def getID(self):
        return self._ID

    def info(self):
        info_message = 'module name:' + __name__ + '\n'
        if hasattr(os, 'getppid'):
            info_message += 'parent process:' + str(os.getppid()) + '\n'
        info_message += 'process id:' + str(os.getpid()) + '\n'
        info_message += 'LocalKnot id:' + str(self._ID) + '\n\n'
        self.logger.info(info_message)

    def read_connections_file(self):
        json_data = open(self.__connections_filename)
        self._ips_and_ports = json.load(json_data)
        json_data.close()

    def open_port(self):
        self.__ip = self._ips_and_ports[self._ID]["ip"]
        self.__port = self._ips_and_ports[self._ID]["port"]
        del self._ips_and_ports[self._ID]

        self.__listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listeningSocket.bind((self.__ip, self.__port))
        self.__listeningSocket.listen(5)

    def read_connections_and_open_port(self):
        self.read_connections_file()
        self.open_port()

    def receive_message(self):
        connection, addr = self.__listeningSocket.accept()
        data = connection.recv(1024)
        if data:
            message = cPickle.loads(data)
            self.logger.info("empfangen: " + message.printToString())
            self.process_received_message(message)

    @abstractmethod
    def process_received_message(self, data):
        pass

    def send_message_to_id(self, message, ID):
        try:
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receiver = self._ips_and_ports[str(ID)]
            sender.connect((receiver["ip"], receiver["port"]))
            sender.sendall(cPickle.dumps(message))
            self.logger.info("gesendet: " + message.printToString())
        except:
            self.logger.error('Error while sending message.', exc_info=1)



