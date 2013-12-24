import time
from AVA3.PhiloCodeBase.BasicPhilosopherKnot import BasicPhilosopherKnot
from CodeBase.Message import Message

__author__ = 'me'


class TokenPhilosopherKnot(BasicPhilosopherKnot):
    TIME_THINK_MAX = 4000
    TIME_EAT_MAX = 4000

    def __init__(self, ID, connections_filename, topology_filename):
        super(TokenPhilosopherKnot, self).__init__(ID, connections_filename, topology_filename)
        self.token = False

    def run(self):
        self.info()
        self.read_connections_file()
        self.open_port()
        self.choose_new_neighbours()
        while True:
            self.think()
            self.logger.info("I want to eat now. Waiting for the token.")
            while not self.token:
                self.receive_messages()
            self.logger.info("Received the token. Waiting for the left fork.")
            self.order_left_fork()
            while not self.has_left_fork:
                self.receive_messages()
            self.logger.info("I received the left fork.")
            self.logger.info("Waiting for the right fork.")
            self.order_right_fork()
            while not self.has_right_fork:
                self.receive_messages()
            self.logger.info("I received the right fork.")
            self.eat()
            self.return_forks()
            self.send_token_to_next_philosopher()

    def process_received_message(self, connection, message):
        super(TokenPhilosopherKnot, self).process_received_message(connection, message)
        if message.getAction() == "token":
            self.token = True

    def send_token_to_next_philosopher(self):
        token_message = Message("token", "Ready to eat?", sender=self._ID)
        neighbour_id = self.rightNeighbour
        self.send_message_to_id(token_message, neighbour_id)
        self.token = False




