import time
import cPickle
from CodeBase.AbstractGraphKnot import AbstractGraphKnot
from CodeBase.Message import Message

__author__ = 'me'


class TokenPhilosopherKnot(AbstractGraphKnot):
    TIME_THINK_MAX = 4000
    TIME_EAT_MAX = 4000

    def __init__(self, ID, connections_filename, topology_filename):
        super(TokenPhilosopherKnot, self).__init__(ID, connections_filename, topology_filename)
        self.token = False
        self.has_left_fork = False
        self.has_right_fork = False


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
            self.returnForks()
            self.send_token_to_next_philosopher()

    def think(self):
        time_to_think = self._system_random.randint(0, TokenPhilosopherKnot.TIME_THINK_MAX) / 1000.0  # [s = ms / 1000]
        self.logger.info("I am thinking now for " + str(time_to_think) + " seconds.")
        time.sleep(time_to_think)

    def eat(self):
        time_to_eat = self._system_random.randint(0, TokenPhilosopherKnot.TIME_EAT_MAX) / 1000.0 # [s = ms / 1000]
        self.logger.info("I am eating now for " + str(time_to_eat) + " seconds.")
        time.sleep(time_to_eat)

    def process_received_message(self, connection, message):
        if message.getAction() == "token":
            self.token = True
        elif message.getAction() == "receiveFork":
            if message.getSender() == self.rightNeighbour:
                self.has_right_fork = True
            else:
                self.has_left_fork = True

    def send_token_to_next_philosopher(self):
        tokenMessage = Message("token", "Ready to eat?", sender=self._ID)
        neighbourID = self.rightNeighbour
        self.send_message_to_id(tokenMessage, neighbourID)
        self.token = False

    def order_left_fork(self):
        self.order_fork(self.leftNeighbour)

    def order_right_fork(self):
        self.order_fork(self.rightNeighbour)

    def order_fork(self, ID):
        order_fork_message = Message("orderFork", "Are you free?", sender=self._ID)
        self.send_message_to_id(order_fork_message, ID)

    def returnForks(self):
        returnForkMessage = Message("returnFork", "You are free now.", sender=self._ID)
        if self.send_message_to_id(returnForkMessage, self.leftNeighbour):
            self.has_left_fork = False
        if self.send_message_to_id(returnForkMessage, self.rightNeighbour):
            self.has_right_fork = False




