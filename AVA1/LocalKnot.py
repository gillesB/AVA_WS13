import json
import random
import socket
import cPickle
from Message import Message

__author__ = 'me'

from multiprocessing import Process
import os


class LocalKnot(Process):
    def __init__(self, ID):
        super(LocalKnot, self).__init__()
        self.__ID = str(ID)
        self.__ips_and_ports = None
        self.__ip = None
        self.__port = None
        self.__listeningSocket = None
        self.__neighbours = {}

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


    def info(self):
        print 'module name:', __name__
        if hasattr(os, 'getppid'):
            print 'parent process:', os.getppid()
        print 'process id:', os.getpid()
        print 'LocalKnot id:', self.__ID
        print

    def read_input_file(self):
        json_data = open('AVA1/json_data')
        self.__ips_and_ports = json.load(json_data)
        json_data.close()

    def open_port(self):
        self.__ip = self.__ips_and_ports[self.__ID]["ip"]
        self.__port = self.__ips_and_ports[self.__ID]["port"]
        del self.__ips_and_ports[self.__ID]

        self.__listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.__listeningSocket.bind((host, self.__port))
        self.__listeningSocket.listen(5)

    def choose_neighbours(self):
        for i in range(3):
            random_index = random.randint(0, len(self.__ips_and_ports) - 1)
            key = self.__ips_and_ports.keys()[random_index]
            self.__neighbours[key] = self.__ips_and_ports[key]
            del self.__ips_and_ports[key]

    def receive_message(self):
        connection, addr = self.__listeningSocket.accept()
        data = connection.recv(1024)
        if data:
            message = cPickle.loads(data)
            print "empfangen: " + message.printToString()

    def send_id_to_neighbours(self):
        for neighbour in self.__neighbours.values():
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = socket.gethostname()
            #sender.connect((neighbour["ip"], neighbour["port"]))
            sender.connect((host, neighbour["port"]))
            own_id_message = Message("ID", self.__ID)
            sender.sendall(cPickle.dumps(own_id_message))
            print "gesendet: " + own_id_message.printToString()



