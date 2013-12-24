from CodeBase.Message import Message
from CodeBase.AbstractGraphKnot import AbstractGraphKnot

__author__ = 'me'


class TokenForkKnot(AbstractGraphKnot):

    def __init__(self, ID, connections_filename, topology_filename):
        super(TokenForkKnot, self).__init__(ID, connections_filename, topology_filename)
        self.free = True
        self.owner = None
        self.ordered_by = -1

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.give_philosopher_a_fork()
            self.receive_messages()

    def process_received_message(self, connection, message):
        if message.getAction() == "token":
            # leite Nachricht weiter
            neighbourID = self.rightNeighbour
            self.send_message_to_id(message, neighbourID)
        elif message.getAction() == "orderFork":
            self.ordered_by = message.getSender()
        elif message.getAction() == "returnFork":
            self.setFree(message.getSender())

    def give_philosopher_a_fork(self):
        if self.ordered_by >= 0:
            philosopher_receives_fork_message = Message("receiveFork", "A fork for a philiospher.", sender=self._ID)
            self.send_message_to_id(philosopher_receives_fork_message, self.ordered_by)
            self.ordered_by = -1

    def setFree(self, requestComesFrom):
        if requestComesFrom == self.owner:
            self.free = True


