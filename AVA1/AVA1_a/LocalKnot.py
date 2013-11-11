import random
import sys

from AVA1.AVA1_a.Message import Message
from CodeBase.AbstractKnot import AbstractKnot


__author__ = 'me'


class LocalKnot(AbstractKnot):

    def __init__(self, ID, connections_filename):
        super(LocalKnot, self).__init__(ID, connections_filename)
        self._neighbours = {}

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_neighbours()
        init = True
        while True:
            self.receive_message()
            if init:
                self.send_id_to_neighbours()
                init = False

    def choose_neighbours(self):
        for i in range(3):
            random_index = random.randint(0, len(self._ips_and_ports) - 1)
            ID = self._ips_and_ports.keys()[random_index]
            self.add_neighbour(ID)

    def add_neighbour(self, ID):
        self._neighbours[ID] = self._ips_and_ports[ID]

    def process_received_message(self, message):
        if message.getAction() == 'suicide':
            sys.exit(0)

    def send_id_to_neighbours(self):
        own_id_message = Message("ID", self._ID)
        for neighbourID in self._neighbours.keys():
            self.send_message_to_id(own_id_message, neighbourID)

if __name__ == '__main__':
    id = sys.argv[1]
    filename = sys.argv[2]
    localKnot = LocalKnot(id, filename)
    localKnot.run()



