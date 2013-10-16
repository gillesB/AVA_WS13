import json
from pprint import pprint
import random
import socket

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
        '''
        init = True
        while True:
            message = self.receive_message()
            self.print_message(message)
            if init:
                self.send_ID_to_neighbours()
                init = False
                '''


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

        self.__listeningSocket = socket.socket()
        host = socket.gethostname()
        self.__listeningSocket.bind((host, self.__port))

    def choose_neighbours(self):
        for i in range(3):
            random_index = random.randint(0, len(self.__ips_and_ports)-1)
            key = self.__ips_and_ports.keys()[random_index]
            self.__neighbours[key] = self.__ips_and_ports[key]
            del self.__ips_and_ports[key]


