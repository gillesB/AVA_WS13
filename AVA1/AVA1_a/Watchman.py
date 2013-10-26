import cPickle
import logging
import socket
import json
import time
from AVA1.AVA1_a.Message import Message


__author__ = 'me'


class Watchman:
    def __init__(self, topology_filename):
        self.__ips_and_ports = {}
        self.__topology_filename = topology_filename
        self.read_input_file()
        self.__init_message = Message('init', 'Is this end of the beginning?', True)
        self.__kill_message = Message('suicide', 'Or the beginning of the end?', True)

        self.logger = logging.getLogger(__name__)


    def read_input_file(self):
        json_data = open(self.__topology_filename)
        self.__ips_and_ports = json.load(json_data)
        json_data.close()

    def send_message(self, ID, message):
        try:
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            suicidal = self.__ips_and_ports[str(ID)]
            sender.connect((suicidal["ip"], suicidal["port"]))
            sender.sendall(cPickle.dumps(message))
        except:
            self.logger.error('Error while sending message.', exc_info=1)

    def terminate_all(self):
        for localKnot_id in self.__ips_and_ports.keys():
            self.send_message(localKnot_id, self.__kill_message)

    def user_interface(self):
        while True:
            print 'You can: send init message (init <ID>); kill knot (kill <ID>); kill all knots (killAll)'
            user_input = raw_input('$ ').split(' ')
            command = user_input[0]
            if command == 'init' or command == 'i':
                self.send_message(user_input[1], self.__init_message)
            elif command == 'kill' or command == 'k':
                self.send_message(user_input[1], self.__kill_message)
            elif command == 'killAll' or command == 'ka':
                self.terminate_all()
            else:
                print 'command not known'
            time.sleep(0.5)


