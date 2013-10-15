import json
from pprint import pprint

__author__ = 'me'

from multiprocessing import Process
import os


class LocalKnot(Process):
    def __init__(self, ID):
        super(LocalKnot, self).__init__()
        self.__ID = ID
        self.__ips_and_ports = None

    def run(self):
        self.info()
        self.read_input_file()
        '''
        self.open_port()
        self.choose_neighbours()
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
        print self.__ips_and_ports
        json_data.close()
