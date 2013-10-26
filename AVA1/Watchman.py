import cPickle
import socket
import json

from Message import Message


__author__ = 'me'


class Watchman:
    def __init__(self, topology_filename):
        self.__ips_and_ports = ""
        self.__topology_filename = topology_filename
        self.read_input_file()


    def read_input_file(self):
        json_data = open(self.__topology_filename)
        self.__ips_and_ports = json.load(json_data)
        json_data.close()

    def send_init(self, ID):
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        initiator = self.__ips_and_ports[str(ID)]
        sender.connect((initiator["ip"], initiator["port"]))
        init_message = Message('init', 'Is this end of the beginning?', True)
        sender.sendall(cPickle.dumps(init_message))

    def user_interface(self):
        while (True):
            print 'You can: send init message (init <ID>); kill knot (kill <ID>); kill all knots (killAll)'
            input = raw_input('$ ').split(' ')
            command = input[0]
            if command == 'init' or command == 'i':
                self.send_init(input[1])
            elif command == 'kill' or command == 'k':
                pass
            elif command == 'killAll' or command == 'ka':
                pass
            else:
                print 'command not known'


