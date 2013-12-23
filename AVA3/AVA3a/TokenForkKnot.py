from CodeBase.Message import Message
from CodeBase.AbstractGraphKnot import AbstractGraphKnot

__author__ = 'me'


class TokenForkKnot(AbstractGraphKnot):

    def __init__(self, ID, connections_filename, topology_filename):
        super(TokenForkKnot, self).__init__(ID, connections_filename, topology_filename)
        self.free = True
        self.owner = None

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.receive_messages()

    def process_received_message(self, connection, message):
        if message.getAction() == "token":
            tokenMessage = Message("token", "Ready to eat?", sender=self._ID)
            neighbourID = self.rightNeighbour
            self.send_message_to_id(tokenMessage, neighbourID)
        elif message.getAction() == "getFork":
            self.givePhilosopherAFork(connection, message.getSender())
        elif message.getAction() == "setFree":
            self.setFree(message.getSender())

    def givePhilosopherAFork(self,connection, requester):
        forkFreeMessage = Message("forkFree", self.free, sender=self._ID)
        success = self.send_message_over_socket(connection, forkFreeMessage)
        if self.free and success:
            self.free = False
            self.owner = requester

    def setFree(self, requestComesFrom):
        if requestComesFrom == self.owner:
            self.free = True


