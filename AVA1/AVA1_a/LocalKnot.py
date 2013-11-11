import random
import sys

from CodeBase.Message import Message
from CodeBase.AbstractKnot import AbstractKnot


__author__ = 'me'


class LocalKnot(AbstractKnot):

    def __init__(self, ID, connections_filename):
        super(LocalKnot, self).__init__(ID, connections_filename)

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours(3)
        init = True
        while True:
            self.receive_messages()
            if init:
                self.send_id_to_neighbours()
                init = False

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



